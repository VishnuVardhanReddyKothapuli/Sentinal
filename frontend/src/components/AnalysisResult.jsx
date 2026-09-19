import { CircleCheck, FileText, Fingerprint, Info, ScanText, ShieldCheck, Sparkles } from 'lucide-react';
import ConfidenceMeter from './common/ConfidenceMeter';
import { Badge } from './common/Ui';
import MediaPreview from './MediaPreview';

export default function AnalysisResult({ record, mode = 'combined' }) {
  const safety = mode !== 'similarity';
  const similarity = mode !== 'nsfw';
  const scores = record?.scores;

  return (
    <div className={`analysis-results ${record ? 'has-result' : ''}`}>
      <div className="panel result-panel">
        <div className="panel-heading">
          <h2>
            <ShieldCheck size={18} />
            Assessment
          </h2>
          {record ? <Badge status={record.overall_status} /> : <span className="muted micro">AWAITING MEDIA</span>}
        </div>

        {!record ? (
          <div className="result-empty">
            <div className="empty-crosshair">
              <ScanText size={32} strokeWidth={1.4} />
            </div>
            <h3>Clarity begins with an upload.</h3>
            <p>
              Upload media to evaluate{' '}
              {mode === 'similarity'
                ? 'vector similarity, duplicate signals, and semantic matches'
                : 'safety classifications, embedded OCR text, and contextual analysis'}
              .
            </p>
            <div className="empty-signal-row">
              <span>INPUT</span>
              <i />
              <span>ANALYSIS</span>
              <i />
              <span>INSIGHT</span>
            </div>
          </div>
        ) : (
          <>
            <div className="result-main">
              <ConfidenceMeter
                value={safety ? scores?.safe : record.similarity_score}
                label={safety ? 'Safe confidence' : 'Closest match'}
              />
              <div className="result-signal">
                <span className="eyebrow">{safety ? 'VISUAL SAFETY' : 'SIMILARITY SIGNAL'}</span>
                <h3>
                  {record.overall_status === 'SAFE'
                    ? safety
                      ? 'No risk flagged'
                      : 'No close match flagged'
                    : record.overall_status === 'FLAGGED'
                    ? 'Attention required'
                    : 'Human review needed'}
                </h3>
                <p>
                  {record.overall_status === 'REVIEW'
                    ? 'Certain signals require attention. Review evidence and capability notes below.'
                    : 'Review each signal before reaching a final moderation decision.'}
                </p>
                {record.frames_analyzed > 0 && (
                  <span className="metadata-chip">{record.frames_analyzed} frame(s) analyzed</span>
                )}
              </div>
            </div>

            {safety && (
              <div className="score-list">
                {['safe', 'explicit', 'suggestive', 'gore'].map((label) => (
                  <div className={`score-row score-${label}`} key={label}>
                    <span>{label}</span>
                    <div>
                      <i style={{ width: `${Math.max(0, Math.min(100, scores?.[label] || 0))}%` }} />
                    </div>
                    <strong>
                      {typeof scores?.[label] === 'number' ? `${scores[label].toFixed(1)}%` : 'N/A'}
                    </strong>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {record && (
        <>
          <div className="panel narrative">
            <h2>
              <Sparkles size={18} />
              Context & Explanation
            </h2>
            <p>{record.ai_explanation || 'An explanation is not available for this analysis.'}</p>
            <div className="narrative-note">
              <Info size={14} />
              Automated intelligence is designed to assist human moderation oversight.
            </div>
          </div>

          {safety && (
            <div className="panel text-result">
              <div className="section-heading">
                <h2>
                  <FileText size={17} />
                  Embedded Text (OCR)
                </h2>
                <Badge status={record.text_flagged ? 'FLAGGED' : record.checks_complete?.ocr ? 'SAFE' : 'REVIEW'} />
              </div>
              <p className="extracted-text">
                {record.extracted_text ||
                  (record.checks_complete?.ocr
                    ? 'OCR completed. No embedded text was detected in the sampled media.'
                    : 'Text extraction is incomplete or unavailable. Review capability notes below.')}
              </p>
              {record.text_flag_reason && <p className="flag-reason">{record.text_flag_reason}</p>}
            </div>
          )}

          {similarity && (
            <div className="panel similarity-result">
              <div className="section-heading">
                <h2>
                  <Fingerprint size={18} />
                  Visual Matches
                </h2>
                <span className="metadata-chip">
                  {record.is_duplicate ? 'Duplicate Detected' : 'Vector Library Search'}
                </span>
              </div>
              {record.matches?.length ? (
                <div className="matches">
                  {record.matches.map((match, index) => (
                    <div className="match" key={match.record_id}>
                      <MediaPreview
                        recordId={match.record_id}
                        fileType={match.file_type}
                        alt={`Visual match ${index + 1}`}
                      />
                      <div>
                        <strong>{match.file_name || `Match ${String(index + 1).padStart(2, '0')}`}</strong>
                        <span>{Number(match.similarity_score ?? match.score).toFixed(1)}% similarity</span>
                        <small>Record {match.record_id.slice(0, 8)}</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="match-empty">
                  {record.checks_complete?.similarity ? <CircleCheck size={22} /> : <Info size={22} />}
                  <p>
                    {record.checks_complete?.similarity
                      ? 'No matching records found.'
                      : 'Similarity search could not be completed.'}
                    <small>
                      {record.checks_complete?.similarity
                        ? 'No stored media in your account met the similarity threshold.'
                        : 'Review capability notes below for indexing status.'}
                    </small>
                  </p>
                </div>
              )}
            </div>
          )}

          {record.warnings?.length > 0 && (
            <div className="notice warning">
              <Info size={18} />
              <div>
                <strong>Capability Notes</strong>
                <ul>
                  {record.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
