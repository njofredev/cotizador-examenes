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
  CheckCircle2
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
  const [prevision, setPrevision] = React.useState('Particular');
  const [pdfUrl, setPdfUrl] = React.useState<string | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = React.useState(false);

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

  const handleSelectExamen = (examen: Examen) => {
    if (packActivo) {
      toast.warning('No puedes agregar exámenes individuales a un paquete cerrado');
      return;
    }
    if (selectedExams.find(i => i.examen.codigo === examen.codigo)) {
      toast.info('El examen ya está en la lista');
      return;
    }
    setSelectedExams(prev => [...prev, { examen, cantidad: 1 }]);
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
          valor_bono_fonasa: i.examen.valor_bono_fonasa * i.cantidad,
          valor_copago: i.examen.valor_copago * i.cantidad,
          valor_particular_general: i.examen.valor_particular_general * i.cantidad,
          valor_particular_preferencial: i.examen.valor_particular_preferencial * i.cantidad
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
      <div className="min-h-screen bg-[#F8FAFC] pb-12">
        <Toaster position="top-center" richColors />

        <main className="container max-w-6xl mx-auto px-4 pt-12 grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column */}
          <div className="lg:col-span-2 space-y-10">

            {/* Section: Individual Search */}
            <section ref={searchSectionRef} className="space-y-6">
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
                disabled={loading || !!packActivo}
                placeholder="Busca por nombre o código (Ej: 301041, Hemograma, Glucosa...)"
              />
            </section>

            {/* Section: Packages - Hide if individual exams are selected (and not part of a pack) */}
            {(selectedExams.length === 0 || !!packActivo) && (
              <section className="space-y-6 animate-in fade-in slide-in-from-top-4 duration-700">
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
              <div ref={resultsSectionRef} className="pt-8 space-y-4 animate-in slide-in-from-bottom-5 duration-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-brand-mint" />
                    Exámenes seleccionados
                  </h2>
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className="text-slate-400 border-slate-200">
                      {selectedExams.length} ítems
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
              </div>
            )}
          </div>

          {/* Right Column: Calculations */}
          <div className="space-y-6 lg:sticky lg:top-12 h-fit">
            <div className="flex bg-slate-100 p-1.5 rounded-2xl w-full border border-slate-200">
              <Button
                variant="ghost"
                className={cn(
                  "flex-1 h-10 text-[10px] font-black tracking-widest rounded-xl transition-all duration-300",
                  prevision === 'Particular'
                    ? "bg-brand-dark text-brand-mint shadow-lg shadow-brand-dark/20"
                    : "text-slate-400 hover:text-slate-600"
                )}
                onClick={() => setPrevision('Particular')}
              >
                PARTICULAR
              </Button>
              <Button
                variant="ghost"
                className={cn(
                  "flex-1 h-10 text-[10px] font-black tracking-widest rounded-xl transition-all duration-300",
                  prevision === 'Fonasa'
                    ? "bg-brand-dark text-brand-mint shadow-lg shadow-brand-dark/20"
                    : "text-slate-400 hover:text-slate-600"
                )}
                onClick={() => setPrevision('Fonasa')}
              >
                FONASA
              </Button>
            </div>

            <Card className="border-none shadow-xl shadow-slate-200/50 overflow-hidden bg-white/80 backdrop-blur-sm">
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
                        {isFonasa ? 'Total Copago' : 'Particular Pref.'}
                      </span>
                      <p className="text-xs text-slate-400 font-medium">A pagar en sucursal</p>
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
                          disabled={selectedExams.length === 0 || isGenerating}
                          className={cn(
                            "w-full h-14 rounded-2xl text-base font-bold transition-all duration-300 shadow-xl",
                            selectedExams.length === 0
                              ? "bg-[#FFD700] hover:bg-[#FFD700] text-amber-900/50 border-b-4 border-amber-600/30 opacity-60 shadow-amber-200/20"
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
                      {selectedExams.length === 0
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
                      <p className="text-[11px] font-bold text-slate-700">Sucursal Vitacura: Av. Vitacura #8620</p>
                      <p className="text-[10px] text-slate-500">+56 2 2933 6740</p>
                      <p className="text-[9px] text-slate-400 italic">Toma de muestras - Policlínico Tabancura</p>
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
                  onClick={() => {
                    if (pdfUrl) window.open(`${API_URL}${pdfUrl}`, '_blank');
                  }}
                  className="w-full h-14 border-slate-200 text-slate-700 font-bold rounded-2xl flex items-center justify-center gap-3 hover:bg-slate-50 transition-all active:scale-95"
                >
                  <Download className="h-5 w-5" />
                  DESCARGAR ARCHIVO PDF
                </Button>
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
