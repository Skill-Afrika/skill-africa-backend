// eslint.config.ts
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import prettier from 'eslint-plugin-prettier';

const config = [
  {
    files: ['**/*.ts', '**/*.tsx'],

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
