export interface TruncatedText {
  excerpt: string;
  truncated: boolean;
}

/**
 * Truncates free-text (a question's prompt, which can run to a couple
 * thousand characters for a multi-stage task) to `maxLength` at a word
 * boundary, for use in a table row where the full text belongs on the
 * question's own detail page instead. Internal newlines collapse to spaces
 * first, since a multi-paragraph question would otherwise blow out a
 * table row's height even before truncation kicks in.
 */
export function truncateText(text: string, maxLength: number): TruncatedText {
  const collapsed = text.replace(/\s+/g, " ").trim();

  if (collapsed.length <= maxLength) {
    return { excerpt: collapsed, truncated: false };
  }

  const cut = collapsed.slice(0, maxLength);
  const lastSpace = cut.lastIndexOf(" ");
  const wordBoundary = lastSpace > 0 ? cut.slice(0, lastSpace) : cut;

  return { excerpt: `${wordBoundary.trimEnd()}…`, truncated: true };
}
