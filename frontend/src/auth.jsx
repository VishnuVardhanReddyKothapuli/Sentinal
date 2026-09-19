import { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';
const AuthContext = createContext(null);
export function AuthProvider({children}) {
  const [user,setUser] = useState(null); const [loading,setLoading] = useState(true);
  useEffect(() => {const logout = () => setUser(null); window.addEventListener('sentinel:logout',logout); if(localStorage.getItem('sentinel_token')) api.get('/auth/me').then(r=>setUser(r.data)).catch(()=>localStorage.removeItem('sentinel_token')).finally(()=>setLoading(false)); else setLoading(false); return ()=>window.removeEventListener('sentinel:logout',logout);},[]);
  const authenticate = async (route, data) => {const response = await api.post(`/auth/${route}`,data); localStorage.setItem('sentinel_token',response.data.access_token); setUser(response.data.user);};
  const logout = () => {localStorage.removeItem('sentinel_token');setUser(null);};
  return <AuthContext.Provider value={{user,loading,authenticate,logout}}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
