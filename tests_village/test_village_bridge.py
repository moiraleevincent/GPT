"""Offline checks for the owner-only AI Village bridge."""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import village_bridge as bridge


class VillageBridgeTests(unittest.TestCase):
    def test_escape_github_mentions(self):
        text = bridge.github_safe("@SomeAgent says hello to @another")
        self.assertNotIn("@SomeAgent", text)
        self.assertEqual(bridge.github_safe(text), text)
        self.assertIn("@\u200bSomeAgent", text)

    def test_village_mention_restore(self):
        self.assertEqual(bridge.restore_village_mentions("[[at]]SomeAgent hi"),
                         "@SomeAgent hi")

    def test_status_does_not_call_village(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(bridge, "request_json") as call:
                answer = bridge.perform("/village status")
        self.assertIn("not configured", answer)
        call.assert_not_called()

    def test_read_count_is_bounded(self):
        with patch.object(bridge, "village_info") as call:
            self.assertIn("from 1 to 30", bridge.perform("/village read 31 all"))
            call.assert_not_called()

    def test_cannot_post_without_identity(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(bridge, "request_json") as call:
                answer = bridge.submit_message({"chatRooms": []}, "general", "hello")
        self.assertIn("Not sent", answer)
        call.assert_not_called()

    def test_cannot_post_to_unknown_room(self):
        with patch.dict(os.environ, {"VILLAGE_VISITOR_ID": "random-id-longer-than-twenty"}, clear=True):
            with patch.object(bridge, "request_json") as call:
                answer = bridge.submit_message({"chatRooms": []}, "general", "hello")
        self.assertIn("Not sent", answer)
        call.assert_not_called()

    def test_submit_uses_guest_api_and_preserves_mentions(self):
        village = {"id": "abc", "chatRooms": [{"id": "room1", "name": "general"}]}
        environment = {"VILLAGE_VISITOR_ID": "random-id-longer-than-twenty",
                       "VILLAGE_DISPLAY_NAME": "Rook (external GPT-6)"}
        with patch.dict(os.environ, environment, clear=True):
            with patch.object(bridge, "request_json",
                              side_effect=[{"id": "guest1"}, {}, {"hasBeenApproved": False}]) as calls:
                answer = bridge.submit_message(village, "general", "[[at]]Opus hi")
        self.assertIn("approval pending", answer)
        self.assertEqual(calls.call_count, 3)
        self.assertEqual(calls.call_args_list[-1].args[1]["content"], "@Opus hi")

    def test_non_owner_comment_is_ignored(self):
        event = {"issue": {"number": 1, "user": {"login": "moiraleevincent"}},
                 "comment": {"user": {"login": "somebodyelse"},
                             "body": "/village post general malicious"}}
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "moiraleevincent/GPT",
                                     "GITHUB_EVENT_PATH": "event.json"}, clear=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(event))):
                with patch.object(bridge, "request_json") as call:
                    bridge.main()
        call.assert_not_called()

    def test_owner_request_reply_is_github_safe(self):
        event = {"issue": {"number": 1, "user": {"login": "moiraleevincent"}},
                 "comment": {"user": {"login": "moiraleevincent"},
                             "body": "/village read 1 general"}}
        environment = {"GITHUB_REPOSITORY": "moiraleevincent/GPT",
                       "GITHUB_EVENT_PATH": "event.json", "GITHUB_TOKEN": "test"}
        with patch.dict(os.environ, environment, clear=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(event))):
                with patch.object(bridge, "perform", return_value="@Someone says hi"):
                    with patch.object(bridge, "request_json") as api:
                        bridge.main()
        self.assertEqual(api.call_args.args[1]["body"], "@\u200bSomeone says hi")


if __name__ == "__main__":
    unittest.main()
