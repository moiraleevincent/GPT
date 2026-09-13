# Signal Garden

A small, dependency-free lexical motif explorer that runs entirely in the browser.

## What it does

Paste two corpora into **A** and **B** and Signal Garden will:

- compare 1-, 2-, or 3-word motifs;
- normalize frequencies per 10,000 words;
- rank terms by how strongly they drift toward one corpus;
- show the raw counts, normalized difference, and frequency ratio;
- reveal context snippets for any selected motif;
- build a simple "motif trail" of words that tend to occur nearby.

## Privacy

Signal Garden makes **no network requests**. Text is analyzed in JavaScript in the current browser tab. It is not uploaded, stored, or included in this repository. Reloading the page discards the pasted text.

That makes the tool suitable for exploring text you are permitted to analyze but not redistribute. You are still responsible for the terms that govern your own source material.

## Run it

Open `index.html` in a browser. No install, build step, server, API key, or model is required.

## Why this exists

Frequency by itself is rarely the interesting part of a lexical pattern. Comparison is. A word becomes more informative when you can ask: *Where is it unusually common? What surrounds it? What changes when the comparison set changes?*

Signal Garden is deliberately small. It is meant to help find places worth reading closely, not replace the reading.
