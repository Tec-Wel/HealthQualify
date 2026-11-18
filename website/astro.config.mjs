import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://healthqualify.live',
  base: '/',
  output: 'static',
  build: { format: 'directory' },
});
