import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://tec-wel.github.io',
  base: '/HealthQualify/',
  output: 'static',
  build: { format: 'directory' },
});
