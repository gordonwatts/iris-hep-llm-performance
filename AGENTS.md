# Project instructions

## Data storage

- Resolve the bulk-data root from an explicit task-specific override, then
  `IRIS_HEP_DATA_DIR`, then `[data].root` in the ignored `data.local.toml`
  at the repository root. These are project storage conventions; pass the
  resolved path explicitly to tools that do not read this configuration.
- Keep machine-specific paths and disk characteristics in `data.local.toml`.
  A minimal configuration is `[data]` followed by `root = "/path/to/bulk-data"`.
  On a fresh checkout with no configured root, ask where bulk data should go
  before downloading large inputs. Verify the configured location exists and
  is accessible; do not silently fall back to the source checkout.
- Store downloaded input files, ROOT ntuples, ServiceX deliveries and bulk
  data caches, large intermediate outputs, and full run logs/reports under
  that root. Use named analysis/run subdirectories, such as `calratio/<run-id>/`,
  and record input/output provenance.
- Bulk storage may be a high-capacity spinning disk, suitable for ntuples and
  sequential I/O. Keep source checkouts, Python environments, package caches,
  builds, and latency-sensitive scratch work on a faster local disk when
  available, unless a task requires otherwise.
- Keep runnable scripts, small sample/provenance manifests, compact evidence
  tables, concise status notes, and selected small review plots in the repository.
  Reference bulk artifacts from those manifests instead of committing them.
- Make new extraction/analysis scripts accept a configurable data root so the
  workflow remains usable on other hosts. Document the resolved data location
  in run metadata.
- For WSL execution, translate a configured Windows data root to its actual
  WSL mount path and verify that it refers to the same directory before use.
