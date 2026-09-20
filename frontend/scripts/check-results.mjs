import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

// The saved appearance is applied before React paints, with a safe white default.
const themeScript = readFileSync(new URL('../index.html', import.meta.url), 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
for (const saved of [null, 'light', 'dark', 'invalid', 'blocked']) {
  const meta = { content: '#f5f5f7' };
  const document = { documentElement: { dataset: {} }, querySelector: () => meta };
  runInNewContext(themeScript, { document, localStorage: { getItem() {
    if (saved === 'blocked') throw new Error('Storage disabled');
    return saved;
  } } });
  assert.equal(document.documentElement.dataset.theme, saved === 'dark' ? 'dark' : undefined);
  assert.equal(meta.content, saved === 'dark' ? '#080809' : '#f5f5f7');
}
console.log('5 appearance initialization checks passed.');

// Render real result components against API response states without model downloads.
const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
try {
  const { default: AnalysisResult } = await server.ssrLoadModule('/src/components/AnalysisResult.jsx');
  const record = { overall_status: 'REVIEW', scores: null, matches: [], checks_complete: {}, warnings: [] };
  const render = (overrides, mode = 'combined') => renderToStaticMarkup(React.createElement(AnalysisResult, { record: { ...record, ...overrides }, mode }));

  const unavailable = render({});
  assert.match(unavailable, /Safe confidence: not evaluated/);
  assert.match(unavailable, /Similarity search could not be completed/);
  assert.doesNotMatch(unavailable, /No matching records found/);
  assert.match(unavailable, /Text extraction is incomplete or unavailable/);

  const noText = render({ checks_complete: { ocr: true } }, 'nsfw');
  assert.match(noText, /OCR completed. No embedded text was detected/);
  assert.match(noText, /badge safe/);
  assert.doesNotMatch(noText, /Visual Matches/);

  const similarity = render({ overall_status: 'SAFE', similarity_score: 0, checks_complete: { similarity: true }, ai_explanation: 'No stored items met the comparison threshold.' }, 'similarity');
  assert.match(similarity, /Context &amp; Explanation/);
  assert.match(similarity, /No stored items met the comparison threshold/);
  assert.match(similarity, /No matching records found/);
  assert.match(similarity, /Closest match: 0.0 percent/);
  assert.doesNotMatch(similarity, /No risk flagged|Embedded Text|Safe confidence/);

  const matched = render({ matches: [{ record_id: 'previous-record', file_name: 'reference.png', similarity_score: 89 }] }, 'similarity');
  assert.match(matched, /reference.png/);
  assert.match(matched, /89.0% similarity/);
  assert.doesNotMatch(matched, /NaN/);

  const flagged = render({ text_flagged: true, extracted_text: '<script>untrusted</script>', text_flag_reason: 'Phrase needs review.' }, 'nsfw');
  assert.match(flagged, /badge flagged/);
  assert.match(flagged, /&lt;script&gt;untrusted&lt;\/script&gt;/);
  assert.doesNotMatch(flagged, /<script>/);
  console.log('5 result-display checks passed.');
} finally {
  await server.close();
}
