import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../auth';
export default function ProtectedRoutes({admin=false}) {const {user,loading}=useAuth();const location=useLocation();if(loading)return <div className="loading-state" role="status">Restoring your session…</div>;if(!user)return <Navigate to="/login" state={{from:location.pathname}} replace/>;if(admin&&user.role!=='ADMIN')return <Navigate to="/" replace/>;return <Outlet/>;}
