const API_BASE = '';

/**
 * Upload a file for NSFW + copyright moderation.
 * @param {File} file
 * @param {string} uploadedBy
 * @param {boolean} deepMatch
 * @returns {Promise<object>}
 */
export async function moderate(file, uploadedBy = 'anonymous', deepMatch = false) {
  const form = new FormData();
  form.append('file', file);
  form.append('uploaded_by', uploadedBy || 'anonymous');
  form.append('deep_match', deepMatch ? 'true' : 'false');

  const res = await fetch(`${API_BASE}/api/moderate`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Request failed (${res.status})`);
  }

  return res.json();
}

/**
 * Fetch recent upload history.
 * @param {number} limit
 * @returns {Promise<object[]>}
 */
export async function fetchHistory(limit = 50) {
  const res = await fetch(`${API_BASE}/api/history?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}
