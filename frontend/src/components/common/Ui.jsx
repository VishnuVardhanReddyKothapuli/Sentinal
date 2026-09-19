import { Dialog, DialogPanel, DialogTitle } from '@headlessui/react';
import { AlertCircle, X } from 'lucide-react';

export function Badge({ status }) {
  const norm = String(status || 'REVIEW').toUpperCase();
  return (
    <span className={`badge ${norm.toLowerCase()}`}>
      <span />
      {norm}
    </span>
  );
}

export function ErrorNotice({ children }) {
  return children ? (
    <div className="notice error" role="alert">
      <AlertCircle size={16} />
      <span>{children}</span>
    </div>
  ) : null;
}

export function Modal({ title, children, onClose }) {
  return (
    <Dialog open onClose={onClose} className="modal-root">
      <div className="modal-shade" />
      <div className="modal-wrap">
        <DialogPanel className="modal-panel">
          <div className="section-heading">
            <DialogTitle as="h2">{title}</DialogTitle>
            <button onClick={onClose} className="icon-button" aria-label="Close dialog">
              <X size={18} />
            </button>
          </div>
          {children}
        </DialogPanel>
      </div>
    </Dialog>
  );
}

export function PageHeading({ eyebrow, title, description, children }) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {description && <p className="page-description">{description}</p>}
      </div>
      {children}
    </div>
  );
}
