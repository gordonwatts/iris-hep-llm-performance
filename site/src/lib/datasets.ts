/**
 * A rucio dataset identifier as it appears in question text: a scope, a
 * colon, and a dotted/underscored dataset name — e.g.
 * "user.zmarshal:user.zmarshal.364702_OpenData_v1_p6026_2024-04-23" or
 * "opendata:mc20_13TeV.700325...p6026". Requires a letter in the scope so a
 * URL's "https:" is never mistaken for one.
 */
const DATASET_PATTERN = /\b[A-Za-z][A-Za-z0-9_.]*:[A-Za-z0-9][A-Za-z0-9_.-]*/g;

/**
 * Pulls rucio dataset identifiers out of a question's free-text prompt, for
 * rendering as chips on the question page. Best-effort: a pattern this
 * general can't distinguish a dataset from some other colon-separated
 * token, but every dataset in the current specs matches it and nothing else
 * does.
 */
export function extractDatasets(text: string): string[] {
  const matches = text.match(DATASET_PATTERN) ?? [];
  return matches
    .filter((match) => !/^https?:/i.test(match))
    .map((match) => match.replace(/[.,;:]+$/, ""));
}
