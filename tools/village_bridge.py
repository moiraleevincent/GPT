#!/usr/bin/env python3
"""Explicit, owner-controlled bridge from a GitHub Issue to AI Village Open Chat.

Inspired by the public interface documented at Minuteandone/Village-chat-tool.
Read/post commands are intentionally limited; no automatic conversation relay.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

VILLAGE_BASE = "https://theaidigest.org/village"
MAX_MESSAGE = 1200


def request_json(url, payload=None, method=None, token=None):
    if not (url.startswith(VILLAGE_BASE + "/api/") or
            url.startswith("https://api.github.com/repos/")):
        raise ValueError("Unexpected API host")
    headers = {"Accept": "application/json", "User-Agent": "MoiraVillageBridge/1.0"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    verb = method or ("POST" if body is not None else "GET")
    req = urllib.request.Request(url, data=body, headers=headers, method=verb)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            # Full event pages can be much larger than ordinary API responses.
            cap = 32_000_000 if "/api/events?" in url else 3_000_000
            raw = response.read(cap + 1)
            if len(raw) > cap:
                raise RuntimeError("API reply exceeded maximum size")
            return json.loads(raw or b"{}")
    except urllib.error.HTTPError as error:
        path = urllib.parse.urlsplit(url).path
        raise RuntimeError("API returned HTTP %d for %s" % (error.code, path)) from None


def github_safe(value):
    """Avoid accidental pings to GitHub users sharing Village agent names."""
    return re.sub(r"@(?![\u200b\u200c\u200d])", "@\u200b", str(value))


def restore_village_mentions(value):
    """[[at]]Name is safe inside the public GitHub issue command."""
    value = value.replace("[[at]]", "@")
    return re.sub(r"@[\u200b\u200c\u200d]+", "@", value)


def village_info():
    slug = os.environ.get("VILLAGE_SLUG", "open-chat") or "open-chat"
    url = VILLAGE_BASE + "/api/villages?" + urllib.parse.urlencode({"slug": slug})
    result = request_json(url)
    if not isinstance(result, dict) or not result.get("id"):
        raise RuntimeError("Village not found")
    return request_json(VILLAGE_BASE + "/api/villages/" +
                        urllib.parse.quote(str(result["id"]), safe=""))


def read_messages(info, count, room_filter):
    village_id = str(info["id"])
    base = VILLAGE_BASE + "/api/villages/" + urllib.parse.quote(village_id, safe="")
    dates = request_json(base + "/active-dates").get("dates", [])
    if not dates:
        return "No active Village days were found."
    date = max(dates)
    speakers = {str(a["id"]): a.get("name", "Agent")
                for a in info.get("agents", []) if a.get("id")}
    rooms = {str(r["id"]): r.get("name", "")
             for r in info.get("chatRooms", []) if r.get("id")}
    found = []
    complete = False
    for page in range(1, 101):
        params = urllib.parse.urlencode({"villageId": village_id, "date": date,
                                         "page": page})
        events = request_json(VILLAGE_BASE + "/api/events?" + params)
        if not isinstance(events, dict) or not isinstance(events.get("events"), list):
            raise RuntimeError("Unexpected event feed format")
        for event in events["events"]:
            data = event.get("data") or {}
            if not isinstance(data, dict) or data.get("actionType") not in ("AGENT_TALK", "USER_TALK"):
                continue
            message = data.get("content")
            if not isinstance(message, str) or not message.strip():
                continue
            room_id = str(data.get("roomId", ""))
            room_name = rooms.get(room_id, room_id)
            if room_filter.casefold() not in ("all", room_id.casefold(),
                                              room_name.casefold()):
                continue
            if data["actionType"] == "AGENT_TALK":
                speaker = speakers.get(str(data.get("speakerId")), "Agent")
            else:
                speaker = data.get("speakerName") or "Human"
            found.append((str(event.get("createdAt", "")),
                          int(event.get("eventIndex") or 0),
                          speaker, room_name, message.strip()))
        if not events.get("hasMore"):
            complete = True
            break
    found.sort(key=lambda item: (item[0], item[1]))
    lines = ["AI Village Open Chat — %s (%d matching messages)" % (date, len(found))]
    if not complete:
        lines.append("Partial results: page limit reached.")
    for timestamp, _, speaker, room_name, message in found[-count:]:
        lines.extend(["", "%s — %s — %s" % (speaker, room_name, timestamp),
                      message])
    return "\n".join(lines)[:60000]


def submit_message(info, room_name, message):
    visitor_id = os.getenv("VILLAGE_VISITOR_ID", "").strip()
    display_name = (os.getenv("VILLAGE_DISPLAY_NAME") or "Rook (external GPT-6)").strip()
    if not 20 <= len(visitor_id) <= 200:
        return "Not sent: configure a private VILLAGE_VISITOR_ID Actions secret (20–200 random characters)."
    if not 1 <= len(display_name) <= 50:
        return "Not sent: VILLAGE_DISPLAY_NAME must be between 1 and 50 characters."
    if not 1 <= len(message) <= MAX_MESSAGE:
        return "Not sent: message must contain 1–1200 characters."
    matches = [room for room in info.get("chatRooms", [])
               if room_name.casefold() in (str(room.get("name", "")).casefold(),
                                          str(room.get("id", "")).casefold())]
    if len(matches) != 1:
        return "Not sent: ambiguous or nonexistent Village chat room."
    identity = request_json(VILLAGE_BASE + "/api/users",
                            {"localStorageId": visitor_id})
    if not isinstance(identity, dict) or not identity.get("id"):
        raise RuntimeError("Village did not accept the guest identity")
    user_id = str(identity["id"])
    response = request_json(VILLAGE_BASE + "/api/users/display-name",
                            {"userId": user_id, "name": display_name,
                             "villageId": info["id"]}, method="PUT")
    if isinstance(response, dict) and response.get("error"):
        raise RuntimeError("Village rejected the display name")
    reply = request_json(VILLAGE_BASE + "/api/chat/messages",
                         {"villageId": info["id"], "roomId": matches[0]["id"],
                          "userSpeakerId": user_id,
                          "content": restore_village_mentions(message)})
    if isinstance(reply, dict) and reply.get("error"):
        raise RuntimeError("Village rejected the message")
    approval = reply.get("hasBeenApproved") if isinstance(reply, dict) else None
    if approval is None and isinstance(reply, dict):
        approval = (reply.get("message") or {}).get("hasBeenApproved")
    status = ("approval pending" if approval is False else
              "server marked approved (not independently checked)" if approval is True
              else "public visibility unverified")
    return "Village accepted one message submission from %s; %s." % (display_name, status)


def perform(command):
    parts = command.strip().split(maxsplit=3)
    if len(parts) < 2 or parts[0] != "/village":
        return "Unknown command."
    if parts[1] == "status":
        ready = 20 <= len(os.environ.get("VILLAGE_VISITOR_ID", "")) <= 200
        return ("Bridge ready for read commands; posting identity %s. "
                "This command did not post anything." % ("configured" if ready else "not configured"))
    if parts[1] == "read":
        try:
            count = int(parts[2]) if len(parts) > 2 else 10
        except ValueError:
            return "Read count must be an integer from 1 to 30."
        if not 1 <= count <= 30:
            return "Read count must be from 1 to 30."
        return read_messages(village_info(), count, parts[3] if len(parts) > 3 else "all")
    if parts[1] == "post" and len(parts) == 4:
        return submit_message(village_info(), parts[2], parts[3])
    return "Try /village status, /village read 10 general, or /village post general Hello!"


def main():
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as source:
        event = json.load(source)
    issue = event.get("issue") or {}
    comment = event.get("comment") or {}
    repository = os.environ["GITHUB_REPOSITORY"]
    owner = repository.split("/")[0].casefold()
    # Double-check user identity even though the Actions workflow also gates.
    if (issue.get("pull_request") or
            (issue.get("user") or {}).get("login", "").casefold() != owner or
            (comment.get("user") or {}).get("login", "").casefold() != owner):
        return
    command = comment.get("body", "")
    if not command.startswith("/village "):
        return
    try:
        result = perform(command)
    except Exception as error:
        result = "Bridge failed: %s" % error
    issue_number = int(issue["number"])
    destination = ("https://api.github.com/repos/" + repository +
                   "/issues/" + str(issue_number) + "/comments")
    request_json(destination, {"body": github_safe(result)[:65000]},
                 token=os.environ["GITHUB_TOKEN"])


if __name__ == "__main__":
    main()
