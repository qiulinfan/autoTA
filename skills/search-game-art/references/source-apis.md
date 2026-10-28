# Programmatic source APIs

Machine-readable routes for discovery and authorized acquisition. Uniform licensing can
simplify acquisition; it does not replace visual/technical selection or actual-file auditing.
Sources with per-item licenses still need the main Skill's candidate-level audit.

## Poly Haven (CC0 — textures, models, HDRIs)

Uniformly CC0, so programmatic acquisition is safe once provenance is
recorded and the actual files pass the applicable audit. Public JSON API, no auth key:

- Official access documentation: `https://polyhaven.com/our-api`.

- `https://api.polyhaven.com/assets?type=textures|models|hdris` — full
  catalog; filter locally by id keywords (e.g. `plaster`, `worn`, `damaged`).
- `https://api.polyhaven.com/info/<id>` — asset name and `authors` for the
  provenance record.
- `https://api.polyhaven.com/files/<id>` — per-map, per-resolution download
  URLs on `dl.polyhaven.org`, with per-file metadata for local integrity checks.

Practical notes:

- **Send a descriptive `User-Agent` header identifying the client**, as in the official docs;
  do not impersonate another browser. Fetch the catalog once per task, filter keywords/tags
  locally and fetch file metadata only for serious candidates. Respect rate limits and
  `Retry-After`; bounded retries with backoff are for transient errors, not authentication
  failures or CAPTCHA challenges. Report persistent failures and continue other sources.
- Useful map set for engine PBR materials: `Diffuse`, `nor_gl` (OpenGL-Y
  normal, what Godot expects), `Rough`, `AO`; 1k–2k JPEG is usually enough
  for prototype-grade surfaces.
- Record creator, source page (`https://polyhaven.com/a/<id>`), license + license page,
  resolution and imported filenames in the target project's notices. Keep computed hashes
  and raw API/run records in local ignored output when the project excludes them from Git.

## Other official catalogs

ambientCG documents search and download APIs at `https://docs.ambientcg.com/api/`.
Read its current endpoint and rate/access documentation before use; this reference does not
claim a tested ambientCG adapter. Use API results for discovery, then inspect original asset
pages and the actual selected files. Do not limit a search to API-accessible sources when
other source classes are needed for the brief's characters, animation or visual quality.

## Non-uniform sources

Sketchfab, itch.io, OpenGameArt, asset stores: license varies per item —
never automate acquisition there; follow the standard selection → per-item
license verification → audited acquisition flow in the main Skill.
