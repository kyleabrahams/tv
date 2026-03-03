/** @type {import('eslint').Linter.Config} */
module.exports = {
  // ESLint configuration
  ignores: [
    '**/urllib3/**',      // keep your existing ignore
    '**/._*',             // ignore all macOS hidden temp files
    'node_modules/**',    // always ignore node_modules
    '**/*.min.js',        // optional: ignore minified files
  ],
};