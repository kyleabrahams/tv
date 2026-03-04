export default [
  // Global ignores
  {
    ignores: [
      '**/urllib3/**',
      '._*',
      '**/._*',
      'node_modules/**',
    ],
  },

  // Lint JS files
  {
    files: ['**/*.js', '**/*.mjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      // your existing rules go here
    },
  },
];