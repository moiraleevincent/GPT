# Motif Terrarium

A tiny, dependency-free lexical motif explorer that runs entirely in the browser.

Paste a transcript or chunk of prose, give it a watchlist of words, and it will show:

- exact motif counts
- distribution across the text
- motif co-occurrence within a ±12-token window
- concordance snippets for every hit
- a compact field note you can copy into research notes

Nothing is uploaded anywhere. Open `index.html` and it works.

## Why this exists

Frequency alone can hide the interesting part of a lexical pattern. A word can be rare but arrive at the same kind of moment, repeatedly appear next to another motif, or become conspicuous by disappearing. Motif Terrarium is meant as a fast first-pass retrieval aid before deeper qualitative analysis.

It is deliberately simple: exact words, transparent counts, no model calls, no statistics pretending to be stronger than they are.
