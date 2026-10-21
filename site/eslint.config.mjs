import { defineConfig } from "eslint/config";
import { includeIgnoreFile } from "@eslint/compat";
import { fileURLToPath } from "node:url";
import eslintPluginAstro from "eslint-plugin-astro";

const gitignorePath = fileURLToPath(new URL(".gitignore", import.meta.url));

export default defineConfig([
  {
    ignores: ["public/**"],
  },
  includeIgnoreFile(gitignorePath),

  ...eslintPluginAstro.configs.recommended,

  {
    rules: {
      "no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" },
      ],
    },
  },
]);
