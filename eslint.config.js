export default [
  {
    files: ["static/**/*.js", "tests/js/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
        localStorage: "readonly",
        Intl: "readonly",
        alert: "readonly",
        fetch: "readonly",
        console: "readonly",
        Event: "readonly",
        Element: "readonly",
        HTMLElement: "readonly",
        SVGElement: "readonly",
        setTimeout: "readonly",
      },
    },
    rules: {
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
      "no-undef": "error",
      "eqeqeq": ["error", "always"],
    },
  },
];
