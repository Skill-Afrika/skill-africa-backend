// eslint.config.ts
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import prettier from 'eslint-plugin-prettier';

const config = [
  // Use the flat config `ignores` property instead of a standalone .eslintignore file.
  // This prevents the deprecation warning and keeps ESLint from traversing build/ and other generated folders.
  {
    ignores: ['build/**', 'node_modules/**', 'coverage/**', '.env', '.vscode/**', '.DS_Store']
  },
  {
    files: ['src/**/*.ts', 'src/**/*.tsx'],

    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2018,
        sourceType: 'module'
      }
    },

    plugins: {
      '@typescript-eslint': tseslint,
      prettier
    },

    rules: {
      ...tseslint.configs.recommended.rules,
      'prettier/prettier': 'error',
      '@typescript-eslint/no-explicit-any': 'off'
    }
  }
];

export default config;
