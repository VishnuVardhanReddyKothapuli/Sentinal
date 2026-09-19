import { useEffect, useRef, useState } from 'react';
import { FileImage, Film, Info, Layers3, LockKeyhole, ScanLine, UploadCloud, X, ArrowUpRight } from 'lucide-react';
import { api, errorMessage } from '../api';
import AnalysisResult from '../components/AnalysisResult';
import { ErrorNotice, PageHeading } from '../components/common/Ui';

const modes = {
  nsfw: {
    title: 'Safety Analyzer',
    description: 'Inspect visual risks, detect adult/graphic material, and evaluate embedded text.',
    label: 'Analyze Content Safety',
    steps: ['Visual classification', 'Embedded text & safety', 'Contextual explanation']
  },
  similarity: {
    title: 'Similarity Checker',
    description: 'Find semantic connections and compare your media against your vector library.',
    label: 'Find Similar Content',
    steps: ['Semantic embedding', 'Vector library search', 'Duplicate assessment']
  },
  combined: {
    title: 'Combined Analysis',
    description: 'One upload. Unified intelligence. A complete assessment of your content.',
    label: 'Run Combined Analysis',
    steps: ['Visual safety & text', 'Similarity & duplicates', 'Unified assessment']
  }
};

export default function Analyzer({ mode }) {
  const config = modes[mode];
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [pending, setPending] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const chooseFile = (next) => {
    setError('');
    setResult(null);
    if (!next) return;
    if (
      !['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo'].includes(
        next.type
      )
    ) {
      setError('Choose a JPG, PNG, WebP image or MP4, WebM, MOV, AVI video.');
      return;
    }
    if (next.size > 50 * 1024 * 1024) {
      setError('This file exceeds the 50 MB upload limit. Choose a smaller file.');
      return;
    }
    setFile(next);
  };

  const analyze = async () => {
    if (!file || pending) return;
    setPending(true);
    setResult(null);
    setError('');
    setProgress(0);
    const form = new FormData();
    form.append('file', file);
    try {
      const { data } = await api.post(`/analyze/${mode}`, form, {
        onUploadProgress: (e) => setProgress(Math.round((e.loaded / (e.total || file.size)) * 100))
      });
      setResult(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setPending(false);
    }
  };

  return (
    <>
      <PageHeading eyebrow="ANALYSIS STUDIO" title={config.title} description={config.description}>
        <span className="studio-mode">
          <Layers3 size={15} />
          <span>{mode === 'combined' ? 'Full Pipeline' : mode === 'nsfw' ? 'Safety Pipeline' : 'Similarity Pipeline'}</span>
        </span>
      </PageHeading>

      <div className="analyzer-grid">
        <div className="upload-column">
          <section className="panel upload-panel">
            <div className="panel-heading">
              <h2>
                <UploadCloud size={18} />
                Source Media
              </h2>
              <span className="muted micro">01 / INPUT</span>
            </div>

            <input
              className="sr-only"
              ref={inputRef}
              id="media-file"
              aria-label="Choose image or video"
              type="file"
              accept=".jpg,.jpeg,.png,.webp,.mp4,.webm,.mov,.avi"
              disabled={pending}
              onChange={(e) => chooseFile(e.target.files?.[0])}
            />

            <div
              className={`dropzone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
              onDragOver={(e) => {
                e.preventDefault();
                if (!pending) setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                if (!pending) chooseFile(e.dataTransfer.files?.[0]);
              }}
            >
              {file ? (
                <>
                  <div className="source-preview">
                    {file.type.startsWith('video/') ? (
                      <video src={preview} controls aria-label="Selected video preview" />
                    ) : (
                      <img src={preview} alt="Selected media preview" />
                    )}
                  </div>
                  <div className="selected-file">
                    <FileImage size={18} />
                    <div>
                      <strong>{file.name}</strong>
                      <small>
                        {(file.size / 1024 / 1024).toFixed(2)} MB · {file.type.startsWith('video/') ? 'VIDEO' : 'IMAGE'}
                      </small>
                    </div>
                    <button
                      className="icon-button"
                      disabled={pending}
                      aria-label="Remove selected file"
                      onClick={() => {
                        setFile(null);
                        setResult(null);
                        if (inputRef.current) inputRef.current.value = '';
                      }}
                    >
                      <X size={16} />
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <span className="upload-icon">
                    <UploadCloud size={28} strokeWidth={1.5} />
                  </span>
                  <h3>Drop media to inspect</h3>
                  <p>Drag and drop an image or video here</p>
                  <button className="button secondary" onClick={() => inputRef.current?.click()}>
                    <span>Browse Files</span>
                    <UploadCloud size={15} />
                  </button>
                  <span className="dropzone-limit">
                    JPG, PNG, WebP · MP4, WebM, MOV, AVI
                    <br />
                    Up to 50 MB per file
                  </span>
                </>
              )}
            </div>

            <div className="media-types">
              <span>
                <FileImage size={14} />
                Images
              </span>
              <span>
                <Film size={14} />
                Videos
              </span>
              <span>
                <LockKeyhole size={14} />
                Private Scoping
              </span>
            </div>

            <div className="upload-actions">
              <ErrorNotice>{error}</ErrorNotice>
              {pending && (
                <div className="progress-state" role="status">
                  <div>
                    <span>{progress < 100 ? 'Uploading media…' : 'Analyzing media with vision core…'}</span>
                    <strong>{progress < 100 ? `${progress}%` : 'Processing'}</strong>
                  </div>
                  <progress max="100" value={progress} aria-label="Upload progress" />
                </div>
              )}
              <button className="button primary full-width" disabled={!file || pending} onClick={analyze}>
                <ScanLine size={17} />
                <span>{pending ? 'Analysis in Progress…' : config.label}</span>
                <ArrowUpRight size={15} />
              </button>
            </div>
          </section>

          <section className="pipeline-panel">
            <span className="eyebrow">Behind the Analysis</span>
            <ol>
              {config.steps.map((step, index) => (
                <li key={step}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <div>
                    <strong>{step}</strong>
                    <small>
                      {index === 0
                        ? 'Inspect the source file'
                        : index === 1
                        ? 'Extract multimodal signals'
                        : 'Synthesize accountable evidence'}
                    </small>
                  </div>
                </li>
              ))}
            </ol>
            <div className="pipeline-disclaimer">
              <Info size={15} />
              <p>Active models govern coverage. Any missing signals are flagged for human oversight.</p>
            </div>
          </section>
        </div>

        <AnalysisResult record={result} mode={mode} />
      </div>
    </>
  );
}
