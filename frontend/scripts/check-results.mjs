import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

// Render real result components against API response states without model downloads.
const server = await createServer({ server: { middlewareMode: true }, appType: 'custom' });
try {
  const { default: AnalysisResult } = await server.ssrLoadModule('/src/components/AnalysisResult.jsx');
  const record = { overall_status: 'REVIEW', scores: null, matches: [], checks_complete: {}, warnings: [] };
  const render = (overrides, mode = 'combined') => renderToStaticMarkup(React.createElement(AnalysisResult, { record: { ...record, ...overrides }, mode }));

  const unavailable = render({});
  assert.match(unavailable, /Safe confidence: not evaluated/);
  assert.match(unavailable, /Similarity could not be assessed/);
  assert.doesNotMatch(unavailable, /No matching records found/);
  assert.match(unavailable, /Text extraction is incomplete or unavailable/);

  const noText = render({ checks_complete: { ocr: true } }, 'nsfw');
  assert.match(noText, /OCR completed. No embedded text was detected/);
  assert.match(noText, /badge safe/);
  assert.doesNotMatch(noText, /Visual matches/);

  const similarity = render({ overall_status: 'SAFE', similarity_score: 0, checks_complete: { similarity: true }, ai_explanation: 'No stored items met the comparison threshold.' }, 'similarity');
  assert.match(similarity, /Context &amp; explanation/);
  assert.match(similarity, /No stored items met the comparison threshold/);
  assert.match(similarity, /No matching records found/);
  assert.match(similarity, /Closest match: 0.0 percent/);
  assert.doesNotMatch(similarity, /No risk flagged|Embedded text|Safe confidence/);

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
