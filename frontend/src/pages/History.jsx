import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, FileImage, History as HistoryIcon, Search, Trash2, ArrowUpRight } from 'lucide-react';
import { api, errorMessage } from '../api';
import { Badge, ErrorNotice, Modal, PageHeading } from '../components/common/Ui';
import AnalysisResult from '../components/AnalysisResult';
import MediaPreview from '../components/MediaPreview';

export default function History() {
  const [params, setParams] = useSearchParams();
  const page = Number(params.get('page')) || 1;
  const status = params.get('status') || '';
  const search = params.get('search') || '';
  const [data, setData] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [record, setRecord] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [pending, setPending] = useState(false);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    const timer = setTimeout(
      () =>
        api
          .get('/user/history', { params: { page, page_size: 10, status, search } })
          .then((r) => {
            if (active) setData(r.data);
          })
          .catch((err) => {
            if (active) setError(errorMessage(err));
          })
          .finally(() => {
            if (active) setLoading(false);
          }),
      250
    );
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [page, status, search, revision]);

  const update = (key, value) =>
    setParams((current) => {
      const next = new URLSearchParams(current);
      if (value) next.set(key, value);
      else next.delete(key);
      if (key !== 'page') next.delete('page');
      return next;
    });

  const openRecord = async (id) => {
    try {
      setError('');
      const { data } = await api.get(`/user/history/${id}`);
      setRecord(data);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const remove = async () => {
    setPending(true);
    try {
      await api.delete(`/user/history/${deleting.id}`);
      setDeleting(null);
      setRevision((x) => x + 1);
      if (data.items.length === 1 && page > 1) update('page', String(page - 1));
    } catch (err) {
      setError(errorMessage(err));
      setDeleting(null);
    } finally {
      setPending(false);
    }
  };

  return (
    <>
      <PageHeading
        eyebrow="YOUR CONTENT LIBRARY"
        title="Analysis History"
        description="Every scan, signal, and decision. Revisit and inspect your records."
      >
        <Link className="button primary" to="/analyze/combined">
          <span>New Analysis</span>
          <ArrowRight size={15} />
        </Link>
      </PageHeading>

      <section className="panel history-panel">
        <div className="table-toolbar">
          <div className="search-field">
            <Search size={16} />
            <input
              type="search"
              value={search}
              onChange={(e) => update('search', e.target.value)}
              placeholder="Search file names…"
              aria-label="Search analysis file names"
            />
          </div>
          <div className="filter-field">
            <label htmlFor="status-filter">Status Filter</label>
            <select id="status-filter" value={status} onChange={(e) => update('status', e.target.value)}>
              <option value="">All Statuses</option>
              <option value="SAFE">Safe Only</option>
              <option value="FLAGGED">Flagged</option>
              <option value="REVIEW">Needs Review</option>
            </select>
          </div>
        </div>

        <ErrorNotice>{error}</ErrorNotice>

        {loading ? (
          <div className="table-loading" role="status" aria-label="Loading analysis history">
            {[0, 1, 2, 3].map((i) => (
              <div className="skeleton-row" key={i} />
            ))}
          </div>
        ) : !data.items.length ? (
          <div className="table-empty">
            <HistoryIcon size={32} strokeWidth={1.3} />
            <h2>{search || status ? 'No matching analyses' : 'Your history starts with a scan'}</h2>
            <p>
              {search || status
                ? 'Try adjusting your search keywords or clearing the status filter.'
                : 'Upload your first image or video to populate your private content library.'}
            </p>
            <Link className="button secondary" to="/analyze/combined">
              <span>Start Analysis</span>
              <ArrowRight size={15} />
            </Link>
          </div>
        ) : (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Media File</th>
                    <th>Pipeline</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th className="align-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <button className="file-cell" onClick={() => openRecord(item.id)}>
                          <span className="file-icon">
                            <FileImage size={17} />
                          </span>
                          <span>
                            {item.file_name}
                            <small>
                              {item.file_type} · {item.id.slice(0, 8)}
                            </small>
                          </span>
                        </button>
                      </td>
                      <td>
                        <span className="table-type">{item.analysis_type}</span>
                      </td>
                      <td>
                        <Badge status={item.overall_status} />
                      </td>
                      <td className="muted nowrap">
                        {new Date(item.created_at).toLocaleDateString(undefined, {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric'
                        })}
                      </td>
                      <td>
                        <div className="row-actions">
                          <button className="text-link" onClick={() => openRecord(item.id)}>
                            <span>View</span>
                            <ArrowUpRight size={13} />
                          </button>
                          <button
                            className="icon-button danger-text"
                            onClick={() => setDeleting(item)}
                            aria-label={`Delete ${item.file_name}`}
                            title="Delete record"
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <span>
                {(page - 1) * 10 + 1}–{Math.min(page * 10, data.total)} of {data.total} analyses
              </span>
              <div>
                <button
                  className="icon-button"
                  disabled={page === 1}
                  onClick={() => update('page', String(page - 1))}
                  aria-label="Previous page"
                >
                  <ArrowLeft size={16} />
                </button>
                <span className="font-semibold text-[var(--text-primary)]">Page {page}</span>
                <button
                  className="icon-button"
                  disabled={page * 10 >= data.total}
                  onClick={() => update('page', String(page + 1))}
                  aria-label="Next page"
                >
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </section>

      {record && (
        <Modal title={record.file_name} onClose={() => setRecord(null)}>
          <div className="detail-preview">
            <MediaPreview recordId={record.id} fileType={record.file_type} alt={record.file_name} />
          </div>
          <AnalysisResult record={record} mode={record.analysis_type.toLowerCase()} />
        </Modal>
      )}

      {deleting && (
        <Modal title="Delete this analysis?" onClose={() => !pending && setDeleting(null)}>
          <p className="modal-copy">
            The analysis for <strong>{deleting.file_name}</strong>, its stored media preview, and indexed vectors will
            be permanently removed from your account.
          </p>
          <div className="modal-actions">
            <button className="button secondary" disabled={pending} onClick={() => setDeleting(null)}>
              Keep Analysis
            </button>
            <button className="button danger" disabled={pending} onClick={remove}>
              <Trash2 size={15} />
              <span>{pending ? 'Deleting…' : 'Delete Record'}</span>
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
