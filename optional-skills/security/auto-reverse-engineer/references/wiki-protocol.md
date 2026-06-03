# Wiki Protocol

`wiki/` is durable understanding; `artifacts/` is immutable evidence. Every fact
cites `artifacts/` or `derived/`.

```text
index.md       map/start here
log.md         append-only ingest/query/lint log
facts.md       cited claims
hypotheses.md  unproven claims
disproved.md   rejected claims
entities/      functions/endpoints/keys/components/packet types
concepts/      auth/frame/boot-chain abstractions
sources/       one page per artifact
```

Page frontmatter: `tags`, `sources`, `confidence`, `updated`. Body: one-line
definition, facts with `[[sources/<slug>]]`, open questions, related links.

Ops:

- Ingest: create source page, update entities/concepts, move claims among
  facts/hypotheses/disproved, refresh index, log it.
- Query: read index, drill down, write new synthesis back, log it.
- Lint every ~10 iterations: contradictions, stale claims, orphans, broken
  links, missing concepts, uncited facts.

No citation means hypothesis. Overturned facts move to `disproved.md`.
Confidence follows evidence.
