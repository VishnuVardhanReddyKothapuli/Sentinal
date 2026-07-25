import { useState, useCallback } from 'react'
import UploadPanel from './components/UploadPanel'
import HistoryPanel from './components/HistoryPanel'

export default function App() {
  // A counter that increments after each successful analysis
  // to tell HistoryPanel to refetch.
  const [refreshKey, setRefreshKey] = useState(0)

  const onAnalyzed = useCallback(() => {
    setRefreshKey((k) => k + 1)
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Header ─────────────────────────────────── */}
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-3">
          <svg
            className="w-7 h-7 text-blue-500 shrink-0"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          <h1 className="text-xl font-semibold tracking-tight">
            <span className="text-blue-500">Senti</span>
            <span className="text-gray-800">Nal</span>
          </h1>
          <span className="hidden sm:inline text-xs text-gray-400 ml-2 mt-0.5">
            Content moderation &amp; copyright detection
          </span>
        </div>
      </header>

      {/* ── Main two-panel layout ──────────────────── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left — Upload + Results */}
        <section className="lg:col-span-5 xl:col-span-4">
          <UploadPanel onAnalyzed={onAnalyzed} />
        </section>

        {/* Right — History */}
        <section className="lg:col-span-7 xl:col-span-8">
          <HistoryPanel refreshKey={refreshKey} />
        </section>
      </main>

      {/* ── Footer ─────────────────────────────────── */}
      <footer className="border-t border-gray-200 bg-white text-center text-xs text-gray-400 py-4">
        SentiNal — AI-powered content moderation
      </footer>
    </div>
  )
}
