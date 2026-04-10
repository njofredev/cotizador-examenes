'use client';

import * as React from 'react';
import Image from 'next/image';
import {
  Search,
  User,
  Calendar,
  Activity,
  ArrowLeft,
  FileDown,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Menu,
  ChevronDown,
  LayoutDashboard,
  Users,
  Settings,
  LogOut,
  Bell,
  Sun,
  MapPin,
  PartyPopper,
  FileText,
  Stethoscope,
  MousePointerClick,
  CircleCheck,
  Heart,
  Trash2,
  PlusCircle
} from 'lucide-react';
import { toast, Toaster } from 'sonner';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';

import { ExamSearch } from '@/components/cotizador/examen-search';
import { PacketCard } from '@/components/cotizador/packet-card';
import { CotizacionTable } from '@/components/cotizador/cotizacion-table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';

import { getExamenes, getPaquetes, getPaciente, postCotizar, API_URL, Examen, Paquete } from '@/lib/api';
import { cn, formatRut } from '@/lib/utils';

const PREVISION_OPTIONS = [
  { value: 'Fonasa', label: 'Fonasa' },
  { value: 'Particular', label: 'Particular' },
];

function IntroCard() {
  return (
    <Card className="border-none shadow-xl bg-white overflow-hidden animate-in fade-in slide-in-from-right-4 duration-700">
      <div className="bg-brand-dark h-2 px-1 flex gap-1">
        <div className="h-full w-1/2 bg-brand-dark" />
        <div className="h-full w-1/2 bg-brand-mint" />
      </div>
      <CardHeader className="pt-8 pb-4 text-center">
        <div className="mx-auto w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-4 border border-slate-100 shadow-sm overflow-hidden p-2">
          <Image
            src="/logo_vec.svg"
            alt="Logo Policlínico Tabancura"
            width={64}
            height={64}
            className="object-contain w-full h-full"
          />
        </div>
        <Badge className="w-fit mx-auto mb-2 bg-brand-mint/10 text-brand-dark border-brand-mint/20 hover:bg-brand-mint/10 font-bold px-3 py-1">
          Cotizador Digital
        </Badge>
        <CardTitle className="text-2xl font-black text-slate-800 tracking-tight">
          ¡Bienvenid@ 👋!
        </CardTitle>
        <CardDescription className="text-slate-500 text-sm leading-relaxed px-2">
          Obtén presupuestos oficiales, revisa tus copagos y genera tu orden médica en segundos.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6 pb-8">
        <div className="space-y-4 pt-2">
          <div className="flex gap-4 items-start group">
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0 group-hover:bg-brand-mint/10 transition-colors">
              <User className="h-4 w-4 text-slate-400 group-hover:text-brand-mint" />
            </div>
            <div>
              <p className="text-xs font-black text-brand-dark uppercase tracking-tighter">1. Identifícate</p>
              <p className="text-[11px] text-slate-500 font-medium">Ingresa tu RUT para cargar tu perfil</p>
            </div>
          </div>

          <div className="flex gap-4 items-start group">
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0 group-hover:bg-brand-mint/10 transition-colors">
              <Search className="h-4 w-4 text-slate-400 group-hover:text-brand-mint" />
            </div>
            <div>
              <p className="text-xs font-black text-brand-dark uppercase tracking-tighter">2. Selecciona</p>
              <p className="text-[11px] text-slate-500 font-medium">Busca exámenes individuales o packs</p>
            </div>
          </div>

          <div className="flex gap-4 items-start group">
            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0 group-hover:bg-brand-mint/10 transition-colors">
              <CircleCheck className="h-4 w-4 text-slate-400 group-hover:text-brand-mint" />
            </div>
            <div>
              <p className="text-xs font-black text-brand-dark uppercase tracking-tighter">3. Cotiza</p>
              <p className="text-[11px] text-slate-500 font-medium">Obtén tu PDF oficial listo para usar</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-xl border border-dashed border-slate-200 text-center">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-loose">
            Para comenzar, ingresa tu rut o pasaporte en el panel de identificación 👈
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function CotizadorPage() {
  // State
  const [docId, setDocId] = React.useState('');
  const [nombre, setNombre] = React.useState('');
  const [fechaNac, setFechaNac] = React.useState('');
  const [prevision, setPrevision] = React.useState('');
  const [aceptoTerminos, setAceptoTerminos] = React.useState(false);
  const [isTerminosModalOpen, setIsTerminosModalOpen] = React.useState(false);

  const [examenes, setExamenes] = React.useState<Examen[]>([]);
  const [paquetes, setPaquetes] = React.useState<Paquete[]>([]);
  const [selectedExams, setSelectedExams] = React.useState<{ examen: Examen, cantidad: number }[]>([]);
  const [packActivo, setPackActivo] = React.useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = React.useState<string | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [loading, setLoading] = React.useState(true);
  const [mounted, setMounted] = React.useState(false);

  // Package Confirmation State
  const [pendingPackage, setPendingPackage] = React.useState<Paquete | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = React.useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = React.useState(false);

  // Registration Flow State
  const [isPatientChecked, setIsPatientChecked] = React.useState(false);
  const [isSearching, setIsSearching] = React.useState(false);

  // Refs
  const examSectionRef = React.useRef<HTMLDivElement>(null);
  const resultsSectionRef = React.useRef<HTMLDivElement>(null);

  // Initialization
  React.useEffect(() => {
    async function init() {
      try {
        const [examRes, packRes] = await Promise.all([getExamenes(), getPaquetes()]);
        const allExams = examRes.data;

        // Clean packets: Only keep exams that exist in the master list
        const cleanPaquetes = packRes.data.map(p => ({
          ...p,
          examenes: p.examenes.filter(pe => allExams.some(e => e.codigo === pe.codigo))
        }));

        setExamenes(allExams);
        setPaquetes(cleanPaquetes);
      } catch (error) {
        console.error('Error al cargar datos:', error);
        toast.error('Error al cargar datos del servidor');
      } finally {
        setLoading(false);
      }
    }
    setMounted(true);
    init();
  }, []);

  const handleIngresar = async () => {
    if (docId.length < 5) {
      toast.error('Por favor ingresa un documento válido');
      return;
    }
    setLoading(true);
    try {
      const res = await getPaciente(docId);
      if (res.data && res.data.nombre) {
        setNombre(res.data.nombre);
        if (res.data.fecha_nacimiento) setFechaNac(res.data.fecha_nacimiento.split('T')[0]);
        setPrevision(res.data.prevision || 'Particular');
        toast.success('Paciente encontrado');
      } else {
        toast.info('Paciente nuevo, por favor completa sus datos');
      }
      setIsPatientChecked(true);
    } catch (error) {
      setIsPatientChecked(true); // Allow manual entry even on error
    } finally {
      setLoading(false);
    }
  };

  const handlePrevisionChange = (value: string | null) => {
    const val = value || '';
    setPrevision(val);
    if (val) {
      toast.success('Paso completado: Registro de paciente listo');
      // Scroll to exam section after a short delay for the animation
      setTimeout(() => {
        examSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 400);
    }
  };

  const handleSelectExamen = (examen: Examen) => {
    if (selectedExams.find(i => i.examen.codigo === examen.codigo)) {
      toast.info('El examen ya está en la lista');
      return;
    }
    setSelectedExams(prev => [...prev, { examen, cantidad: 1 }]);
    toast.success(`${examen.nombre} añadido`);
  };

  const handleSelectPaquete = (paquete: Paquete) => {
    setPendingPackage(paquete);
    setIsConfirmOpen(true);
  };

  const confirmPackage = () => {
    if (!pendingPackage) return;

    const newExams = pendingPackage.examenes.map(p_ex => {
      const fullEx = examenes.find(e => e.codigo === p_ex.codigo);
      return fullEx ? { examen: fullEx, cantidad: p_ex.cantidad } : null;
    }).filter(Boolean) as { examen: Examen, cantidad: number }[];

    setSelectedExams(newExams);
    setPackActivo(pendingPackage.nombre);
    toast.success(`Paquete "${pendingPackage.nombre}" aplicado`);

    setIsConfirmOpen(false);
    setPendingPackage(null);

    // Scroll to results after a short delay
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
    setPackActivo(null);
  };

  const handleGenerarPDF = async () => {
    if (!nombre || !prevision || !fechaNac) {
      toast.error('Por favor completa todos los datos del paciente');
      return;
    }
    if (selectedExams.length === 0) {
      toast.error('Selecciona al menos un examen');
      return;
    }

    setIsGenerating(true);
    try {
      const payload = {
        nombre_paciente: nombre,
        fecha_nacimiento: fechaNac,
        tipo_documento: 'RUT/Pasaporte',
        documento_id: docId,
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
        setIsSuccessModalOpen(true);
        toast.success('¡Cotización generada con éxito!');
      }
    } catch (error) {
      toast.error('Error al generar la cotización');
    } finally {
      setIsGenerating(false);
    }
  };

  const reset = () => {
    setDocId('');
    setNombre('');
    setFechaNac('');
    setPrevision('');
    setAceptoTerminos(false);
    setIsPatientChecked(false);
    setSelectedExams([]);
    setPackActivo(null);
    setPdfUrl(null);
    toast.info('Formulario reiniciado');
  };

  // Calculations
  const isFonasa = prevision === 'Fonasa';
  const totalV1 = selectedExams.reduce((acc, item) => acc + (isFonasa ? item.examen.valor_bono_fonasa : item.examen.valor_particular_general) * item.cantidad, 0);
  const totalV2 = selectedExams.reduce((acc, item) => {
    const val = isFonasa ? (item.examen.valor_bono_fonasa > 0 ? item.examen.valor_copago : item.examen.valor_particular_general) : item.examen.valor_particular_preferencial;
    return acc + val * item.cantidad;
  }, 0);

  // --- RENDERING MAIN PAGE (SINGLE INTERFACE) ---
  return (
    <div className="min-h-screen pb-12">
      <Toaster position="top-center" richColors />

      <main className="container max-w-6xl mx-auto px-4 pt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Left Column: Form & Selection */}
        <div className="lg:col-span-2 space-y-6">

          {/* Patient Info Section */}
          <section className="space-y-6">
            {!(aceptoTerminos && nombre && prevision) ? (
              <>
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-3 text-brand-dark">
                    <div className="bg-brand-mint/10 p-2 rounded-xl">
                      <User className="h-6 w-6 text-brand-mint" />
                    </div>
                    Datos del paciente
                  </h2>
                  <p className="text-slate-500 mt-1">Ingresa la identificación para cargar o registrar al paciente</p>
                </div>

                <Card className="border-none shadow-sm overflow-hidden">
                  <CardContent className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className={cn("space-y-2 transition-all duration-300", !isPatientChecked ? "lg:col-span-2" : "lg:col-span-1")}>
                      <label className="text-xs font-bold uppercase text-slate-400 tracking-wider">Identificación (Rut/Pasaporte)</label>
                      <div className="flex gap-2">
                        <Input
                          value={docId}
                          onChange={(e) => setDocId(formatRut(e.target.value))}
                          placeholder="Ingrese RUT o pasaporte..."
                          className="bg-slate-50 border-slate-200 h-11"
                          onKeyDown={(e) => e.key === 'Enter' && handleIngresar()}
                          onBlur={handleIngresar}
                        />
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="outline" size="icon" onClick={handleIngresar} disabled={!mounted ? false : loading} className="h-11 w-11 shrink-0">
                              {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>Buscar paciente o validar RUT</TooltipContent>
                        </Tooltip>
                      </div>
                      {!isPatientChecked && (
                        <div className="flex items-center gap-1.5 px-1 animate-in fade-in slide-in-from-top-1 duration-700">
                          <Activity className="h-3 w-3 text-brand-mint" />
                          <p className="text-[10px] text-slate-400 font-medium italic">
                            Ingresa sólo números, sin puntos ni guión. <b>Presiona Enter</b> para continuar.
                          </p>
                        </div>
                      )}
                    </div>

                    {isPatientChecked && (
                      <>
                        <div className="space-y-2 lg:col-span-1 animate-in fade-in slide-in-from-top-1 duration-300">
                          <label className="text-xs font-bold uppercase text-slate-400 tracking-wider">Nombre completo</label>
                          <Input
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value.toUpperCase())}
                            disabled={!!pdfUrl}
                            placeholder="Ingrese el nombre del paciente..."
                            className="bg-slate-50 border-slate-200 uppercase h-11"
                          />
                        </div>
                        <div className="space-y-2 animate-in fade-in slide-in-from-top-1 duration-300">
                          <label className="text-xs font-bold uppercase text-slate-400 tracking-wider">Fecha de nacimiento</label>
                          <Input
                            type="date"
                            value={fechaNac}
                            onChange={(e) => setFechaNac(e.target.value)}
                            disabled={!!pdfUrl}
                            className="bg-slate-50 border-slate-200 block w-full h-11"
                          />
                        </div>
                        <div className="space-y-2 animate-in fade-in slide-in-from-top-1 duration-300">
                          <label className="text-xs font-bold uppercase text-slate-400 tracking-wider">Previsión</label>
                          <Select value={prevision} onValueChange={handlePrevisionChange} disabled={!!pdfUrl}>
                            <SelectTrigger className="bg-slate-50 border-slate-200 h-11 w-full">
                              <SelectValue placeholder="Seleccione previsión..." />
                            </SelectTrigger>
                            <SelectContent>
                              {PREVISION_OPTIONS.map(opt => <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>

                        {/* Terms and Conditions Checkbox */}
                        <div className="md:col-span-2 mt-4 p-4 bg-slate-50 rounded-xl border border-slate-100 flex items-start gap-4 transition-all hover:bg-slate-100/80 animate-in fade-in slide-in-from-top-1 duration-500">
                          <Checkbox
                            id="terms"
                            className="mt-1 border-slate-300"
                            checked={aceptoTerminos}
                            onCheckedChange={(checked) => setAceptoTerminos(checked as boolean)}
                          />
                          <div className="grid gap-1.5 leading-none">
                            <label
                              htmlFor="terms"
                              className="text-xs font-medium text-slate-700 leading-relaxed cursor-pointer select-none"
                            >
                              He leído y acepto los{" "}
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setIsTerminosModalOpen(true);
                                }}
                                className="text-brand-mint font-bold hover:underline underline-offset-4"
                              >
                                Términos y condiciones
                              </button>
                              <span className="text-[9px] text-slate-400 ml-1">(Hacer clic para leer)</span>
                            </label>
                            <p className="text-[9px] text-slate-400 mt-0.5 font-medium">Declaración jurada obligatoria según ley de derechos del paciente.</p>
                          </div>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : (
              /* Collapsed view when terms are accepted */
              <Card className="border-none bg-brand-dark text-white shadow-lg animate-in slide-in-from-top-4 duration-500">
                <CardContent className="p-4 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="bg-white/10 p-2 rounded-lg">
                        <User className="h-5 w-5 text-brand-mint" />
                      </div>
                      <div>
                        <h3 className="font-bold text-sm leading-tight">{nombre}</h3>
                        <div className="flex items-center gap-2 mt-0.5">
                          <Badge className="bg-brand-mint/20 hover:bg-brand-mint/30 text-brand-mint text-[9px] border-none px-1.5 py-0 h-4">
                            {prevision}
                          </Badge>
                          <span className="text-[10px] text-white/50">{docId}</span>
                        </div>
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setAceptoTerminos(false)}
                      className="text-white/60 hover:text-white hover:bg-white/10 text-xs font-bold gap-2"
                    >
                      <ArrowLeft className="h-3 w-3" /> Cambiar datos
                    </Button>
                  </div>

                  <div className="flex items-center gap-1.5 px-1 animate-in fade-in slide-in-from-top-1 duration-1000">
                    <Activity className="h-3 w-3 text-brand-mint" />
                    <p className="text-[10px] font-medium text-white/50 italic">
                      Ya puedes seleccionar exámenes de manera individual o elegir un paquete preventivo de exámenes.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </section>

          {/* Search Examen Block / Placeholder (Conditional Rendering) */}
          {!pdfUrl && (
            <>
              {(!prevision || !aceptoTerminos) ? (
                /* Placeholder card when no identification/prevision is set or terms not accepted */
                <Card className="border-dashed border-2 bg-amber-50/30 border-amber-100 animate-in fade-in duration-500">
                  <CardContent className="py-12 flex flex-col items-center text-center space-y-4">
                    <div className="bg-white p-4 rounded-full shadow-sm border border-amber-100">
                      <User className="h-8 w-8 text-amber-300" />
                    </div>
                    <div className="max-w-sm">
                      <h3 className="font-bold text-slate-800 text-lg mb-1">
                        {!prevision ? "Identificación" : "Pasos pendientes"}
                      </h3>
                      <p className="text-xs text-slate-500 leading-relaxed px-6">
                        {!prevision
                          ? "Para comenzar, ingresa tu RUT. Cargaremos tus datos automáticamente si ya eres paciente."
                          : "Para continuar, debes completar tus datos, seleccionar tu previsión y leer y aceptar los términos y condiciones."
                        }
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                /* Actual Exam Selection - Shown AFTER Prevision is selected */
                <div ref={examSectionRef} className="space-y-10 animate-in fade-in zoom-in-95 duration-500">

                  {/* Mode 1: Individual Search */}
                  <section className={`space-y-6 transition-opacity ${packActivo ? 'opacity-50 pointer-events-none' : ''}`}>
                    <div className="flex items-center gap-3">
                      <div className="bg-brand-mint/10 p-2 rounded-lg">
                        <Search className="h-5 w-5 text-brand-mint" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-800">
                          Cotiza tus exámenes de manera individual
                          {packActivo && <span className="ml-2 text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-normal ">Limpia el <b>carrito</b> para cotizar de manera individual.</span>}
                        </h3>
                        <p className="text-xs text-slate-500">Agrega exámenes por su nombre o código en el buscador</p>
                      </div>
                    </div>
                    <ExamSearch
                      examenes={examenes}
                      onSelect={handleSelectExamen}
                      onSearchChange={setIsSearching}
                      disabled={!!packActivo}
                      selectedIds={selectedExams.map(i => i.examen.codigo)}
                    />
                  </section>

                  {/* Mode 2: Preventive Packages - Hide when individual exams are selected, or if a pack is active, OR if the user is currently searching */}
                  {(selectedExams.length === 0 || !!packActivo) && !isSearching && (
                    <section className="space-y-6 animate-in fade-in slide-in-from-top-3 duration-500">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="bg-brand-mint/10 p-2 rounded-lg">
                            <Activity className="h-5 w-5 text-brand-mint" />
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-slate-800">Paquetes de Chequeo Preventivo</h3>
                            <p className="text-xs text-slate-500">Optimiza tu salud con grupos de exámenes especializados</p>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
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
                </div>
              )}
            </>
          )}

          {/* Selection Table */}
          {selectedExams.length > 0 && (
            <div ref={resultsSectionRef} className="space-y-4 animate-in slide-in-from-bottom-5 duration-700 scroll-mt-[120px]">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-3 text-brand-dark">
                    <div className="bg-brand-mint/10 p-2 rounded-xl">
                      <Activity className="h-6 w-6 text-brand-mint" />
                    </div>
                    Exámenes seleccionados
                  </h2>
                  <p className="text-slate-500 mt-1">
                    {packActivo ? `Detalle del Pack: ${packActivo}` : 'Revisa el detalle de los servicios que has agregado'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedExams([]);
                      setPackActivo(null);
                      toast.info('Selección limpiada');
                    }}
                    className="text-slate-400 hover:text-red-500 hover:bg-red-50 h-8 gap-1.5 text-[10px] font-bold uppercase tracking-wider transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    Limpiar
                  </Button>
                  <Badge variant="secondary" className="bg-slate-100 text-slate-500 hover:bg-slate-100 font-bold px-3 py-1">
                    {selectedExams.length} ítems
                  </Badge>
                </div>
              </div>
              <CotizacionTable
                items={selectedExams}
                prevision={prevision}
                onUpdateCantidad={updateCantidad}
                onRemove={removeExamen}
                disabled={!!pdfUrl}
                isPackActive={!!packActivo}
              />
            </div>
          )}
        </div>

        {/* Right Column: Totals & Summary */}
        <div className="space-y-6 lg:sticky lg:top-[120px] transition-all duration-500 h-fit">
          {!isPatientChecked ? (
            <IntroCard />
          ) : (
            <Card className={`border-none shadow-xl ${pdfUrl ? 'bg-primary text-white' : 'bg-white'} animate-in zoom-in-95 duration-500`}>
              <CardHeader>
                <CardTitle className="text-xl flex items-center justify-between">
                  Total cotización
                  {pdfUrl && <CheckCircle2 className="h-6 w-6 text-white animate-pulse" />}
                </CardTitle>
                <CardDescription className={pdfUrl ? 'text-blue-100' : ''}>Desglose según tu previsión</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 py-6">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
                    {isFonasa ? 'Valor Bono Fonasa' : 'Total Particular General'}
                  </span>
                  <span className={cn("text-lg font-bold", pdfUrl ? "text-white" : "text-slate-700")}>
                    ${totalV1.toLocaleString('es-CL')}
                  </span>
                </div>
                <Separator className={pdfUrl ? 'bg-white/20' : ''} />
                <div className="flex justify-between items-end">
                  <div>
                    <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider block mb-1">
                      {isFonasa ? 'Total copago' : 'Particular pref.'}
                    </span>
                    <span className={cn("text-[10px] font-medium", pdfUrl ? "text-blue-100" : "text-slate-500")}>
                      A pagar en sucursal
                    </span>
                  </div>
                  <span className={cn("text-2xl font-black", pdfUrl ? "text-white" : "text-brand-dark")}>
                    ${totalV2.toLocaleString('es-CL')}
                  </span>
                </div>

                {isFonasa && totalV2 > totalV1 && !pdfUrl && (
                  <div className="flex gap-2 p-3 bg-amber-50 rounded-lg border border-amber-100 animate-in fade-in slide-in-from-top-1 duration-500">
                    <AlertCircle className="h-3.5 w-3.5 text-amber-600 shrink-0 mt-0.5" />
                    <p className="text-[10px] text-amber-800 font-bold leading-relaxed">
                      Nota: El copago es superior al valor bono debido a que algunos exámenes seleccionados sólo se realizan de forma particular y no cuentan con cobertura Fonasa.
                    </p>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex flex-col gap-3 pt-2">
                {!pdfUrl ? (
                  <>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="w-full">
                          {(() => {
                            const isReady = aceptoTerminos && selectedExams.length > 0 && !isGenerating && !!nombre && !!prevision;
                            return (
                              <Button
                                className={cn(
                                  "w-full h-12 text-base font-black shadow-lg transition-all duration-500 uppercase tracking-tight",
                                  isReady
                                    ? "bg-brand-mint hover:bg-brand-mint/90 text-brand-dark shadow-brand-mint/20"
                                    : "bg-amber-400 hover:bg-amber-500 text-white shadow-amber-200/50"
                                )}
                                disabled={!isReady}
                                onClick={handleGenerarPDF}
                              >
                                {isGenerating ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <FileDown className="mr-2 h-5 w-5" />}
                                Generar Cotización (PDF)
                              </Button>
                            );
                          })()}
                        </div>
                      </TooltipTrigger>
                      <TooltipContent className="bg-brand-dark text-white border-none shadow-xl py-2 px-4 text-xs font-bold animate-in zoom-in-95">
                        {!aceptoTerminos && selectedExams.length === 0
                          ? "Falta aceptar términos y seleccionar exámenes"
                          : !aceptoTerminos
                            ? "Debes aceptar los términos y condiciones"
                            : "Selecciona al menos un examen"
                        }
                      </TooltipContent>
                    </Tooltip>
                    <Button
                      variant="ghost"
                      className="w-full text-slate-400 hover:text-slate-600 hover:bg-slate-50 text-[10px] uppercase font-bold tracking-widest mt-1"
                      onClick={reset}
                    >
                      <RefreshCw className="mr-2 h-3 w-3" /> Limpiar Formulario
                    </Button>
                  </>
                ) : (
                  <>
                    <Button variant="secondary" className="w-full h-12 text-base font-black text-primary bg-white hover:bg-slate-100 shadow-xl" onClick={() => window.open(`${API_URL}${pdfUrl}`, '_blank')}>
                      <FileDown className="mr-2 h-5 w-5" /> Descargar PDF
                    </Button>
                    <Button variant="ghost" className="w-full text-white/80 hover:text-white hover:bg-white/10 font-bold" onClick={reset}>
                      <RefreshCw className="mr-2 h-4 w-4" /> Nueva Cotización
                    </Button>
                  </>
                )}

                <Separator className={pdfUrl ? 'bg-white/20' : 'bg-slate-100'} />

                {/* Branch info integrated inside the main card */}
                <div className="w-full space-y-3 py-2 text-left">
                  <div className="flex items-center gap-2">
                    <MapPin className={`h-4 w-4 ${pdfUrl ? 'text-brand-mint' : 'text-primary'}`} />
                    <h4 className={`text-[11px] font-bold uppercase tracking-wider ${pdfUrl ? 'text-white' : 'text-slate-800'}`}>Lugar de atención</h4>
                  </div>
                  <div className={`p-3 rounded-lg border flex flex-col gap-2 ${pdfUrl ? 'bg-white/10 border-white/20 text-blue-50' : 'bg-slate-50 border-slate-100 text-slate-500'}`}>
                    <p className="text-[10px] leading-relaxed font-bold">
                      Sucursal Vitacura: Av. Vitacura #8620 • +562 2933 6740
                    </p>
                    <p className="text-[9px] leading-relaxed opacity-80">
                      Toma de muestras - Policlínico Tabancura
                    </p>
                    <div className="flex gap-2 pt-1">
                      <a href="https://www.policlinicotabancura.cl" target="_blank" className={`flex-1 text-[9px] font-black text-center py-1.5 rounded uppercase border transition-all ${pdfUrl ? 'border-white/30 text-white hover:bg-white/10' : 'border-slate-200 text-primary hover:bg-white'}`}>Sitio Web</a>
                      <a href="https://ff.healthatom.io/FKV7ZY" target="_blank" className={`flex-1 text-[9px] font-black text-center py-1.5 rounded uppercase border transition-all ${pdfUrl ? 'border-white/30 text-white hover:bg-white/10' : 'border-slate-200 text-primary hover:bg-white'}`}>Agendar Hora</a>
                    </div>
                  </div>
                </div>
              </CardFooter>
            </Card>
          )}
        </div>
      </main>

      {/* Package Detail/Confirmation Dialog */}
      <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <DialogContent className="max-w-md border-none shadow-2xl">
          <DialogHeader className="space-y-3">
            <div className="w-12 h-12 bg-brand-dark/5 rounded-full flex items-center justify-center mb-2">
              <Activity className="h-6 w-6 text-brand-dark" />
            </div>
            <DialogTitle className="text-xl font-bold text-slate-800 flex items-center justify-between">
              <span>Detalle del Paquete</span>
              <span className="text-[10px] bg-brand-mint/20 text-brand-dark px-2 py-1 rounded-full border border-brand-mint/30 font-black uppercase tracking-tighter">
                {pendingPackage?.examenes.length} Exámenes
              </span>
            </DialogTitle>
            <DialogDescription className="text-slate-500 text-xs">
              Estás por aplicar el paquete <span className="font-bold text-brand-dark">{pendingPackage?.nombre}</span>.
              Revisa los exámenes que incluye a continuación:
            </DialogDescription>
          </DialogHeader>

          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 max-h-60 overflow-y-auto mt-2">
            <ul className="space-y-2">
              {pendingPackage?.examenes.map((ex, idx) => (
                <li key={idx} className="text-xs font-medium text-slate-600 flex items-start gap-2">
                  <span className="text-brand-dark font-bold mt-0.5">•</span>
                  {ex.nombre}
                </li>
              ))}
            </ul>
          </div>

          <DialogFooter className="mt-6 flex gap-2">
            <Button variant="ghost" className="flex-1 font-bold h-11" onClick={() => {
              setIsConfirmOpen(false);
              setPendingPackage(null);
            }}>
              Volver
            </Button>
            <Button className="flex-1 bg-brand-dark text-brand-mint hover:bg-brand-dark/90 font-bold h-11 shadow-lg shadow-brand-dark/20" onClick={confirmPackage}>
              Confirmar y Agregar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Terms and Conditions Dialog */}
      <Dialog open={isTerminosModalOpen} onOpenChange={setIsTerminosModalOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold flex items-center gap-2 outline-none" tabIndex={0}>
              <Activity className="h-5 w-5 text-primary" />
              Términos y Condiciones del Servicio
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4 text-slate-600 text-sm leading-relaxed">
            <h4 className="font-bold text-slate-800">Policlínico Tabancura</h4>
            <ol className="space-y-4 list-decimal pl-4">
              <li>
                <span className="font-bold text-slate-800">Propósito del Cotizador</span>: Este servicio es una herramienta informativa. Los precios mostrados son referenciales y pueden variar según la vigencia de los aranceles de Fonasa o su Isapre al momento de la atención presencial.
              </li>
              <li>
                <span className="font-bold text-slate-800">Privacidad de Datos</span>: Los datos personales ingresados (Nombre, RUT, Fecha de Nacimiento) serán utilizados exclusivamente para generar la cotización y la orden médica correspondiente en nuestros sistemas. El Policlínico Tabancura garantiza la confidencialidad de su información.
              </li>
              <li>
                <span className="font-bold text-slate-800">Validez de la Cotización</span>: Esta cotización tiene una validez de <span className="font-bold">30 días corridos</span> desde la fecha de emisión. Transcurrido este plazo, los valores podrían ser actualizados.
              </li>
              <li>
                <span className="font-bold text-slate-800">Preparación para Exámenes</span>: Es responsabilidad del paciente informarse sobre los requisitos de ayuno o preparación previa para cada examen. Puede consultar estos detalles en nuestro sitio web o por vía telefónica.
              </li>
              <li>
                <span className="font-bold text-slate-800">Órdenes Médicas</span>: Las órdenes médicas generadas a través de paquetes preventivos son válidas únicamente para ser utilizadas en el Policlínico Tabancura.
              </li>
              <li>
                <span className="font-bold text-slate-800">Aceptación</span>: Al marcar la casilla "Acepto los términos y condiciones", usted declara que ha leído, comprendido y aceptado los puntos anteriores.
              </li>
              <li>
                <span className="font-bold text-slate-800">Email marketing</span>: Al aceptar los términos y condiciones, usted acepta recibir correos electrónicos con información sobre nuestros servicios y promociones.
              </li>
            </ol>
            <div className="mt-8 pt-4 border-t text-[10px] text-slate-400 text-center">
              © 2026 Policlínico Tabancura - Todos los derechos reservados.
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setIsTerminosModalOpen(false)} className="w-full sm:w-auto">
              He leído los términos
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      {/* Success and Booking Modal */}
      <Dialog open={isSuccessModalOpen} onOpenChange={setIsSuccessModalOpen}>
        <DialogContent className="max-w-md p-0 overflow-hidden border-none shadow-2xl">
          <div className="bg-brand-mint/10 p-8 flex flex-col items-center text-center space-y-4">
            <div className="w-20 h-20 bg-brand-mint text-white rounded-full flex items-center justify-center shadow-lg shadow-brand-mint/30 animate-in zoom-in duration-500">
              <CheckCircle2 className="h-10 w-10" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-black text-brand-dark flex items-center justify-center gap-2">
                ¡Todo Listo! <PartyPopper className="h-6 w-6 text-brand-mint" />
              </h2>
              <p className="text-slate-600 text-sm font-medium leading-relaxed">
                Tu cotización ha sido generada exitosamente. El documento ya se encuentra disponible para su descarga.
              </p>
            </div>
          </div>

          <div className="p-6 bg-white space-y-6">
            <div className="space-y-3">
              <Button
                className="w-full bg-brand-dark text-brand-mint hover:bg-brand-dark/90 h-14 text-base font-black shadow-xl shadow-brand-dark/20 uppercase tracking-tight flex items-center justify-center gap-3 transition-all hover:scale-[1.02]"
                onClick={() => {
                  window.open('https://policlinicotabancura.cl/reserva-de-horas/', '_blank');
                  setIsSuccessModalOpen(false);
                }}
              >
                <Calendar className="h-5 w-5" />
                Agendar mi Hora Ahora
              </Button>

              <p className="text-[10px] text-slate-400 text-center uppercase font-bold tracking-widest">
                O puedes revisar tu documento
              </p>

              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  className="border-slate-200 text-slate-600 font-bold h-11 text-xs flex items-center gap-2"
                  onClick={() => pdfUrl && window.open(pdfUrl, '_blank')}
                >
                  <FileText className="h-4 w-4" />
                  Ver PDF
                </Button>
                <Button
                  variant="ghost"
                  className="text-slate-500 font-bold h-11 text-xs"
                  onClick={() => setIsSuccessModalOpen(false)}
                >
                  Cerrar
                </Button>
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg flex items-center gap-3 border border-slate-100">
              <div className="bg-white p-2 rounded shadow-sm">
                <MapPin className="h-4 w-4 text-brand-mint" />
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] font-black text-brand-dark uppercase tracking-tighter">Lugar de Atención</span>
                <span className="text-[11px] text-slate-500 font-medium">Sucursal Vitacura, Av. Vitacura #8620</span>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
