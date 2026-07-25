import { useState, useEffect, useCallback } from 'react'
import { fetchHistory } from '../api'

export default function HistoryPanel({ refreshKey }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchHistory(50)
      setItems(data)
    } catch {
      // best-effort
    } finally {
      setLoading(false)
    }
  }, [])

  // Load on mount + whenever refreshKey changes (after a new analysis).
  useEffect(() => {
    load()
  }, [load, refreshKey])

  const formatDate = (iso) => {
    try {
      return new Date(iso).toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return iso
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100">
        <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <svg className="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          Recent Uploads
        </h2>
        <button
          onClick={load}
          className="text-xs text-gray-400 hover:text-gray-600 transition-colors flex items-center gap-1"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="bg-gray-50/70">
              <th className="px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">File</th>
              <th className="px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">Type</th>
              <th className="px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
              <th className="px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">Score</th>
              <th className="px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">User</th>
              <th className="px-5 py-2.5 text-xs font-semibold text-gray-400 uppercase tracking-wider">When</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {loading && items.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-5 py-10 text-center text-gray-400 text-sm">
                  Loading…
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-5 py-10 text-center text-gray-400 text-sm">
                  No uploads yet.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-5 py-3 text-gray-700 max-w-[160px] truncate">{item.filename}</td>
                  <td className="px-5 py-3 text-gray-500">{item.media_type}</td>
                  <td className="px-5 py-3">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        item.is_nsfw
                          ? 'bg-red-50 text-red-500'
                          : 'bg-green-50 text-green-600'
                      }`}
                    >
                      {item.nsfw_status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-500 tabular-nums">
                    {(item.nsfw_score * 100).toFixed(0)}%
                  </td>
                  <td className="px-5 py-3 text-gray-500">{item.uploaded_by}</td>
                  <td className="px-5 py-3 text-gray-400 text-xs whitespace-nowrap">
                    {formatDate(item.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
