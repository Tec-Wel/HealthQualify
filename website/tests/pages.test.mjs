import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('../', import.meta.url);
const read = file => readFileSync(new URL(file, root), 'utf8');

test('all marketing pages and layout exist', () => {
  for (const name of ['index','agents/index','qualification/index','local-edition/index','community/index','demo/index','architecture/index','showcase/index']) {
    assert.ok(existsSync(new URL('src/pages/' + name + '.astro', root)), name);
  }
  assert.match(read('src/layouts/BaseLayout.astro'), /docs\//);
});
test('site contains explicit alpha and privacy limits', () => {
  const layout = read('src/layouts/BaseLayout.astro');
  assert.match(layout, /No PHI/);
  assert.match(layout, /Not FDA/);
  assert.match(read('src/pages/index.astro'), /No mandatory paid API/);
  assert.match(read('src/pages/demo/index.astro'), /STATIC ILLUSTRATION/);
  assert.match(read('src/pages/architecture/index.astro'), /No automatic approval|never a qualification/);
});
test('no mandatory paid services, external trackers or remote fonts', () => {
  const files = ['src/layouts/BaseLayout.astro','src/styles/site.css','astro.config.mjs','package.json'];
  for (const file of files) {
    assert.doesNotMatch(read(file), /google-analytics\.com|googletagmanager\.com|fonts\.googleapis\.com|segment\.io|stripe\.com/i);
  }
});
