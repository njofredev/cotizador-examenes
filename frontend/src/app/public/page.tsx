'use client';

import * as React from 'react';
import {
  Activity,
  Search,
  Trash2,
  Download,
  MapPin,
  Globe,
  Calendar,
  ChevronRight,
  RefreshCw,
  Info,
  CheckCircle2,
  PlusCircle,
  Stethoscope,
  Heart,
  Plus,
  Minus,
  FileDown,
  ShieldCheck
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { toast, Toaster } from 'sonner';
import { Badge } from '../../components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from '../../components/ui/tooltip';
import { Separator } from '../../components/ui/separator';

import { ExamSearch } from '../../components/cotizador/examen-search';
import { PacketCard } from '../../components/cotizador/packet-card';
import { CotizacionTable } from '../../components/cotizador/cotizacion-table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '../../components/ui/dialog';

import { getExamenes, getPaquetes, postCotizar, API_URL, Examen, Paquete } from '../../lib/api';

export default function GuestPage() {
  const [mounted, setMounted] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [examenes, setExamenes] = React.useState<Examen[]>([]);
  const [paquetes, setPaquetes] = React.useState<Paquete[]>([]);
  const [selectedExams, setSelectedExams] = React.useState<{ examen: Examen, cantidad: number }[]>([]);
  const [packActivo, setPackActivo] = React.useState<string | null>(null);
  const [prevision, setPrevision] = React.useState('');
  const [pdfUrl, setPdfUrl] = React.useState<string | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = React.useState(false);

  const [currentStep, setCurrentStep] = React.useState(1); // 1: Info, 2: Search, 3: Results
  const [isSearching, setIsSearching] = React.useState(false);

  // Guest Defaults
  const GUEST_DATA = {
    nombre: 'Público General',
    docId: '1-9',
    fechaNac: '1990-01-01',
    prevision: 'Particular'
  };

  const resultsSectionRef = React.useRef<HTMLDivElement>(null);
  const searchSectionRef = React.useRef<HTMLElement>(null);

  React.useEffect(() => {
    setMounted(true);
    async function init() {
      try {
        const [examRes, packRes] = await Promise.all([getExamenes(), getPaquetes()]);
        setExamenes(examRes.data);
        setPaquetes(packRes.data);
      } catch (err) {
        toast.error('Error al cargar datos del servidor');
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const DEFAULT_QUANTITIES: Record<string, number> = {
    '302032': 3, // Electrolitos plasmáticos
    '309012': 3, // Electrolitos orina
    '302063': 2, // Transaminasas
    '305027': 3, // Inmunoglobulinas
    '305105': 2, // Beta 2 glicoproteina
    '305084': 2, // Anticardiolipinas
    '305170': 3, // Antígeno Ca 125, 15-3, 19-9
    '306013': 2, // Bordetella
    '306037': 2, // Mycoplasma
    '306041': 2, // Treponema
    '302039': 3, // Fosfatasas isoenzimas
    '305108': 6, // A-ENA
    '305081': 3, // Antiendomisio
    '301025': 7  // Factores coagulación
  };

  const handleSelectExamen = (examen: Examen) => {
    if (packActivo) {
      toast.warning('No puedes agregar exámenes individuales a un paquete cerrado');
      return;
    }
    if (selectedExams.find(i => i.examen.codigo === examen.codigo)) {
      toast.info('El examen ya está en la lista');
      return;
    }
    const initialCantidad = DEFAULT_QUANTITIES[examen.codigo] || 1;
    setSelectedExams(prev => [...prev, { examen, cantidad: initialCantidad }]);
    toast.success(`${examen.nombre} añadido`);
  };

  const handleSelectPaquete = (paquete: Paquete) => {
    const newExams = paquete.examenes.map(p_ex => {
      const fullEx = examenes.find(e => e.codigo === p_ex.codigo);
      return fullEx ? { examen: fullEx, cantidad: p_ex.cantidad } : null;
    }).filter(Boolean) as { examen: Examen, cantidad: number }[];

    setSelectedExams(newExams);
    setPackActivo(paquete.nombre);
    toast.success(`Paquete "${paquete.nombre}" aplicado`);

    setTimeout(() => {
      resultsSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
  };

  const updateCantidad = (codigo: string, cantidad: number) => {
    setSelectedExams(prev => prev.map(item =>
      item.examen.codigo === codigo ? { ...item, cantidad } : item
    ));
  };

  const removeExamen = (codigo: string) => {
    setSelectedExams(prev => prev.filter(i => i.examen.codigo !== codigo));
    if (packActivo) setPackActivo(null);
  };

  const handleGenerarPDF = async () => {
    if (selectedExams.length === 0) {
      toast.error('Selecciona al menos un examen');
      return;
    }
    if (!prevision) {
      toast.error('Selecciona tu previsión (Particular o Fonasa)');
      return;
    }

    setIsGenerating(true);
    try {
      const payload = {
        nombre_paciente: GUEST_DATA.nombre,
        fecha_nacimiento: GUEST_DATA.fechaNac,
        tipo_documento: 'Genérico',
        documento_id: GUEST_DATA.docId,
        prevision: prevision,
        pack_activo: packActivo,
        examenes: selectedExams.map(i => ({
          codigo: i.examen.codigo,
          nombre: i.examen.nombre,
          cantidad: i.cantidad,
          valor_bono_fonasa: i.examen.valor_bono_fonasa,
          valor_copago: i.examen.valor_copago,
          valor_particular_general: i.examen.valor_particular_general,
          valor_particular_preferencial: i.examen.valor_particular_preferencial
        }))
      };
      const res = await postCotizar(payload);
      if (res.data.success) {
        setPdfUrl(res.data.pdf_url);
        toast.success('¡Cotización generada con éxito!');
        setIsSuccessModalOpen(true);
      }
    } catch (error) {
      toast.error('Error al generar la cotización');
    } finally {
      setIsGenerating(false);
    }
  };

  const reset = () => {
    setSelectedExams([]);
    setPackActivo(null);
    setPrevision('Particular');
    setPdfUrl(null);
    // Focus back to search section
    if (searchSectionRef.current) {
      searchSectionRef.current.scrollIntoView({ behavior: 'auto', block: 'start' });
    } else {
      window.scrollTo({ top: 0, behavior: 'auto' });
    }
    toast.info('Limpieza completa');
  };

  const isFonasa = prevision === 'Fonasa';
  const totalV1 = selectedExams.reduce((acc, item) => acc + (isFonasa ? item.examen.valor_bono_fonasa : item.examen.valor_particular_general) * item.cantidad, 0);
  const totalV2 = selectedExams.reduce((acc, item) => {
    const val = isFonasa ? (item.examen.valor_bono_fonasa > 0 ? item.examen.valor_copago : item.examen.valor_particular_general) : item.examen.valor_particular_preferencial;
    return acc + val * item.cantidad;
  }, 0);

  if (!mounted) return null;

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-[#F8FAFC] pb-48 md:pb-12">
        <Toaster position="top-center" richColors />

        {/* MOBILE STEP INDICATOR */}
        <div className="md:hidden pt-4 px-4">
          <div className="flex items-center justify-between gap-2 max-w-sm mx-auto bg-slate-50 p-1.5 rounded-2xl border border-slate-100">
            {[
              { step: 1, label: 'Previsión', icon: ShieldCheck },
              { step: 2, label: 'Selecciona', icon: Search },
              { step: 3, label: 'Cotización', icon: Activity }
            ].map((s) => (
              <button
                key={s.step}
                onClick={() => {
                  if (s.step === 2 && !prevision) {
                    toast.error("Selecciona tu previsión para continuar");
                    return;
                  }
                  if (s.step === 3 && selectedExams.length === 0) {
                    toast.info("Selecciona al menos un examen");
                    return;
                  }
                  if (s.step === 3 && !prevision) {
                    toast.error("Selecciona tu previsión");
                    setCurrentStep(1);
                    return;
                  }
                  setCurrentStep(s.step);
                }}
                className={cn(
                  "flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl transition-all duration-300",
                  currentStep === s.step 
                    ? "bg-brand-dark text-white shadow-lg shadow-brand-dark/20" 
                    : "text-slate-400 hover:bg-slate-100"
                )}
              >
                <s.icon className={cn("h-3.5 w-3.5", currentStep === s.step ? "text-brand-mint" : "text-slate-300")} />
                <span className="text-[9px] font-black uppercase tracking-tighter">{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        <main className="container max-w-6xl mx-auto px-4 pt-8 md:pt-12 grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column */}
          <div className="lg:col-span-2 space-y-10">

            {/* Section: Individual Search */}
            <section ref={searchSectionRef} className={cn(
              "space-y-6",
              currentStep !== 2 && "hidden md:block"
            )}>
              <div className="flex items-center gap-3">
                <div className="bg-brand-mint/10 p-2 rounded-xl">
                  <Search className="h-6 w-6 text-brand-mint" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Buscar exámenes</h1>
                  <p className="text-slate-500 text-sm">Añadir servicios uno a uno</p>
                </div>
              </div>

              <ExamSearch
                examenes={examenes}
                onSelect={handleSelectExamen}
                onSearchChange={setIsSearching}
                disabled={loading || !!packActivo}
                placeholder="Busca por nombre o código (Ej: 301041, Hemograma, Glucosa...)"
              />
            </section>

            {/* Section: Packages - Hide if individual exams are selected (and not part of a pack) */}
            {(selectedExams.length === 0 || !!packActivo) && !isSearching && (
              <section className={cn(
                "space-y-6 animate-in fade-in slide-in-from-top-4 duration-700",
                currentStep !== 2 && "hidden md:block" // Also hide packages if not in step 2 on mobile
              )}>
                <div className="flex items-center gap-3 border-t border-slate-100 pt-10">
                  <div className="bg-brand-mint/10 p-2 rounded-xl">
                    <Activity className="h-6 w-6 text-brand-mint" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-800">Paquetes de Chequeo Preventivo</h2>
                    <p className="text-slate-500 text-sm">Optimiza tu salud con grupos de exámenes especializados</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {paquetes.map(p => (
                    <PacketCard
                      key={p.nombre}
                      paquete={p}
                      active={packActivo === p.nombre}
                      onSelect={handleSelectPaquete}
                    />
                  ))}
                </div>
              </section>
            )}

            {/* Selection Table */}
            {selectedExams.length > 0 && (
              <div ref={resultsSectionRef} className={cn(
                "pt-8 space-y-4 animate-in slide-in-from-bottom-5 duration-700",
                currentStep !== 3 && "hidden md:block"
              )}>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-brand-mint" />
                    Exámenes seleccionados
                  </h2>
                  <div className="flex items-center gap-3">
                    <Badge className="bg-brand-dark hover:bg-brand-dark/90 text-brand-mint font-black h-8 px-3 rounded-full border-none">
                      {selectedExams.reduce((acc, curr) => acc + curr.cantidad, 0)} ítems
                    </Badge>
                    <Button
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        reset();
                      }}
                      className="h-8 px-2 text-destructive hover:text-destructive hover:bg-destructive/10 flex items-center gap-1.5 cursor-pointer relative z-50 group"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      <span className="text-[10px] font-bold uppercase tracking-wider">Limpiar</span>
                    </Button>
                  </div>
                </div>
                <CotizacionTable
                  items={selectedExams}
                  prevision={prevision}
                  onUpdateCantidad={updateCantidad}
                  onRemove={removeExamen}
                  isPackActive={!!packActivo}
                />

                {/* Mobile Extra Summary Card - Only visible on Step 3 Mobile */}
                <div className="lg:hidden mt-8 pt-4 border-t border-slate-100">
                  <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm space-y-6">
                    <div className="text-center">
                      <h3 className="text-xl font-bold text-slate-800 tracking-tight">Resumen Final</h3>
                      <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mt-1">Cotización lista para descargar</p>
                    </div>
                    <div className="flex justify-between items-center py-3 border-b border-white">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{isFonasa ? 'Bono Fonasa' : 'P. Gral'}</span>
                      <span className="text-base font-bold text-slate-600">${totalV1.toLocaleString('es-CL')}</span>
                    </div>
                    <div className="flex justify-between items-center bg-brand-mint/5 p-4 rounded-2xl border border-brand-mint/10">
                      <div>
                        <span className="text-[9px] font-black text-brand-mint uppercase tracking-tighter">{isFonasa ? 'Total Copago' : 'Total a Pagar'}</span>
                        <p className="text-[10px] text-slate-500 font-bold leading-none mt-1">{isFonasa ? 'Bono Fonasa' : 'Convenio MiVita'}</p>
                      </div>
                      <span className="text-2xl font-black text-brand-dark">${totalV2.toLocaleString('es-CL')}</span>
                    </div>
                    <Button
                      onClick={handleGenerarPDF}
                      disabled={selectedExams.length === 0 || isGenerating}
                      className="w-full h-14 bg-emerald-500 hover:bg-emerald-600 text-white rounded-2xl font-black uppercase tracking-tight shadow-lg shadow-emerald-100 border-b-4 border-emerald-700 transition-all active:scale-95"
                    >
                      {isGenerating ? <RefreshCw className="h-5 w-5 animate-spin" /> : <Download className="h-5 w-5 mr-3" />}
                      {isGenerating ? 'Generando...' : 'Descargar PDF'}
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className={cn(
            "space-y-6 lg:sticky lg:top-12 h-fit",
            currentStep !== 1 && "hidden lg:block" // Step 1 on mobile shows the total/summary start
          )}>
            {/* Header for Step 1 on Mobile */}
            <div className="md:hidden space-y-2 mb-6">
              <div className="flex items-center gap-3">
                <div className="bg-brand-mint/10 p-2 rounded-xl">
                  <ShieldCheck className="h-6 w-6 text-brand-mint" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Tipo de Previsión</h1>
                  <p className="text-slate-500 text-sm">Selecciona una de las dos previsiones para acceder a la selección de exámenes.</p>
                </div>
              </div>
            </div>

            <div className="flex bg-slate-100 p-1.5 rounded-2xl w-full border border-slate-200">
              <Button
                variant="ghost"
                className={cn(
                  "flex-1 h-12 text-[10px] font-black tracking-widest rounded-xl transition-all duration-300",
                  prevision === 'Particular'
                    ? "bg-brand-dark text-brand-mint shadow-lg shadow-brand-dark/20"
                    : "text-slate-400 hover:text-slate-600"
                )}
                onClick={() => {
                  setPrevision('Particular');
                  setCurrentStep(2);
                }}
              >
                PARTICULAR
              </Button>
              <Button
                variant="ghost"
                className={cn(
                  "flex-1 h-12 text-[10px] font-black tracking-widest rounded-xl transition-all duration-300",
                  prevision === 'Fonasa'
                    ? "bg-brand-dark text-brand-mint shadow-lg shadow-brand-dark/20"
                    : "text-slate-400 hover:text-slate-600"
                )}
                onClick={() => {
                  setPrevision('Fonasa');
                  setCurrentStep(2);
                }}
              >
                FONASA
              </Button>
            </div>

            <Card className={cn(
              "border-none shadow-xl shadow-slate-200/50 overflow-hidden bg-white/80 backdrop-blur-sm",
              currentStep === 1 && "hidden lg:block" // Hide on mobile Step 1
            )}>
              <CardContent className="p-8 space-y-8">
                <div className="space-y-2 text-center lg:text-left">
                  <h3 className="text-2xl font-bold text-slate-800">Total cotización</h3>
                  <p className="text-slate-400 text-sm">Desglose según tu previsión ({prevision})</p>
                </div>

                <div className="space-y-6">
                  <div className="flex justify-between items-center py-4 border-b border-slate-50">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                      {isFonasa ? 'Valor Bono Fonasa' : 'Total Particular General'}
                    </span>
                    <span className="text-xl font-bold text-slate-700">${totalV1.toLocaleString('es-CL')}</span>
                  </div>
                  <div className="flex justify-between items-center bg-slate-50/50 p-4 rounded-2xl">
                    <div>
                      <span className="text-[10px] font-black text-brand-mint uppercase tracking-tighter">
                        {isFonasa ? 'Total Copago' : 'Total a Pagar'}
                      </span>
                      <p className="text-xs text-slate-400 font-medium">{isFonasa ? 'A pagar en sucursal' : 'Precio Preferencial'}</p>
                    </div>
                    <span className="text-3xl font-black text-brand-dark">${totalV2.toLocaleString('es-CL')}</span>
                  </div>
                </div>

                <div className="space-y-4 pt-4">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="w-full">
                        <Button
                          onClick={handleGenerarPDF}
                          disabled={selectedExams.length === 0 || !prevision || isGenerating}
                          className={cn(
                            "w-full h-14 rounded-2xl text-base font-bold transition-all duration-300 shadow-xl",
                            (selectedExams.length === 0 || !prevision)
                              ? "bg-amber-100 text-amber-900/40 border-b-4 border-amber-200 opacity-60 cursor-not-allowed"
                              : "bg-emerald-500 hover:bg-emerald-600 text-white border-b-4 border-emerald-700 shadow-emerald-200/50 scale-[1.02]"
                          )}
                        >
                          {isGenerating ? (
                            <RefreshCw className="h-5 w-5 animate-spin mr-2" />
                          ) : (
                            <Download className="h-5 w-5 mr-2" />
                          )}
                          {isGenerating ? 'GENERANDO...' : 'GENERAR COTIZACIÓN (PDF)'}
                        </Button>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top">
                      {!prevision
                        ? "Primero selecciona tu previsión arriba"
                        : selectedExams.length === 0
                          ? "Agrega exámenes para generar la cotización"
                          : "Descargar cotización en formato PDF"}
                    </TooltipContent>
                  </Tooltip>

                  <Button
                    variant="ghost"
                    onClick={reset}
                    className="w-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 flex items-center justify-center gap-2 h-10"
                  >
                    <RefreshCw className="h-4 w-4" />
                    <span className="text-[10px] font-bold uppercase tracking-wider">Limpiar Formulario</span>
                  </Button>
                </div>

                <div className="pt-6 border-t border-slate-100 space-y-6">
                  <div className="flex items-center gap-3 text-slate-800">
                    <MapPin className="h-5 w-5 text-brand-mint" />
                    <span className="text-xs font-bold uppercase tracking-wide">Lugar de atención</span>
                  </div>

                  <div className="bg-slate-50 rounded-2xl p-4 space-y-4">
                    <div className="space-y-1">
                      <p className="text-[11px] font-bold text-slate-700">Sucursal Vitacura: Av. Vitacura #8620 • +56 2 2933 6740</p>
                      <p className="text-[10px] text-slate-500 font-bold">Dirigirse a Recepción del 3er piso - Policlínico Tabancura</p>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <Button variant="outline" size="sm" className="h-8 text-[10px] font-bold border-slate-200">
                        SITIO WEB
                      </Button>
                      <Button variant="outline" size="sm" className="h-8 text-[10px] font-bold border-slate-200">
                        AGENDAR HORA
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>

        {/* STICKY MOBILE ACTION BAR - Visible only on mobile when items are selected */}
        {selectedExams.length > 0 && (
          <div className="fixed bottom-0 left-0 right-0 z-50 lg:hidden animate-in slide-in-from-bottom-full duration-500">
            <div className="bg-brand-dark/95 backdrop-blur-md border-t border-white/10 p-4 pb-6 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.3)] flex flex-col gap-3">
              
              {/* Top row: Summary Info */}
              <div className="flex items-center justify-between px-1 border-b border-white/5 pb-2">
                <div className="flex items-center gap-2">
                  <div className="bg-brand-mint/20 text-brand-mint text-[9px] font-black uppercase px-2 py-0.5 rounded border border-brand-mint/30 tracking-tighter leading-none">
                    {prevision}
                  </div>
                  <div className="text-[10px] font-bold text-white/50 tracking-tight leading-none uppercase">
                    {selectedExams.length} {selectedExams.length === 1 ? 'Examen' : 'Exámenes'}
                  </div>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div className="flex flex-col items-end">
                    <span className="text-[8px] font-black uppercase text-white/20 tracking-widest leading-none mb-0.5">Subtotal</span>
                    <span className="text-xs font-bold text-white/40 leading-none tabular-nums">
                      ${totalV1.toLocaleString('es-CL')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between gap-4">
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-brand-mint uppercase tracking-widest leading-none mb-1">
                    {isFonasa ? 'Total Copago' : 'Total a Pagar'}
                  </span>
                  <span className="text-2xl font-black text-white font-mono leading-none tracking-tighter">
                    ${totalV2.toLocaleString('es-CL')}
                  </span>
                </div>

                <div className="flex items-center gap-2 flex-1 max-w-[210px]">
                  <Button 
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedExams([]);
                      setPackActivo(null);
                      setCurrentStep(2);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                      toast.info('Selección limpiada');
                    }}
                    className="h-12 w-12 bg-white/5 hover:bg-red-500/20 text-white/40 hover:text-red-400 rounded-xl transition-all active:scale-90 flex-shrink-0 border border-white/10"
                    title="Limpiar Selección"
                  >
                    <Trash2 className="h-5 w-5" />
                  </Button>

                  <div className="flex-1">
                    {pdfUrl ? (
                      <Button 
                        className="w-full h-12 bg-brand-mint hover:bg-brand-mint/90 text-brand-dark rounded-xl font-black uppercase text-xs shadow-lg shadow-brand-mint/20"
                        onClick={() => window.open(`${API_URL}${pdfUrl}`, '_blank')}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        PDF
                      </Button>
                    ) : (
                      currentStep === 3 ? (
                        <Button 
                          className={cn(
                            "w-full h-12 rounded-xl font-black uppercase text-xs shadow-lg transition-all active:scale-95",
                            selectedExams.length > 0
                              ? "bg-brand-mint hover:bg-brand-mint/90 text-brand-dark shadow-brand-mint/20"
                              : "bg-slate-700 text-white/30"
                          )}
                          disabled={selectedExams.length === 0 || !prevision || isGenerating}
                          onClick={handleGenerarPDF}
                        >
                          {isGenerating ? <RefreshCw className="h-4 w-4 animate-spin" /> : "Generar"}
                        </Button>
                      ) : (
                        <Button 
                          className="w-full h-12 bg-brand-mint text-brand-dark rounded-xl font-black uppercase text-xs shadow-lg shadow-brand-mint/20"
                          onClick={() => {
                            if (currentStep === 1) setCurrentStep(2);
                            else if (currentStep === 2 && selectedExams.length > 0) setCurrentStep(3);
                            else if (currentStep === 2) toast.info("Selecciona al menos un examen");
                          }}
                        >
                          Siguiente
                        </Button>
                      )
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <Dialog open={isSuccessModalOpen} onOpenChange={setIsSuccessModalOpen}>
          <DialogContent className="max-w-md border-none shadow-2xl p-0 overflow-hidden rounded-3xl">
            <div className="bg-emerald-500 h-2 w-full" />
            <div className="p-8 space-y-6">
              <DialogHeader className="space-y-4">
                <div className="mx-auto w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center border border-emerald-100 shadow-sm">
                  <CheckCircle2 className="h-8 w-8 text-emerald-500" />
                </div>
                <div className="text-center space-y-2">
                  <DialogTitle className="text-2xl font-bold text-slate-800">¡Cotización Generada!</DialogTitle>
                  <DialogDescription className="text-slate-500">
                    Tu presupuesto está listo. ¿Qué te gustaría hacer ahora?
                  </DialogDescription>
                </div>
              </DialogHeader>

              <div className="space-y-3">
                <Button
                  asChild
                  className="w-full h-14 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-2xl shadow-lg shadow-emerald-200/50 flex items-center justify-center gap-3 transition-all active:scale-95"
                >
                  <a href="https://ff.healthatom.io/FKV7ZY" target="_blank" rel="noopener noreferrer">
                    <Calendar className="h-5 w-5" />
                    AGENDAR HORA AHORA
                  </a>
                </Button>

                <Button
                  variant="outline"
                  asChild
                  className="w-full h-14 border-slate-200 text-slate-700 font-bold rounded-2xl flex items-center justify-center gap-3 hover:bg-slate-50 transition-all active:scale-95"
                >
                  <a href={pdfUrl ? `${API_URL}${pdfUrl}` : '#'} target="_blank" download="cotizacion.pdf" rel="noopener noreferrer">
                    <Download className="h-5 w-5" />
                    DESCARGAR ARCHIVO PDF
                  </a>
                </Button>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-2xl flex items-center gap-4 border border-slate-100">
                <div className="bg-white p-2.5 rounded-xl shadow-sm border border-slate-100 shrink-0">
                  <MapPin className="h-5 w-5 text-brand-mint" />
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] font-black text-brand-dark uppercase tracking-widest">Lugar de Atención</span>
                  <span className="text-[11px] text-slate-600 font-bold">Sucursal Vitacura, Av. Vitacura #8620</span>
                  <span className="text-[10px] text-slate-400 font-medium">Dirigirse a Recepción del 3er Piso (+56 2 2933 6740)</span>
                </div>
              </div>

              <Separator className="bg-slate-100" />

              <Button
                variant="ghost"
                onClick={() => {
                  reset();
                  setIsSuccessModalOpen(false);
                }}
                className="w-full text-slate-400 hover:text-slate-600 font-bold h-10 flex items-center justify-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                NUEVA COTIZACIÓN
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </TooltipProvider>
  );
}
