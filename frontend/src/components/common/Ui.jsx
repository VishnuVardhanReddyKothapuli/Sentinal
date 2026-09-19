import { Dialog, DialogPanel, DialogTitle } from '@headlessui/react';
import { AlertCircle, X } from 'lucide-react';
export function Badge({status}){return <span className={`badge ${String(status).toLowerCase()}`}><span/>{status||'REVIEW'}</span>;}
export function ErrorNotice({children}) {return children?<div className="notice error" role="alert"><AlertCircle size={18}/><span>{children}</span></div>:null;}
export function Modal({title,children,onClose}) {return <Dialog open onClose={onClose} className="modal-root"><div className="modal-shade"/><div className="modal-wrap"><DialogPanel className="modal-panel"><div className="section-heading"><DialogTitle as="h2">{title}</DialogTitle><button onClick={onClose} className="icon-button" aria-label="Close dialog"><X size={21}/></button></div>{children}</DialogPanel></div></Dialog>;}
export function PageHeading({eyebrow,title,description,children}){return <div className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{description}</p></div>{children}</div>;}
