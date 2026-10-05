# Tripo API adapter (initial integration)

`tripo_client.py` connects the explicit Tripo v3 provider route to autoTA's
existing asset-contract and DCC/engine verification workflow. This does not
replace or weaken any autoTA gate. The stock hosted-generation skill's Meshy
and Tencent routes remain unchanged.

Credentials are read from a user-specified file and sent only to the fixed
official API origin. Authenticated redirects are rejected. Never commit a key
or include one in a JSON payload. Output directories contain operation receipts,
not credentials. Output task URLs may be signed; keep them local.

## Workflow

1. Create the per-asset contract outside this repository. Record user payment,
   upload, output-root, and target-project authorization.
2. `python scripts/tripo_client.py --key-file <file> --output <run-dir> balance`
3. Read current official docs and prepare a request JSON. P2 quad generation
   currently uses `model: P2-20260801`, `quad: true`, `face_limit`, `texture`,
   `pbr`, and `export_uv`. Do not treat `export_uv` as proof of Smart UV.
4. `python scripts/tripo_client.py --key-file <file> --output <fresh-stage-dir> submit --operation generate --payload <json>`
5. `python scripts/tripo_client.py --key-file <file> --output <stage-dir> query --task-id <id>`
6. On success, download the returned artifacts, preserve hashes, then invoke
   autoTA's source audit, visual inspection, repair, clean import comparison,
   target-engine validation and receipt validator. Download/extraction and DCC
   orchestration are not yet implemented in this adapter.

The adapter refuses duplicate submission directories. A POST is never retried
automatically: an interrupted request can already have created a paid task.
Inspect account task history before deciding whether a new submit is safe.

Zero credit balance blocks generation. Tripo freezes credits on task creation,
deducts on success, and returns frozen credits on failure/cancellation.

## Evidence status

Read-only authentication/balance, one paid P2 text-to-model generation, and
queued/running/success task queries were exercised on 2026-10-04. The returned
FBX contained four 2048 PBR maps. The request's quad/face settings were not
hard guarantees: independent Blender inspection found triangles and open
boundaries. Always audit the actual geometry rather than the submitted flags.
Texture/convert submissions remain untested. Download/extraction and DCC/Unity
orchestration still require the surrounding asset job; this file does not
claim automatic end-to-end validation.

The surrounding asset job also exercised local quad reconstruction, PBR baking,
source/clean-FBX audits, strict geometry/UV comparison, and Unity URP material,
prefab, scene reload and render checks. The textured delivery remains `prototype`
under the current receipt validator's restricted full-material profile. A passing
geometry comparison or receipt structure is not a full PBR validation claim.

Three offline safety tests cover duplicate submissions, ambiguous POST failure,
and empty balance. Run `python -m unittest discover -s scripts -p test_tripo_client.py`.

Official documentation checked 2026-10-04:

- Developer portal and API pricing: https://developers.tripo3d.ai/en/pricing
- API credential management: https://developers.tripo3d.ai/en/keys
- https://developers.tripo3d.ai/en/docs/billing
- https://developers.tripo3d.ai/en/docs/generation-text-to-model/p
- https://developers.tripo3d.ai/en/docs/task-query
- https://developers.tripo3d.ai/en/docs/models-texture

The inspected API documents do not establish a callable Smart UV endpoint.
Recheck its availability before each new pipeline version.
