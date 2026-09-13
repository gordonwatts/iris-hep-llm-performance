/**
 * `{{ field }}` placeholder, matching test-wsl2-llm's strict-placeholder
 * template contract — internal whitespace around the field name is
 * tolerated (`{{question}}` and `{{ question }}` are equivalent).
 */
const PLACEHOLDER_PATTERN = /\{\{\s*([^{}\s]+)\s*\}\}/g;

/**
 * Renders a `prompt_template` against a question's fields.
 *
 * Throws on any placeholder without a matching field rather than shipping a
 * literal `{{ field }}` to the page — an unresolved placeholder means the
 * template and the question's fields have drifted, and that should fail
 * loudly at build time, not render as mojibake on a live page.
 */
export function renderPrompt(
  template: string,
  fields: Record<string, unknown>,
): string {
  return template.replace(PLACEHOLDER_PATTERN, (_match, field: string) => {
    if (!(field in fields)) {
      throw new Error(
        `renderPrompt(): template references "{{ ${field} }}" but no such field was provided.`,
      );
    }
    return String(fields[field]);
  });
}
