# Signal Garden

A small, dependency-free lexical motif explorer that runs entirely in the browser.

## What it does

Paste two corpora into **A** and **B**, or load local text files, and Signal Garden will:

- compare 1-, 2-, or 3-word motifs;
- normalize frequencies per 10,000 words;
- rank terms by how strongly they drift toward one corpus;
- show the raw counts, normalized difference, and frequency ratio;
- reveal context snippets for any selected motif;
- build a simple "motif trail" of words that tend to occur nearby;
- swap the A/B comparison without reloading the source material.

Accepted local-file types include plain text, Markdown, CSV/TSV, JSON and JSONL. Files are read by the browser as text; they are not uploaded.

## Privacy

Signal Garden makes **no network requests**. Text is analyzed in JavaScript in the current browser tab. It is not uploaded, stored, or included in this repository. Reloading the page discards the pasted or loaded text.

That makes the tool suitable for exploring text you are permitted to analyze but not redistribute. You are still responsible for the terms that govern your own source material.

## Run it

Open `index.html` in a browser. No install, build step, server, API key, or model is required.

On desktop, downloading `index.html` and double-clicking it is enough. On iPad, save the file locally and open it with a browser-capable app; once GitHub Pages is enabled for the repository, the same file can instead be used from a normal web URL.

Inside Signal Garden, **Load local file → A/B** opens the device file picker. `Ctrl + Enter` or `⌘ + Enter` runs the analysis.

## Why this exists

Frequency by itself is rarely the interesting part of a lexical pattern. Comparison is. A word becomes more informative when you can ask: *Where is it unusually common? What surrounds it? What changes when the comparison set changes?*

Signal Garden is deliberately small. It is meant to help find places worth reading closely, not replace the reading.
