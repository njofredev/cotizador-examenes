'use client';

import * as React from 'react';
import { 
  BarChart3, 
  Users, 
  Database, 
  LogOut, 
  TrendingUp, 
  Calendar, 
  DollarSign, 
  Search, 
  ArrowLeft,
  Edit2,
  Save,
  X,
  User,
  Hash,
  Activity,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';
import { toast, Toaster } from 'sonner';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { 
  adminLogin, 
  getAdminStats, 
  getAdminHistory, 
  getExamenes, 
  updateArancel, 
  Examen 
} from '../../lib/api';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogDescription
} from '../../components/ui/dialog';

// Custom cn function since we don't have clx
function cn(...inputs: any[]) {
   return inputs.filter(Boolean).join(' ');
}

export default function AdminDashboard() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(false);
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [token, setToken] = React.useState('');
  const [activeTab, setActiveTab] = React.useState<'dashboard'|'pacientes'|'precios'>('dashboard');
  const [isLoading, setIsLoading] = React.useState(false);
  
  // Data State
  const [stats, setStats] = React.useState<any>(null);
  const [history, setHistory] = React.useState<any[]>([]);
  const [examenes, setExamenes] = React.useState<Examen[]>([]);
  const [searchHistory, setSearchHistory] = React.useState('');
  const [searchExams, setSearchExams] = React.useState('');

  // Edit State
  const [editingExamen, setEditingExamen] = React.useState<Examen | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = React.useState(false);

  // Pagination for exams (too many to show at once)
  const [examPage, setExamPage] = React.useState(1);
  const examsPerPage = 10;

  React.useEffect(() => {
    const savedToken = localStorage.getItem('adminToken');
    if (savedToken) {
      setToken(savedToken);
      setIsLoggedIn(true);
      loadDashboardData(savedToken);
    }
  }, []);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await adminLogin({ username, password });
      if (res.data.success) {
        setToken(res.data.token);
        setIsLoggedIn(true);
        localStorage.setItem('adminToken', res.data.token);
        toast.success('Sesión iniciada correctamente');
        loadDashboardData(res.data.token);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem('adminToken');
    setToken('');
    setIsLoggedIn(false);
    toast.info('Sesión cerrada');
  }

  async function loadDashboardData(t: string) {
    setIsLoading(true);
    try {
      const [statsRes, historyRes, examsRes] = await Promise.all([
        getAdminStats(t),
        getAdminHistory(t),
        getExamenes()
      ]);
      setStats(statsRes.data);
      setHistory(historyRes.data);
      setExamenes(examsRes.data);
    } catch (err) {
      toast.error('Sesión expirada o inválida');
      handleLogout();
    } finally {
      setIsLoading(false);
    }
  }

  const filteredHistory = history.filter(h => 
    h.nombre_paciente?.toLowerCase().includes(searchHistory.toLowerCase()) ||
    h.documento_id?.includes(searchHistory) ||
    h.folio?.includes(searchHistory)
  );

  const filteredExams = examenes.filter(e => 
    e.nombre.toLowerCase().includes(searchExams.toLowerCase()) ||
    e.codigo.includes(searchExams)
  );

  const paginatedExams = filteredExams.slice((examPage-1)*examsPerPage, examPage*examsPerPage);
  const totalExamPages = Math.ceil(filteredExams.length / examsPerPage);

  async function handleUpdatePrice() {
    if (!editingExamen) return;
    setIsLoading(true);
    try {
      await updateArancel(editingExamen.codigo, {
        valor_bono_fonasa: editingExamen.valor_bono_fonasa,
        valor_copago: editingExamen.valor_copago,
        valor_particular_general: editingExamen.valor_particular_general,
        valor_particular_preferencial: editingExamen.valor_particular_preferencial
      }, token);
      
      toast.success('Precio actualizado correctamente');
      setIsEditModalOpen(false);
      loadDashboardData(token);
    } catch (err) {
      toast.error('Error al actualizar precio');
    } finally {
      setIsLoading(false);
    }
  }

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <Toaster position="top-center" richColors />
        <Card className="w-full max-w-md border-slate-800 bg-slate-900 overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-500">
          <div className="bg-gradient-to-r from-brand-dark to-brand-mint h-1.5" />
          <CardHeader className="space-y-1 text-center pt-8">
            <div className="mx-auto w-12 h-12 bg-brand-mint/10 rounded-xl flex items-center justify-center mb-4">
              <LogOut className="h-6 w-6 text-brand-mint rotate-180" />
            </div>
            <CardTitle className="text-2xl font-black text-white px-2 tracking-tight">Acceso Administrativo</CardTitle>
            <CardDescription className="text-slate-400">Panel de Control Policlínico Tabancura</CardDescription>
          </CardHeader>
          <CardContent className="pt-4 pb-8">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <p className="text-xs font-bold text-slate-500 uppercase px-1">Usuario</p>
                <Input 
                  placeholder="admin" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white h-12"
                />
              </div>
              <div className="space-y-2">
                <p className="text-xs font-bold text-slate-500 uppercase px-1">Contraseña</p>
                <Input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white h-12"
                />
              </div>
              <Button type="submit" disabled={isLoading} className="w-full h-12 bg-brand-mint hover:bg-brand-mint/90 text-brand-dark font-black text-sm uppercase tracking-widest mt-4">
                {isLoading ? 'Autenticando...' : 'Entrar al Panel'}
              </Button>
            </form>
          </CardContent>
          <div className="text-center pb-6">
            <button onClick={() => window.location.href = '/'} className="text-xs text-slate-500 hover:text-brand-mint flex items-center gap-1 mx-auto transition-colors">
              <ArrowLeft className="h-3 w-3" /> Volver al Cotizador
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Toaster position="top-right" richColors />
      
      {/* Sidebar / Nav */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-mint flex items-center justify-center">
              <Activity className="h-5 w-5 text-brand-dark" />
            </div>
            <div>
              <p className="text-sm font-black text-white tracking-tight">TABANCURA <span className="text-brand-mint">ADMIN</span></p>
              <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest leading-none">v2.0 Beta</p>
            </div>
          </div>

          <div className="hidden md:flex gap-1">
            <Button variant={activeTab === 'dashboard' ? 'secondary' : 'ghost'} size="sm" onClick={() => setActiveTab('dashboard')} className="font-bold">Dashboard</Button>
            <Button variant={activeTab === 'pacientes' ? 'secondary' : 'ghost'} size="sm" onClick={() => setActiveTab('pacientes')} className="font-bold">Pacientes</Button>
            <Button variant={activeTab === 'precios' ? 'secondary' : 'ghost'} size="sm" onClick={() => setActiveTab('precios')} className="font-bold">Maestro Precios</Button>
          </div>

          <Button variant="ghost" size="sm" onClick={handleLogout} className="text-rose-400 hover:text-rose-300 gap-2">
            <LogOut className="h-4 w-4" /> <span className="hidden sm:inline">Cerrar Sesión</span>
          </Button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-700">
        
        {/* --- TAB DASHBOARD --- */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-3xl font-black text-white tracking-tighter">Panel de Reportería</h1>
                <p className="text-slate-400">Resumen general del movimiento de cotizaciones.</p>
              </div>
              <Button onClick={() => loadDashboardData(token)} disabled={isLoading} variant="outline" size="sm" className="border-slate-800 bg-slate-900 text-slate-400 text-xs">
                 Actualizar Datos
              </Button>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard 
                title="Total Cotizaciones" 
                value={stats?.total_cotizaciones || 0} 
                icon={<BarChart3 className="text-brand-mint" />} 
                description="Histórico acumulado"
              />
              <StatCard 
                title="Cotizaciones Hoy" 
                value={stats?.total_hoy || 0} 
                icon={<Calendar className="text-blue-400" />} 
                description="Actividad de hoy"
                highlight
              />
              <StatCard 
                title="Ingresos Fonasa" 
                value={`$${(stats?.monto_fonasa || 0).toLocaleString()}`} 
                icon={<DollarSign className="text-amber-400" />} 
                description="Estimado recaudado"
              />
              <StatCard 
                title="Ingresos Particulares" 
                value={`$${(stats?.monto_particular || 0).toLocaleString()}`} 
                icon={<TrendingUp className="text-emerald-400" />} 
                description="Estimado recaudado"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Ranking Examenes */}
              <Card className="lg:col-span-1 bg-slate-900 border-slate-800 shadow-xl overflow-hidden">
                <CardHeader>
                  <CardTitle className="text-lg font-bold flex gap-2 items-center">
                    <Activity className="h-5 w-5 text-brand-mint" />
                    Top 5 Exámenes
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {stats?.top_examenes.map((ex: any, idx: number) => (
                    <div key={idx} className="flex justify-between items-center group">
                      <div className="space-y-1 max-w-[70%]">
                        <p className="text-sm font-bold text-white leading-tight truncate">{ex.nombre}</p>
                        <div className="h-1 bg-slate-800 rounded-full w-full overflow-hidden">
                           <div className="h-full bg-brand-mint" style={{ width: `${stats.top_examenes[0].cantidad > 0 ? (ex.cantidad / stats.top_examenes[0].cantidad) * 100 : 0}%` }} />
                        </div>
                      </div>
                      <Badge variant="secondary" className="bg-slate-800 text-brand-mint font-black">
                        {ex.cantidad}
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card className="lg:col-span-2 bg-slate-900 border-slate-800 shadow-xl">
                 <CardHeader>
                    <CardTitle className="text-lg font-bold">Últimas Interacciones</CardTitle>
                 </CardHeader>
                 <CardContent>
                    <div className="space-y-4">
                       {history.slice(0, 6).map((h, i) => (
                          <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/50 border border-slate-800/50">
                             <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 text-xs font-bold">
                                   {h.nombre_paciente?.substring(0,2).toUpperCase()}
                                </div>
                                <div>
                                   <p className="text-sm font-bold text-white">{h.nombre_paciente}</p>
                                   <p className="text-[10px] text-slate-500 uppercase font-black">{new Date(h.fecha_cotizacion).toLocaleString()}</p>
                                </div>
                             </div>
                             <div className="text-right">
                                <p className="text-xs font-black text-brand-mint">{h.folio}</p>
                                <p className="text-[11px] text-slate-400">{h.prevision}</p>
                             </div>
                          </div>
                       ))}
                    </div>
                 </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* --- TAB PACIENTES --- */}
        {activeTab === 'pacientes' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-3xl font-black text-white tracking-tighter">Historial de Pacientes</h1>
                <p className="text-slate-400">Usuarios que han completado el flujo de cotización.</p>
              </div>
              <div className="w-full md:w-64 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <Input 
                  placeholder="Buscar por Nombre o RUT..." 
                  value={searchHistory}
                  onChange={(e) => setSearchHistory(e.target.value)}
                  className="bg-slate-900 border-slate-800 pl-10"
                />
              </div>
            </div>

            <Card className="bg-slate-900 border-slate-800 shadow-2xl overflow-hidden">
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-900 border-b border-slate-800">
                      <tr>
                        <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Paciente</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Documento ID</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Folio</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Previsión</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Fecha</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {filteredHistory.map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4">
                            <p className="text-sm font-bold text-white">{row.nombre_paciente}</p>
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-400 font-mono">
                            {row.documento_id}
                          </td>
                          <td className="px-6 py-4">
                            <Badge className="bg-brand-mint/10 text-brand-mint border-brand-mint/20">{row.folio}</Badge>
                          </td>
                          <td className="px-6 py-4 text-sm">
                             {row.prevision}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-500 font-bold uppercase">
                            {new Date(row.fecha_cotizacion).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-right">
                             <p className="text-sm font-black text-brand-mint">
                               ${(row.total_copago || 0).toLocaleString()}
                             </p>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                 </table>
               </div>
            </Card>
          </div>
        )}

        {/* --- TAB PRECIOS --- */}
        {activeTab === 'precios' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
               <div>
                  <h1 className="text-3xl font-black text-white tracking-tighter">Maestro de Aranceles</h1>
                  <p className="text-slate-400">Consulta y edita los precios del catálogo clínico.</p>
               </div>
               <div className="w-full md:w-64 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <Input 
                    placeholder="Filtrar catálogo..." 
                    value={searchExams}
                    onChange={(e) => {setSearchExams(e.target.value); setExamPage(1);}}
                    className="bg-slate-900 border-slate-800 pl-10"
                  />
               </div>
            </div>

            <Card className="bg-slate-900 border-slate-800 shadow-2xl overflow-hidden">
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-900 border-b border-slate-800 text-[10px] font-black uppercase tracking-widest text-slate-500">
                       <tr>
                         <th className="px-6 py-4">Cod / Examen</th>
                         <th className="px-6 py-4">Fonasa / Copago</th>
                         <th className="px-6 py-4">Part. Gral / Pref</th>
                         <th className="px-6 py-4 text-right">Acción</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                       {paginatedExams.map((ex, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition-colors group">
                             <td className="px-6 py-4 max-w-xs">
                                <p className="text-[10px] font-black text-slate-500">{ex.codigo}</p>
                                <p className="text-sm font-bold text-white line-clamp-2 leading-tight">{ex.nombre}</p>
                             </td>
                             <td className="px-6 py-4">
                                <div className="space-y-0.5">
                                   <p className="text-xs text-slate-500">F: <span className="text-blue-400 font-bold">${ex.valor_bono_fonasa.toLocaleString()}</span></p>
                                   <p className="text-xs text-slate-500">C: <span className="text-brand-mint font-bold">${ex.valor_copago.toLocaleString()}</span></p>
                                </div>
                             </td>
                             <td className="px-6 py-4">
                                <div className="space-y-0.5">
                                   <p className="text-xs text-slate-500">G: <span className="text-slate-300 font-bold">${ex.valor_particular_general.toLocaleString()}</span></p>
                                   <p className="text-xs text-brand-mint font-black">P: ${(ex.valor_particular_preferencial).toLocaleString()}</p>
                                </div>
                             </td>
                             <td className="px-6 py-4 text-right">
                                <Button 
                                  variant="ghost" 
                                  size="icon" 
                                  className="text-slate-500 hover:text-brand-mint opacity-0 group-hover:opacity-100 transition-opacity"
                                  onClick={() => {setEditingExamen({...ex}); setIsEditModalOpen(true);}}
                                >
                                   <Edit2 className="h-4 w-4" />
                                </Button>
                             </td>
                          </tr>
                       ))}
                    </tbody>
                 </table>
               </div>
               
               {/* Pagination Footer */}
               <div className="bg-slate-900 border-t border-slate-800 p-4 flex items-center justify-between">
                  <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Página {examPage} de {totalExamPages}</p>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={() => setExamPage(p => Math.max(1, p-1))} 
                      disabled={examPage === 1}
                      className="bg-slate-800 border-slate-700 h-8 w-8"
                    >
                       <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={() => setExamPage(p => Math.min(totalExamPages, p+1))} 
                      disabled={examPage === totalExamPages}
                      className="bg-slate-800 border-slate-700 h-8 w-8"
                    >
                       <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
               </div>
            </Card>
          </div>
        )}

      </main>

      {/* --- EDIT MODAL --- */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
         <DialogContent className="bg-slate-950 border-slate-800 text-white max-w-sm">
            <DialogHeader>
               <DialogTitle className="text-xl font-black">Editar Arancel</DialogTitle>
               <DialogDescription className="text-slate-400">
                  Modificando los precios para: <br/>
                  <span className="text-brand-mint font-bold text-sm tracking-tight">{editingExamen?.nombre}</span>
               </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
               <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                     <p className="text-[10px] font-black text-slate-500 uppercase">Valor Fonasa</p>
                     <Input 
                       type="number" 
                       value={editingExamen?.valor_bono_fonasa || 0}
                       onChange={(e) => setEditingExamen(prev => prev ? {...prev, valor_bono_fonasa: parseInt(e.target.value)} : null)}
                       className="bg-slate-900 border-slate-800"
                     />
                  </div>
                  <div className="space-y-1.5">
                     <p className="text-[10px] font-black text-slate-500 uppercase">Valor Copago</p>
                     <Input 
                       type="number" 
                       value={editingExamen?.valor_copago || 0}
                       onChange={(e) => setEditingExamen(prev => prev ? {...prev, valor_copago: parseInt(e.target.value)} : null)}
                       className="bg-slate-900 border-slate-800"
                     />
                  </div>
                  <div className="space-y-1.5">
                     <p className="text-[10px] font-black text-slate-500 uppercase">Part. General</p>
                     <Input 
                       type="number" 
                       value={editingExamen?.valor_particular_general || 0}
                       onChange={(e) => setEditingExamen(prev => prev ? {...prev, valor_particular_general: parseInt(e.target.value)} : null)}
                       className="bg-slate-900 border-slate-800"
                     />
                  </div>
                  <div className="space-y-1.5">
                     <p className="text-[10px] font-black text-slate-500 uppercase">Part. Preferencial</p>
                     <Input 
                       type="number" 
                       value={editingExamen?.valor_particular_preferencial || 0}
                       onChange={(e) => setEditingExamen(prev => prev ? {...prev, valor_particular_preferencial: parseInt(e.target.value)} : null)}
                       className="bg-slate-900 border-slate-800"
                     />
                  </div>
               </div>
            </div>

            <DialogFooter className="gap-2 sm:gap-0">
               <Button variant="ghost" onClick={() => setIsEditModalOpen(false)} className="text-slate-400 hover:text-white">Cancelar</Button>
               <Button onClick={handleUpdatePrice} disabled={isLoading} className="bg-brand-mint hover:bg-brand-mint/90 text-brand-dark font-bold">
                  Guardar Cambios
               </Button>
            </DialogFooter>
         </DialogContent>
      </Dialog>

    </div>
  );
}

function StatCard({ title, value, icon, description, highlight = false }: any) {
  return (
    <Card className={cn(
      "bg-slate-900 border-slate-800 shadow-xl relative overflow-hidden group",
      highlight && "ring-1 ring-brand-mint/30"
    )}>
       <CardContent className="pt-6">
          <div className="flex justify-between items-start mb-4">
             <div className="p-3 bg-slate-950 rounded-xl group-hover:scale-110 transition-transform">
                {icon}
             </div>
             {highlight && (
               <Badge className="bg-brand-mint/20 text-brand-mint border-none text-[10px] font-black">VIVO</Badge>
             )}
          </div>
          <div className="space-y-0.5">
             <p className="text-2xl font-black text-white tracking-tighter leading-none">{value}</p>
             <p className="text-xs font-bold text-slate-300 tracking-tight">{title}</p>
             <p className="text-[10px] text-slate-500 font-medium pt-2">{description}</p>
          </div>
       </CardContent>
    </Card>
  );
}
