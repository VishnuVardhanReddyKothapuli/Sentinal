import { useState, useRef, useCallback } from 'react'
import { moderate } from '../api'

export default function UploadPanel({ onAnalyzed }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [username, setUsername] = useState('anonymous')
  const [mode, setMode] = useState('quick') // 'quick' | 'deep'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const pickFile = useCallback((f) => {
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setError(null)
    setResult(null)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f) pickFile(f)
  }, [pickFile])

  const handleAnalyze = useCallback(async () => {
    if (!file) {
      setError('Please choose an image or GIF first.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const data = await moderate(file, username, mode === 'deep')
      setResult(data)
      onAnalyzed?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [file, username, mode, onAnalyzed])

  const resetUpload = useCallback(() => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ''
  }, [])

  const nsfwPct = result ? (result.nsfw_score * 100).toFixed(1) : 0
  const dup = result?.duplicate

  return (
    <div className="space-y-5">
      {/* ── Mode Toggle ──────────────────────────── */}
      <div className="flex gap-2">
        <button
          onClick={() => setMode('quick')}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
            mode === 'quick'
              ? 'bg-blue-50 text-blue-600 ring-1 ring-blue-200'
              : 'bg-white text-gray-500 ring-1 ring-gray-200 hover:bg-gray-50'
          }`}
        >
          Quick Scan
        </button>
        <button
          onClick={() => setMode('deep')}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
            mode === 'deep'
              ? 'bg-blue-50 text-blue-600 ring-1 ring-blue-200'
              : 'bg-white text-gray-500 ring-1 ring-gray-200 hover:bg-gray-50'
          }`}
        >
          Deep Match
        </button>
        <span className="text-xs text-gray-400 self-center ml-2">
          {mode === 'quick' ? 'NSFW check only' : 'NSFW + copyright lookup'}
        </span>
      </div>

      {/* ── Drop Zone ────────────────────────────── */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl cursor-pointer transition-all
          ${dragOver
            ? 'border-blue-400 bg-blue-50/50'
            : file
              ? 'border-gray-200 bg-white'
              : 'border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50/50'
          }
          ${file ? 'p-4' : 'p-10'}
        `}
      >
        {file && preview ? (
          <div className="text-center">
            <img
              src={preview}
              alt="Preview"
              className="max-h-44 max-w-full mx-auto rounded-lg object-contain"
            />
            <p className="text-sm text-gray-500 mt-3 truncate">{file.name}</p>
            <button
              onClick={(e) => { e.stopPropagation(); resetUpload() }}
              className="mt-2 text-xs text-gray-400 hover:text-red-500 transition-colors"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="text-center">
            <svg
              className="w-10 h-10 mx-auto text-gray-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="3" width="18" height="18" rx="3" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="m21 15-5-5L5 21" />
            </svg>
            <p className="text-sm text-gray-500 mt-3">
              Drag an image here, or click to browse
            </p>
            <p className="text-xs text-gray-400 mt-1">
              JPG, PNG, GIF, WebP
            </p>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.gif"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (f) pickFile(f)
          }}
        />
      </div>

      {/* ── Username + Analyze ───────────────────── */}
      <div className="flex gap-3">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="flex-1 h-10 px-3 text-sm bg-white border border-gray-200 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300
                     transition-all placeholder:text-gray-400"
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !file}
          className="h-10 px-5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300
                     text-white text-sm font-medium rounded-lg transition-all
                     flex items-center gap-2 shrink-0"
        >
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full inline-block"
                    style={{ animation: 'spin 0.7s linear infinite' }} />
              Analyzing…
            </>
          ) : (
            <>
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                   strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              Analyze
            </>
          )}
        </button>
      </div>

      {/* ── Error ────────────────────────────────── */}
      {error && (
        <div className="animate-fade-in flex items-center gap-2 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600">
          <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {error}
        </div>
      )}

      {/* ── Results ──────────────────────────────── */}
      {result && (
        <div className="animate-fade-in bg-white border border-gray-200 rounded-xl p-5 space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{result.filename}</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {result.media_type.toUpperCase()} · {result.frames_analyzed} frame{result.frames_analyzed > 1 ? 's' : ''} analyzed
              </p>
            </div>
            <span
              className={`shrink-0 text-xs font-semibold px-3 py-1 rounded-full ${
                result.is_nsfw
                  ? 'bg-red-50 text-red-600'
                  : 'bg-green-50 text-green-600'
              }`}
            >
              {result.is_nsfw ? '⚠ NSFW' : '✓ Safe'}
            </span>
          </div>

          {/* Score bar */}
          <div>
            <div className="flex justify-between text-xs text-gray-500 mb-1.5">
              <span>NSFW confidence</span>
              <span className="font-medium">{nsfwPct}%</span>
            </div>
            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  result.nsfw_score >= 0.5 ? 'bg-red-400' : 'bg-green-400'
                }`}
                style={{ width: `${nsfwPct}%` }}
              />
            </div>
          </div>

          {/* Duplicate / copyright info */}
          {dup && dup.is_duplicate && (
            <div className="flex items-start gap-2.5 p-3 bg-amber-50 border border-amber-100 rounded-lg text-sm text-amber-700">
              <svg className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <span>
                Copyright match detected — already posted by{' '}
                <strong className="font-semibold">{dup.matched_user}</strong>
                {' '}({Math.round((dup.similarity || 0) * 100)}% similarity)
              </span>
            </div>
          )}

          {dup && !dup.is_duplicate && dup.similarity != null && (
            <div className="flex items-start gap-2.5 p-3 bg-gray-50 border border-gray-100 rounded-lg text-sm text-gray-500">
              <svg className="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <span>
                No copyright match (closest {Math.round((dup.similarity || 0) * 100)}%)
              </span>
            </div>
          )}

          {result.stored && (
            <p className="text-xs text-gray-400">Stored in database</p>
          )}
        </div>
      )}
    </div>
  )
}
