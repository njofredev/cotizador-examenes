'use client';

import * as React from 'react';
import { 
  BarChart, 
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
  ChevronLeft,
  Download,
  Filter,
  PieChart as LucidePieChart,
  ChevronDown
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';

// Custom cn function 
function cn(...inputs: any[]) {
   return inputs.filter(Boolean).join(' ');
}

export default function AdminDashboard() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(false);
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [token, setToken] = React.useState('');
  const [activeTab, setActiveTab] = React.useState<'dashboard'|'pacientes'|'precios'|'reportes'|'exportar'>('dashboard');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isExporting, setIsExporting] = React.useState(false);
  
  // Data State
  const [stats, setStats] = React.useState<any>(null);
  const [history, setHistory] = React.useState<any[]>([]);
  const [examenes, setExamenes] = React.useState<Examen[]>([]);
  
  // Filters
  const [searchHistory, setSearchHistory] = React.useState('');
  const [previsionFilter, setPrevisionFilter] = React.useState('all');
  const [dateFilter, setDateFilter] = React.useState('all');
  const [searchExams, setSearchExams] = React.useState('');

  // Edit State
  const [editingExamen, setEditingExamen] = React.useState<Examen | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = React.useState(false);

  // Pagination for exams
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

  // --- LOGICA DE EXPORTACION ---
  
  const prepareExportData = () => {
    return history.map(h => ({
      Fecha: new Date(h.fecha_cotizacion).toLocaleDateString(),
      Folio: h.folio,
      Paciente: h.nombre_paciente,
      Documento: h.documento_id,
      Prevision: h.prevision,
      Total: h.total_copago
    }));
  };

  const exportToExcel = () => {
    const data = prepareExportData();
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Cotizaciones");
    XLSX.writeFile(wb, `Reporte_Tabancura_${new Date().toLocaleDateString()}.xlsx`);
    toast.success('Archivo Excel generado');
  };

  const exportToCSV = () => {
    const data = prepareExportData();
    const ws = XLSX.utils.json_to_sheet(data);
    const csv = XLSX.utils.sheet_to_csv(ws);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `Reporte_Tabancura_${new Date().toLocaleDateString()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Archivo CSV generado');
  };

  const exportToPDF = () => {
    const doc = new jsPDF() as any;
    
    // Add Brand Header
    doc.setFontSize(18);
    doc.setTextColor(22, 32, 91); // brand-dark
    doc.text("Policlínico Tabancura", 14, 20);
    doc.setFontSize(12);
    doc.setTextColor(100, 100, 100);
    doc.text("Reporte Administrativo Sistematizado", 14, 28);
    doc.text(`Generado: ${new Date().toLocaleString()}`, 14, 34);
    
    // Line separator
    doc.setDrawColor(25, 228, 162); // brand-mint
    doc.line(14, 38, 196, 38);

    const tableData = history.map(h => [
      new Date(h.fecha_cotizacion).toLocaleDateString(),
      h.folio,
      h.nombre_paciente,
      h.prevision,
      `$${(h.total_copago || 0).toLocaleString()}`
    ]);

    doc.autoTable({
      startY: 45,
      head: [['Fecha', 'Folio', 'Paciente', 'Previsión', 'Total']],
      body: tableData,
      headStyles: { fillColor: [22, 32, 91], textColor: [255, 255, 255] },
      alternateRowStyles: { fillColor: [240, 240, 240] },
    });

    doc.save(`Reporte_Tabancura_${new Date().toLocaleDateString()}.pdf`);
    toast.success('Documento PDF generado');
  };

  // --- FILTRADO ---
  
  const filteredHistory = history.filter(h => {
    const matchesSearch = h.nombre_paciente?.toLowerCase().includes(searchHistory.toLowerCase()) ||
                          h.documento_id?.includes(searchHistory) ||
                          h.folio?.includes(searchHistory);
    const matchesPrevision = previsionFilter === 'all' || h.prevision?.toLowerCase() === previsionFilter.toLowerCase();
    
    // Simple date filtering
    let matchesDate = true;
    if (dateFilter === 'today') {
       const today = new Date().toLocaleDateString();
       matchesDate = new Date(h.fecha_cotizacion).toLocaleDateString() === today;
    }
    
    return matchesSearch && matchesPrevision && matchesDate;
  });

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

  // --- UI COMPONENTS ---

  const COLORS = ['#19E4A2', '#3B82F6', '#F59E0B', '#10B981', '#6366F1'];

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
            <CardTitle className="text-2xl font-bold text-white px-2 tracking-tight">Acceso Administrativo</CardTitle>
            <CardDescription className="text-slate-400">Policlínico Tabancura / GESTIÓN</CardDescription>
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
              <Button type="submit" disabled={isLoading} className="w-full h-12 bg-brand-mint hover:bg-brand-mint/90 text-brand-dark font-bold text-sm uppercase tracking-widest mt-4">
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
    <div className="min-h-screen bg-[#090E1A] text-slate-200 selection:bg-brand-mint/30">
      <Toaster position="top-right" richColors />
      
      {/* HEADER CORPORATIVO MEJORADO */}
      <nav className="border-b border-white/5 bg-[#090E1A]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 pr-6 border-r border-white/10">
              <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center p-1.5 shadow-lg shadow-brand-mint/10">
                <img src="/logo_vec.svg" alt="Tabancura" className="w-full h-full object-contain" />
              </div>
              <div>
                <p className="text-lg font-bold text-white tracking-tight leading-none">
                   Policlínico <span className="text-white">Tabancura</span>
                </p>
                <p className="text-xs text-brand-mint font-bold uppercase tracking-[0.2em] mt-1 leading-none">/ ADMINISTRACIÓN</p>
              </div>
            </div>
            
            <div className="hidden lg:flex gap-1 pl-2">
              <NavButton active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} icon={<Activity className="w-4 h-4"/>}>Dashboard</NavButton>
              <NavButton active={activeTab === 'pacientes'} onClick={() => setActiveTab('pacientes')} icon={<Users className="w-4 h-4"/>}>Pacientes</NavButton>
              <NavButton active={activeTab === 'reportes'} onClick={() => setActiveTab('reportes')} icon={<BarChart className="w-4 h-4"/>}>Reportería</NavButton>
              <NavButton active={activeTab === 'precios'} onClick={() => setActiveTab('precios')} icon={<Database className="w-4 h-4"/>}>Precios</NavButton>
              <NavButton active={activeTab === 'exportar'} onClick={() => setActiveTab('exportar')} icon={<Download className="w-4 h-4"/>}>Exportar</NavButton>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:block text-right pr-4 border-r border-white/10">
               <p className="text-xs font-bold text-slate-400 uppercase tracking-tight">Bienvenido,</p>
               <p className="text-sm font-bold text-white tracking-tight">Administrador Central</p>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 gap-2 transition-all group">
              <LogOut className="h-4 w-4 group-hover:rotate-180 transition-transform duration-500" /> <span className="hidden sm:inline font-bold">Cerrar Sesión</span>
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-1000">
        
        {/* --- TAB DASHBOARD --- */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-4xl font-bold text-white tracking-tight">Resumen Global</h1>
                <p className="text-slate-400 font-medium">Estado actual del flujo de atención clínica.</p>
              </div>
              <div className="flex gap-2">
                 <Button onClick={() => loadDashboardData(token)} disabled={isLoading} variant="outline" size="sm" className="border-white/10 bg-white/5 text-slate-300 text-xs font-bold">
                    <TrendingUp className="w-3 h-3 mr-2" /> Actualizar Datos
                 </Button>
              </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard title="Cotizaciones" value={stats?.total_cotizaciones || 0} icon={<Activity />} sub="Histórico" color="emerald" />
              <StatCard title="Actividad Hoy" value={stats?.total_hoy || 0} icon={<Calendar />} sub="Cotizaciones" color="blue" highlight />
              <StatCard title="Ingresos Fonasa" value={`$${(stats?.monto_fonasa || 0).toLocaleString()}`} icon={<DollarSign />} sub="Copagos reales" color="amber" />
              <StatCard title="Ingresos Part." value={`$${(stats?.monto_particular || 0).toLocaleString()}`} icon={<TrendingUp />} sub="Particular Gral." color="purple" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Gráfico de Tendencia */}
              <Card className="lg:col-span-2 bg-[#121927] border-white/5 shadow-2xl overflow-hidden group">
                 <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                       <CardTitle className="text-white font-bold tracking-tight">Tendencia de Uso</CardTitle>
                       <CardDescription className="text-slate-500 text-xs">Cotizaciones diarias (Últimos 15 días)</CardDescription>
                    </div>
                    <BarChart className="text-brand-mint w-5 h-5 opacity-50" />
                 </CardHeader>
                 <CardContent className="h-64 pt-4">
                    <ResponsiveContainer width="100%" height="100%">
                       <AreaChart data={stats?.trend_data || []}>
                          <defs>
                             <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#19E4A2" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="#19E4A2" stopOpacity={0}/>
                             </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                          <XAxis dataKey="fecha" stroke="#ffffff40" fontSize={10} tickLine={false} axisLine={false} />
                          <YAxis stroke="#ffffff40" fontSize={10} tickLine={false} axisLine={false} />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#090e1a', border: '1px solid #ffffff10', borderRadius: '12px', fontSize: '12px' }}
                            itemStyle={{ color: '#19E4A2' }}
                          />
                          <Area type="monotone" dataKey="cantidad" stroke="#19E4A2" strokeWidth={3} fillOpacity={1} fill="url(#colorTrend)" />
                       </AreaChart>
                    </ResponsiveContainer>
                 </CardContent>
              </Card>

              {/* Top Examenes Pie */}
              <Card className="lg:col-span-1 bg-[#121927] border-white/5 shadow-2xl">
                 <CardHeader>
                    <CardTitle className="text-white font-bold tracking-tight">Distribución</CardTitle>
                    <CardDescription className="text-slate-500 text-xs">Exámenes más demandados</CardDescription>
                 </CardHeader>
                 <CardContent className="h-64 flex items-center justify-center pt-8">
                    <ResponsiveContainer width="100%" height="100%">
                       <PieChart>
                          <Pie
                            data={stats?.top_examenes || []}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="cantidad"
                            nameKey="nombre"
                          >
                             {stats?.top_examenes.map((entry: any, index: number) => (
                               <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                             ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#090e1a', border: '1px solid #ffffff10', borderRadius: '12px', fontSize: '10px' }}
                          />
                       </PieChart>
                    </ResponsiveContainer>
                 </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* --- TAB PACIENTES (FILTROS MEJORADOS) --- */}
        {activeTab === 'pacientes' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-4xl font-bold text-white tracking-tight">Historial de Pacientes</h1>
                <p className="text-slate-400 font-medium">Búsqueda y gestión de folios generados.</p>
              </div>
              
              <div className="flex flex-wrap gap-3 w-full md:w-auto">
                 <div className="relative flex-1 md:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <Input 
                      placeholder="Nombre, RUT o Folio..." 
                      value={searchHistory}
                      onChange={(e) => setSearchHistory(e.target.value)}
                      className="bg-[#121927] border-white/10 pl-10 h-10 text-white"
                    />
                 </div>
                 <Select value={previsionFilter} onValueChange={(v) => v && setPrevisionFilter(v)}>
                    <SelectTrigger className="w-32 bg-[#121927] border-white/10 text-white h-10">
                       <SelectValue placeholder="Previsión" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#090e1a] border-white/10 text-white">
                       <SelectItem value="all">Todas</SelectItem>
                       <SelectItem value="fonasa">Fonasa</SelectItem>
                       <SelectItem value="particular">Particular</SelectItem>
                    </SelectContent>
                 </Select>
                 <Select value={dateFilter} onValueChange={(v) => v && setDateFilter(v)}>
                    <SelectTrigger className="w-32 bg-[#121927] border-white/10 text-white h-10">
                       <SelectValue placeholder="Fecha" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#090e1a] border-white/10 text-white">
                       <SelectItem value="all">Siempre</SelectItem>
                       <SelectItem value="today">Hoy</SelectItem>
                    </SelectContent>
                 </Select>
              </div>
            </div>

            <Card className="bg-[#121927] border-white/5 shadow-2xl overflow-hidden ring-1 ring-white/5">
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                    <thead className="bg-[#090e1a] border-b border-white/5">
                      <tr>
                        <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Paciente</th>
                        <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Folio</th>
                        <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Previsión</th>
                        <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Fecha</th>
                        <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400 text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {filteredHistory.length > 0 ? filteredHistory.map((row, idx) => (
                        <tr key={idx} className="hover:bg-white/[0.02] transition-colors group">
                          <td className="px-6 py-5">
                            <p className="text-sm font-bold text-white">{row.nombre_paciente}</p>
                            <p className="text-[10px] font-bold text-slate-500 tracking-tight uppercase">{row.documento_id}</p>
                          </td>
                          <td className="px-6 py-5">
                            <Badge className="bg-brand-mint/10 text-brand-mint border-brand-mint/20 font-bold px-2 py-0.5">{row.folio}</Badge>
                          </td>
                          <td className="px-6 py-5 text-sm font-bold text-slate-300">
                             {row.prevision}
                          </td>
                          <td className="px-6 py-5 text-xs text-slate-500 font-bold uppercase">
                            {new Date(row.fecha_cotizacion).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-5 text-right">
                             <p className="text-sm font-bold text-brand-mint">
                               ${(row.total_copago || 0).toLocaleString()}
                             </p>
                          </td>
                        </tr>
                      )) : (
                        <tr>
                           <td colSpan={5} className="py-20 text-center space-y-4">
                              <Users className="w-12 h-12 text-white/10 mx-auto" />
                              <p className="text-slate-500 font-bold">No se encontraron pacientes registrados con estos filtros.</p>
                           </td>
                        </tr>
                      )}
                    </tbody>
                 </table>
               </div>
            </Card>
          </div>
        )}

        {/* --- TAB REPORTERIA (ADICIONAL) --- */}
        {activeTab === 'reportes' && (
           <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-700">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                  <h1 className="text-4xl font-bold text-white tracking-tight">Reportería Avanzada</h1>
                  <p className="text-slate-400 font-medium">Análisis detallado de la demanda y rentabilidad.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                 <Card className="bg-[#121927] border-white/5 shadow-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                       <LucidePieChart className="text-brand-mint w-5 h-5"/> Mix de Seguros
                    </h3>
                    <div className="h-64">
                       <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                             <Pie
                                data={[
                                   { name: 'Fonasa', value: stats?.monto_fonasa },
                                   { name: 'Particular', value: stats?.monto_particular }
                                ]}
                                cx="50%" cy="50%" innerRadius={40} outerRadius={100} paddingAngle={2} dataKey="value"
                             >
                                <Cell fill="#19E4A2" />
                                <Cell fill="#3B82F6" />
                             </Pie>
                             <Tooltip />
                          </PieChart>
                       </ResponsiveContainer>
                    </div>
                    <div className="flex justify-center gap-8 mt-4">
                       <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-brand-mint" />
                          <span className="text-xs font-bold text-slate-400">Fonasa</span>
                       </div>
                       <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-blue-500" />
                          <span className="text-xs font-bold text-slate-400">Particular</span>
                       </div>
                    </div>
                 </Card>

                 <Card className="bg-[#121927] border-white/5 shadow-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-6">Resumen Ejecutivo</h3>
                    <div className="space-y-6">
                       <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                          <p className="text-xs font-bold text-slate-500 uppercase mb-1">Volumen Promedio Diario</p>
                          <p className="text-2xl font-bold text-white">{(stats?.total_cotizaciones / 30).toFixed(1)} <span className="text-xs text-slate-500">cots/día</span></p>
                       </div>
                       <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                          <p className="text-xs font-bold text-slate-500 uppercase mb-1">Examen más solicitado</p>
                          <p className="text-xl font-bold text-brand-mint tracking-tight">{stats?.top_examenes[0]?.nombre || 'N/A'}</p>
                       </div>
                       <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                          <p className="text-xs font-bold text-slate-500 uppercase mb-1">Ticket Promedio</p>
                          <p className="text-2xl font-bold text-blue-400">${((stats?.monto_fonasa + stats?.monto_particular) / stats?.total_cotizaciones || 0).toLocaleString()}</p>
                       </div>
                    </div>
                 </Card>
              </div>
           </div>
        )}

        {/* --- TAB EXPORTAR --- */}
        {activeTab === 'exportar' && (
           <div className="max-w-4xl mx-auto space-y-8 animate-in zoom-in-95 duration-500">
              <div className="text-center space-y-2">
                 <h1 className="text-4xl font-bold text-white tracking-tight">Centro de Descargas</h1>
                 <p className="text-slate-400">Exporta la información para auditorías o reportes externos.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
                 <ExportCard 
                   title="Exportar CSV" 
                   desc="Ideal para importar en bases de datos." 
                   icon={<Database className="w-8 h-8"/>} 
                   onClick={exportToCSV}
                 />
                 <ExportCard 
                   title="Exportar Excel" 
                   desc="Formato nativo para análisis financiero." 
                   icon={<Download className="w-8 h-8"/>} 
                   onClick={exportToExcel}
                   color="emerald"
                 />
                 <ExportCard 
                   title="Exportar PDF" 
                   desc="Reporte listo para impresión oficial." 
                   icon={<Download className="w-8 h-8"/>} 
                   onClick={exportToPDF}
                   color="rose"
                 />
              </div>

              <div className="bg-[#121927] p-8 rounded-3xl border border-white/5 mt-12 text-center text-slate-500 text-xs leading-relaxed max-w-2xl mx-auto">
                 <p>Nota: Las descargas incluyen todo el historial disponible en el servidor (hasta 100 registros recientes). Asegúrate de realizar respaldos periódicos de la información administrativa.</p>
              </div>
           </div>
        )}

        {/* --- TAB PRECIOS --- */}
        {activeTab === 'precios' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
               <div>
                  <h1 className="text-4xl font-bold text-white tracking-tight">Maestro de Aranceles</h1>
                  <p className="text-slate-400 font-medium">Actualización masiva de precios del catálogo.</p>
               </div>
               <div className="w-full md:w-64 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <Input 
                    placeholder="Filtrar por nombre o código..." 
                    value={searchExams}
                    onChange={(e) => {setSearchExams(e.target.value); setExamPage(1);}}
                    className="bg-[#121927] border-white/10 pl-10 h-10 text-white"
                  />
               </div>
            </div>

            <Card className="bg-[#121927] border-white/5 shadow-2xl overflow-hidden ring-1 ring-white/5">
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                    <thead className="bg-[#090e1a] border-b border-white/5 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                       <tr>
                         <th className="px-6 py-4">Cod / Examen</th>
                         <th className="px-6 py-4">Fonasa / Copago</th>
                         <th className="px-6 py-4">Part. Gral / Pref</th>
                         <th className="px-6 py-4 text-right">Acción</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                       {paginatedExams.map((ex, idx) => (
                          <tr key={idx} className="hover:bg-white/[0.02] transition-colors group">
                             <td className="px-6 py-5 max-w-sm">
                                <p className="text-[10px] font-bold text-slate-500 tracking-widest">{ex.codigo}</p>
                                <p className="text-sm font-bold text-white leading-tight group-hover:text-brand-mint transition-colors cursor-default">{ex.nombre}</p>
                             </td>
                             <td className="px-6 py-5">
                                <div className="space-y-1">
                                   <div className="flex items-center gap-2">
                                      <span className="text-[10px] bg-blue-500/10 text-blue-400 font-bold px-1 rounded">F</span>
                                      <span className="text-sm font-bold text-white">${ex.valor_bono_fonasa.toLocaleString()}</span>
                                   </div>
                                   <div className="flex items-center gap-2">
                                      <span className="text-[10px] bg-brand-mint/10 text-brand-mint font-bold px-1 rounded">C</span>
                                      <span className="text-sm font-bold text-brand-mint">${ex.valor_copago.toLocaleString()}</span>
                                   </div>
                                </div>
                             </td>
                             <td className="px-6 py-5">
                                <div className="space-y-1">
                                   <div className="flex items-center gap-2">
                                      <span className="text-[10px] bg-white/5 text-slate-400 font-bold px-1 rounded">G</span>
                                      <span className="text-sm font-bold text-slate-300">${ex.valor_particular_general.toLocaleString()}</span>
                                   </div>
                                   <div className="flex items-center gap-2">
                                      <span className="text-[10px] bg-brand-mint/5 text-brand-mint font-bold px-1 rounded">P</span>
                                      <span className="text-sm font-bold text-brand-mint">${(ex.valor_particular_preferencial).toLocaleString()}</span>
                                   </div>
                                </div>
                             </td>
                             <td className="px-6 py-5 text-right">
                                <Button 
                                  variant="ghost" 
                                  size="icon" 
                                  className="text-slate-500 hover:text-brand-mint hover:bg-brand-mint/10 opacity-0 group-hover:opacity-100 transition-all rounded-full"
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
               
               <div className="bg-[#090e1a] border-t border-white/5 p-4 flex items-center justify-between">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest px-4">Página {examPage} de {totalExamPages}</p>
                  <div className="flex gap-2 pr-4">
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={() => setExamPage(p => Math.max(1, p-1))} 
                      disabled={examPage === 1}
                      className="bg-[#121927] border-white/10 h-8 w-8 text-white rounded-lg hover:bg-brand-mint hover:text-brand-dark transition-colors"
                    >
                       <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={() => setExamPage(p => Math.min(totalExamPages, p+1))} 
                      disabled={examPage === totalExamPages}
                      className="bg-[#121927] border-white/10 h-8 w-8 text-white rounded-lg hover:bg-brand-mint hover:text-brand-dark transition-colors"
                    >
                       <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
               </div>
            </Card>
          </div>
        )}

      </main>

      {/* --- MODAL EDITAR MEJORADO --- */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
         <DialogContent className="bg-[#090e1a] border-white/10 text-white max-w-sm rounded-[32px] p-0 overflow-hidden ring-1 ring-brand-mint/20">
            <div className="bg-brand-mint/5 p-8 pb-4">
               <DialogHeader>
                  <DialogTitle className="text-2xl font-bold tracking-tight">Editar Arancel</DialogTitle>
                  <DialogDescription className="text-slate-400 pt-2 font-medium">
                     Estás actualizando la base de datos oficial para: <br/>
                     <span className="text-brand-mint font-bold text-sm uppercase tracking-tight block mt-2">{editingExamen?.nombre}</span>
                  </DialogDescription>
               </DialogHeader>
            </div>
            
            <div className="p-8 space-y-4">
               <div className="grid grid-cols-2 gap-4">
                  <PriceInput label="Valor Fonasa" value={editingExamen?.valor_bono_fonasa} onChange={(v: number) => setEditingExamen(p => p ? {...p, valor_bono_fonasa: v}:null)} />
                  <PriceInput label="Valor Copago" value={editingExamen?.valor_copago} onChange={(v: number) => setEditingExamen(p => p ? {...p, valor_copago: v}:null)} />
                  <PriceInput label="Part. General" value={editingExamen?.valor_particular_general} onChange={(v: number) => setEditingExamen(p => p ? {...p, valor_particular_general: v}:null)} />
                  <PriceInput label="Part. Preferencial" value={editingExamen?.valor_particular_preferencial} onChange={(v: number) => setEditingExamen(p => p ? {...p, valor_particular_preferencial: v}:null)} />
               </div>
            </div>

            <div className="bg-white/[0.02] p-6 flex gap-3 justify-end border-t border-white/5">
                <Button variant="ghost" onClick={() => setIsEditModalOpen(false)} className="text-slate-400 font-bold hover:text-white">Descartar</Button>
                <Button onClick={handleUpdatePrice} disabled={isLoading} className="bg-brand-mint hover:bg-brand-mint/90 text-brand-dark font-bold px-6 rounded-xl transition-all">
                   {isLoading ? 'Guardando...' : 'Aplicar Cambios'}
                </Button>
            </div>
         </DialogContent>
      </Dialog>
    </div>
  );
}

function NavButton({ children, active, onClick, icon }: any) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-widest flex items-center gap-2 transition-all duration-300",
        active 
          ? "bg-brand-mint text-brand-dark shadow-lg shadow-brand-mint/20" 
          : "text-slate-400 hover:text-white hover:bg-white/5"
      )}
    >
      {icon}
      {children}
    </button>
  );
}

function StatCard({ title, value, icon, sub, color, highlight }: any) {
  const colorMap: any = {
    emerald: "text-emerald-400 bg-emerald-400/10",
    blue: "text-blue-400 bg-blue-400/10",
    amber: "text-amber-400 bg-amber-400/10",
    purple: "text-purple-400 bg-purple-400/10",
  };

  return (
    <Card className={cn(
      "bg-[#121927] border-white/5 relative overflow-hidden group transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl hover:bg-[#1a2335]",
      highlight && "ring-1 ring-brand-mint/30"
    )}>
       <CardContent className="pt-6">
          <div className="flex justify-between items-start mb-6">
             <div className={cn("p-4 rounded-2xl group-hover:scale-110 transition-transform duration-500", colorMap[color])}>
                {React.cloneElement(icon, { size: 24 })}
             </div>
             {highlight && (
               <Badge className="bg-brand-mint/20 text-brand-mint border-none text-[8px] font-bold tracking-widest">EN VIVO</Badge>
             )}
          </div>
          <div>
             <p className="text-3xl font-bold text-white tracking-tight mb-0.5">{value}</p>
             <p className="text-xs font-bold text-slate-300 uppercase tracking-widest">{title}</p>
             <p className="text-[10px] text-slate-500 font-bold mt-2 uppercase tracking-tight">{sub}</p>
          </div>
       </CardContent>
    </Card>
  );
}

function PriceInput({ label, value, onChange }: any) {
  return (
    <div className="space-y-1.5">
       <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider pl-1">{label}</p>
       <Input 
         type="number" 
         value={value || 0}
         onChange={(e) => onChange(parseInt(e.target.value))}
         className="bg-white/5 border-white/10 text-white h-11 rounded-xl focus:ring-brand-mint/30 focus:border-brand-mint/30 transition-all font-bold"
       />
    </div>
  );
}

function ExportCard({ title, desc, icon, onClick, color = "mint" }: any) {
  const colorMap: any = {
    mint: "text-brand-mint bg-brand-mint/10 group-hover:bg-brand-mint/20",
    emerald: "text-emerald-400 bg-emerald-400/10 group-hover:bg-emerald-400/20",
    rose: "text-rose-400 bg-rose-400/10 group-hover:bg-rose-400/20",
  };

  return (
    <button onClick={onClick} className="group text-left">
       <Card className="bg-[#121927] border-white/5 h-full transition-all duration-500 hover:border-white/10 hover:translate-y-[-4px] overflow-hidden">
          <CardContent className="pt-8 pb-8 flex flex-col items-center text-center">
             <div className={cn("w-20 h-20 rounded-[2rem] flex items-center justify-center mb-6 transition-all duration-500", colorMap[color])}>
                {icon}
             </div>
             <p className="text-xl font-bold text-white mb-2">{title}</p>
             <p className="text-xs text-slate-500 font-medium px-4">{desc}</p>
          </CardContent>
       </Card>
    </button>
  );
}
