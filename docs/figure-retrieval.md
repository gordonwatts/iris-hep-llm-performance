# Internal-note figure retrieval benchmarks

The existing `atlas-metadata-queries.yaml` suite has two figure cases:

| Case | Requested source | Requested figures |
| --- | --- | --- |
| `q7-hdbs-internal-figures` | `ANA-HDBS-2019-03-INT1` | 1 and 2, with a separately verified caption for each |
| `q8-archived-calratio-figure` | `ANA-EXOT-2019-23-INT1` | 1, matched against the archived reference |

The modern case has one user-supplied caption hint. Its mapping to figure 1,
figure 2, or both must be established from source evidence. No mapping is assumed.
The older target was identified from the title page and figure caption in the
existing CalRatio 2019 archive, dated 2 August 2021, on PDF page 8. Its reference
PDF hash and caption-hint hashes are in `spec/figure-retrieval-cases.json`.
The earlier low-EMF calibration note and public Run 1 paper are not substituted.

Protected captions, archived PDFs, figure payloads, full MCP responses, model
traces and reports stay in the configured private bulk-data root. They must not
be committed, included in public PR descriptions, or sent to a contact. Public
unit tests use synthetic pictures and captions. The source IDs and hashes here
are references, not permission to disclose the protected documents.

## Private input and launcher

Prepare a private JSON file under the bulk root with a `cases` object keyed by
the two case IDs. Each target contains `note_id`, `figure_numbers`, `caption_hint`
and `expected_captions`. The older target's `expected_captions` maps `"1"` to the
exact verified archived caption. The modern mapping starts empty until verified.
Do not put this private fixture in the source checkout. The catalogue pins each
caption hint by SHA-256 of whitespace-normalized, case-folded UTF-8 text.

Use the project launcher so the independent payload validator is registered.
The generic runner rejects the project validator if it has not been registered;
a text-only answer cannot silently satisfy these cases.

```powershell
# Prepare only; creates a new named run and never overwrites an existing run.
uv run --script scripts/figure_retrieval.py run q7-hdbs-internal-figures `
  --private-fixture D:/private-data/figure-targets.json `
  --data-root D:/private-data --run-name modern-001
```

Repeat with `q8-archived-calratio-figure`. The root is resolved from
`--data-root`, `IRIS_HEP_DATA_DIR`, then ignored repository `data.local.toml`.
The launcher stages only the selected private search target and this public
contract. It does not seed an archived PDF or figure. Reports and retained
workspaces go under `<data-root>/figure-retrieval/<run-name>/`.

With working MCP access, execute through the existing pinned benchmark runner:

```powershell
uv run --with "git+https://github.com/gordonwatts/test-wsl2-llm.git@608d04c9c35083ee9df13e41513acd9d6cbd190b" `
  --script scripts/figure_retrieval.py run q7-hdbs-internal-figures `
  --private-fixture D:/private-data/figure-targets.json `
  --data-root D:/private-data --run-name modern-live-001 --execute
```

The launcher verifies the staged input hash through the actual WSL mount before
launching. Existing MCP configuration and linked identities are used in place;
this workflow does not log in, reconfigure credentials, or provide a browser
fallback. If the required connection fails, stop affected work and retain its
stage/error. A blocked live attempt is a useful **failed retrieval**, never a pass.

## Retained evidence contract

Write `retrieval-evidence.json` in the retained workspace:

```json
{
  "schema_version": 1,
  "case_id": "q7-hdbs-internal-figures",
  "requests": [
    {
      "id": "payload-1",
      "tool": "mcp__atlas_af__ACTUAL_TOOL_NAME",
      "stage": "payload",
      "status": "succeeded",
      "query": {"actual_arguments": "private retained request"},
      "result_record": "retained raw MCP result locator"
    }
  ],
  "figures": [
    {
      "number": 1,
      "note_id": "ANA-HDBS-2019-03-INT1",
      "status": "retrieved",
      "caption": "<actual private source caption>",
      "mapping_verified": true,
      "source_version": "<actual document revision or source-document SHA-256>",
      "mapping_receipt": {"path": "mapping-1.json", "sha256": "<sha256>"},
      "retrieval_request_id": "payload-1",
      "payload": {
        "path": "figure-1.png",
        "sha256": "<sha256>",
        "bytes": 12345,
        "media_type": "image/png",
        "route": "mcp_figure",
        "source_locator": "https://example.invalid/canonical-path-without-signed-query"
      }
    }
  ]
}
```

This abbreviated example shows one row; the modern case requires **both** rows.
A mapping receipt is retained JSON containing `note_id`, `figure_number`, the
actual `caption`, matching `source_version` and a `source_record` identifying its raw service evidence.
Record document version and returned figure indexing alongside these fields.
Retain raw MCP responses privately so an independent reviewer can establish that
the mapping and payload calls really occurred. Never manufacture receipts.
Use exact actual tool names and request arguments, not the example placeholders.
Remove credentials and signed query values before writing evidence.

Supported payloads are decoded PNG/JPEG or a single-page PDF with graphics.
When the route is `mcp_pdf_crop`, also include `payload.crop` with `source_pdf`
(a retained `{path, sha256}` record), one-based `page`, and `bbox` in PDF points
`[x0, y0, x1, y1]`. Record the verified figure mapping before extraction. A whole
note, whole-page substitute, uniform placeholder or mislabeled HTML is rejected.
An offline archive extraction may establish the reference, but its route is
`archive_reference` and it cannot pass a live MCP retrieval case.

Every requested figure gets a row even after a failure. Use `blocked_access`,
`not_indexed`, `metadata_only`, `caption_unverified`, or `payload_error` for
unresolved results; set missing captions/receipts/payloads to null and retain the
precise failure category, endpoint/tool path, request and error. Do not call a
figure absent from the index when authentication prevented searching it.

Validate a retained result without running a model:

```powershell
uv run --script scripts/figure_retrieval.py validate D:/private-data/retained-workspace `
  D:/private-data/figure-targets.json q7-hdbs-internal-figures
```

The validator checks per-figure completeness, note/caption/receipt consistency,
actual local hashes/byte counts, supported decodable content, path containment,
distinct figure payloads and successful MCP payload-request provenance. These
checks do not authenticate a model-written ledger: separately inspect its raw
MCP trace and source mapping. A metadata hit or caption without an accessible
payload remains a failed retrieval.

## Initial access checkpoint

The November 13 gateway inventory reported OpenSearch `link_required` with a
rejected linked credential. No live figure search or payload call was made and
no browser fallback was used. The older figure's local reference was verified;
modern caption/index mapping remains unverified. All three requested live figure
outcomes remain access-blocked. This checkpoint is not a successful model run.
Full queries, protected captions, reference crop and failed checks are retained
under the private bulk root. Rerun after the user restores linked access.
