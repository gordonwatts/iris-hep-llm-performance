export interface ModelSelector {
  name: string;
  effort: string | null;
}

/**
 * Parses a `MODEL[:EFFORT]` selector, matching test-wsl2-llm's own
 * `model`/`models` field format (e.g. "gpt-5.6-luna:medium").
 */
export function parseModelSelector(selector: string): ModelSelector {
  const colonIndex = selector.indexOf(":");
  if (colonIndex === -1) {
    return { name: selector, effort: null };
  }

  return {
    name: selector.slice(0, colonIndex),
    effort: selector.slice(colonIndex + 1),
  };
}
