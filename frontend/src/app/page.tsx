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
  PlusCircle,
  ShieldCheck,
  Download
} from 'lucide-react';
import { toast, Toaster } from 'sonner';

import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "../components/ui/tooltip";
import { Separator } from '../components/ui/separator';
import { Badge } from '../components/ui/badge';
import { Checkbox } from '../components/ui/checkbox';

import { ExamSearch } from '../components/cotizador/examen-search';
import { PacketCard } from '../components/cotizador/packet-card';
import { CotizacionTable } from '../components/cotizador/cotizacion-table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '../components/ui/dialog';

import { getExamenes, getPaquetes, getPaciente, postCotizar, API_URL, Examen, Paquete } from '../lib/api';
import { cn, formatRut } from '../lib/utils';

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
              <p className="text-xs font-black text-brand-dark uppercase tracking-tighter">2. Tipo de Previsión</p>
              <p className="text-[11px] text-slate-500 font-medium tracking-tight">Selecciona una de las dos previsiones para acceder a la selección de exámenes.</p>
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
  const [errorCarga, setErrorCarga] = React.useState<string | null>(null);
  const [mounted, setMounted] = React.useState(false);

  // Package Confirmation State
  const [pendingPackage, setPendingPackage] = React.useState<Paquete | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = React.useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = React.useState(false);
  const [currentStep, setCurrentStep] = React.useState(1); // 1: Info, 2: Search, 3: Results


  // Registration Flow State
  const [isPatientChecked, setIsPatientChecked] = React.useState(false);
  const [isEditingPatient, setIsEditingPatient] = React.useState(false);
  const [isSearching, setIsSearching] = React.useState(false);

  // Refs
  const examSectionRef = React.useRef<HTMLDivElement>(null);
  const resultsSectionRef = React.useRef<HTMLDivElement>(null);

  // Initialization
  React.useEffect(() => {
    setMounted(true);
    init();
  }, []);

  async function init() {
    setLoading(true);
    setErrorCarga(null);
    try {
      const [examRes, packRes] = await Promise.all([
        getExamenes(),
        getPaquetes()
      ]);
      const allExams: Examen[] = examRes.data;

      // Clean packets: Only keep exams that exist in the master list
      const cleanPaquetes = packRes.data.map(p => ({
        ...p,
        examenes: p.examenes.filter(pe => allExams.some(e => e.codigo === pe.codigo))
      }));

      setExamenes(allExams);
      setPaquetes(cleanPaquetes);
    } catch (error: any) {
      console.error('Error al cargar datos:', error);
      const msg = error.response?.data?.detail || error.message || 'Error de conexión';
      setErrorCarga(msg);
      toast.error(`Error al cargar datos: ${msg}`);
    } finally {
      setLoading(false);
    }
  }

  const handleIngresar = async () => {
    if (docId.length < 5) {
      toast.error('Por favor ingresa un documento válido');
      return;
    }
    setLoading(true);
    try {
      const res = await getPaciente(docId);
      if (res.data && res.data.nombre) {
        // Only show toast if data is different or not yet checked
        if (nombre !== res.data.nombre) {
          setNombre(res.data.nombre);
          if (res.data.fecha_nacimiento) setFechaNac(res.data.fecha_nacimiento.split('T')[0]);
          setPrevision(res.data.prevision || 'Particular');
          toast.success('Paciente encontrado');
        }
      } else {
        if (!nombre) toast.info('Paciente nuevo, por favor completa sus datos');
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
    if (val && aceptoTerminos && nombre) {
      toast.success('Paso completado: Registro de paciente listo');
      setIsEditingPatient(false); // End editing mode when prevision is confirmed
      setTimeout(() => setCurrentStep(2), 600);
      // Scroll to exam section after a short delay for the animation
      setTimeout(() => {
        examSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 400);
    } else if (val && !isPatientChecked) {
      // If choosing prevision in guest mode (or while filling info), advance to exams
      setCurrentStep(2);
    }
  };

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
    if (selectedExams.find(i => i.examen.codigo === examen.codigo)) {
      toast.info('El examen ya está en la lista');
      return;
    }
    const initialCantidad = DEFAULT_QUANTITIES[examen.codigo] || 1;
    setSelectedExams(prev => [...prev, { examen, cantidad: initialCantidad }]);
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
          valor_bono_fonasa: i.examen.valor_bono_fonasa,
          valor_copago: i.examen.valor_copago,
          valor_particular_general: i.examen.valor_particular_general,
          valor_particular_preferencial: i.examen.valor_particular_preferencial
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
    setCurrentStep(1);
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
  const isReady = aceptoTerminos && selectedExams.length > 0 && !isGenerating && !!nombre && !!prevision;

  if (!mounted) return null;

  if (errorCarga && examenes.length === 0) {
    return (
      <div className="min-h-svh flex items-center justify-center bg-slate-50 p-6">
        <Card className="max-w-md w-full border-none shadow-2xl p-8 text-center space-y-6">
          <div className="w-20 h-20 bg-red-50 text-red-500 rounded-3xl flex items-center justify-center mx-auto shadow-sm">
            <AlertCircle className="h-10 w-10" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-black text-slate-800 tracking-tight">Fallo de Conexión</h2>
            <p className="text-slate-500 text-sm leading-relaxed">
              No pudimos conectar con el servidor para cargar los exámenes. Esto puede ser un problema temporal de red.
            </p>
            <div className="bg-slate-100 p-2 rounded-lg mt-2 font-mono text-[10px] text-slate-400 break-all">
              Error: {errorCarga}
            </div>
          </div>
          <Button 
            onClick={() => init()}
            className="w-full h-14 bg-brand-dark text-brand-mint hover:bg-brand-dark/90 font-black uppercase tracking-tight rounded-2xl shadow-xl shadow-brand-dark/20 flex items-center justify-center gap-3 transition-all active:scale-95"
          >
            <RefreshCw className="h-5 w-5" />
            Reintentar Conexión
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-svh flex flex-col bg-slate-50">
      <Toaster position="top-center" richColors />

      {/* MOBILE STICKY HEADER - Shown when identified and scrolled */}
      {isPatientChecked && nombre && (
        <div className="fixed top-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-lg border-b border-slate-100 p-3 md:hidden animate-in slide-in-from-top-full duration-500 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-brand-mint/10 p-1.5 rounded-lg">
              <User className="h-4 w-4 text-brand-mint" />
            </div>
            <div>
              <p className="text-[10px] font-black text-slate-800 leading-none">{nombre}</p>
              <p className="text-[8px] font-bold text-brand-mint uppercase tracking-tighter mt-0.5">{prevision}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-[9px] font-black uppercase tracking-tighter"
            onClick={() => {
              setIsEditingPatient(true);
              setCurrentStep(1);
            }}
          >
            Editar
          </Button>

        </div>
      )}

      {/* MOBILE STEP INDICATOR */}
      <div className="md:hidden pt-16 px-4">
        <div className="flex items-center justify-between gap-2 max-w-sm mx-auto bg-slate-50 p-1.5 rounded-2xl border border-slate-100">
          {[
            { step: 1, label: 'Previsión', icon: ShieldCheck },
            { step: 2, label: 'Selecciona', icon: Search },
            { step: 3, label: 'Cotiza', icon: Activity }
          ].map((s) => (
            <button
              key={s.step}
              onClick={() => {
                // Only allow going to step 2 if step 1 is done
                if (s.step === 2 && (!nombre || !prevision || !aceptoTerminos)) return;
                // Only allow going to step 3 if step 2 has items
                if (s.step === 3 && selectedExams.length === 0) return;
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

      <main className={cn(
        "container max-w-6xl mx-auto px-4 pt-4 md:pt-8 grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8 md:pb-12",
        selectedExams.length > 0 && isPatientChecked ? "pb-[220px]" : "pb-12"
      )}>

        {/* Left Column: Form & Selection */}
        <div className="lg:col-span-2 space-y-4 md:space-y-6">

          {/* Patient Info Section */}
          <section className={cn(
            "space-y-4 md:space-y-6",
            currentStep !== 1 && "hidden md:block" // Hide on mobile if not in step 1
          )}>

            {(!(aceptoTerminos && nombre && prevision) || isEditingPatient) ? (
              <>
                <div className="px-1">
                  <h2 className="text-xl md:text-2xl font-black flex items-center gap-3 text-brand-dark">
                    <div className="bg-brand-mint/10 p-2 rounded-xl">
                      <User className="h-5 w-5 md:h-6 md:w-6 text-brand-mint" />
                    </div>
                    Identificación del Paciente
                  </h2>
                  <p className="text-xs md:text-sm text-slate-500 mt-1">Ingresa tu documento para cargar tu perfil</p>
                </div>

                <Card className="border-none shadow-sm overflow-hidden rounded-2xl">
                  <CardContent className="p-4 md:p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className={cn("space-y-2 transition-all duration-300", !isPatientChecked ? "lg:col-span-2" : "lg:col-span-1")}>
                      <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest pl-1">RUT o Pasaporte</label>
                      <div className="flex gap-2">
                        <Input
                          value={docId}
                          onChange={(e) => setDocId(formatRut(e.target.value))}
                          placeholder="Ej: 12.345.678-9"
                          className="bg-slate-50 border-slate-200 h-11 md:h-12 rounded-xl"
                          onKeyDown={(e) => e.key === 'Enter' && handleIngresar()}
                          onBlur={handleIngresar}
                        />
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="outline" size="icon" onClick={handleIngresar} disabled={!mounted ? false : loading} className="h-11 w-11 md:h-12 md:w-12 rounded-xl shrink-0">
                              {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>Buscar o validar</TooltipContent>
                        </Tooltip>
                      </div>
                      {!isPatientChecked && (
                        <div className="flex items-center gap-1.5 px-1 animate-in fade-in slide-in-from-top-1 duration-700">
                          <Activity className="h-3 w-3 text-brand-mint" />
                          <p className="text-[10px] text-slate-400 font-bold italic">
                            Una vez ingresado tu número de identificación, presiona Enter para continuar.
                          </p>
                        </div>
                      )}
                    </div>

                    {isPatientChecked && (
                      <>
                        <div className="space-y-2 lg:col-span-1 animate-in fade-in slide-in-from-top-1 duration-300">
                          <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest pl-1">Nombre Completo</label>
                          <Input
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value.toUpperCase())}
                            disabled={!!pdfUrl}
                            placeholder="NOMBRE APELLIDO"
                            className="bg-slate-50 border-slate-200 uppercase h-11 md:h-12 rounded-xl font-bold"
                          />
                        </div>
                        <div className="space-y-2 animate-in fade-in slide-in-from-top-1 duration-300">
                          <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest pl-1">Fecha Nacimiento</label>
                          <Input
                            type="date"
                            value={fechaNac}
                            onChange={(e) => setFechaNac(e.target.value)}
                            disabled={!!pdfUrl}
                            className="bg-slate-50 border-slate-200 block w-full h-11 md:h-12 rounded-xl font-bold"
                          />
                        </div>
                        <div className="space-y-2 animate-in fade-in slide-in-from-top-1 duration-300">
                          <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest pl-1">Previsión</label>
                          <Select value={prevision} onValueChange={handlePrevisionChange} disabled={!!pdfUrl}>
                            <SelectTrigger className="bg-slate-50 border-slate-200 h-11 md:h-12 w-full rounded-xl font-bold">
                              <SelectValue placeholder="Seleccione..." />
                            </SelectTrigger>
                            <SelectContent className="rounded-xl border-slate-100 shadow-2xl">
                              {PREVISION_OPTIONS.map(opt => <SelectItem key={opt.value} value={opt.value} className="font-bold">{opt.label}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>

                        {/* Terms and Conditions Checkbox */}
                        <div className="md:col-span-2 mt-2 p-4 bg-slate-50/50 rounded-2xl border border-slate-100 flex items-start gap-4 transition-all hover:bg-slate-100/50 animate-in fade-in slide-in-from-top-1 duration-500">
                          <Checkbox
                            id="terms"
                            className="mt-1 border-slate-300 h-5 w-5 rounded-md"
                            checked={aceptoTerminos}
                            onCheckedChange={(checked) => {
                              const val = checked as boolean;
                              setAceptoTerminos(val);
                              if (val && nombre && prevision) {
                                setTimeout(() => setCurrentStep(2), 600);
                              }
                            }}
                          />
                          <div className="grid gap-1.5 leading-none">
                            <label
                              htmlFor="terms"
                              className="text-xs font-bold text-slate-600 leading-relaxed cursor-pointer select-none"
                            >
                              Acepto los{" "}
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.preventDefault();
                                  setIsTerminosModalOpen(true);
                                }}
                                className="text-brand-mint font-black hover:underline underline-offset-4 decoration-2"
                              >
                                Términos y condiciones
                              </button>
                            </label>
                            <p className="text-[9px] text-slate-400 font-bold uppercase tracking-tighter">Declaración obligatoria según ley de derechos del paciente.</p>
                          </div>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : (
              /* Collapsed view when terms are accepted */
              <Card className="border-none bg-brand-dark text-white shadow-xl rounded-2xl animate-in slide-in-from-top-4 duration-500 overflow-hidden">
                <div className="h-1 w-full bg-brand-mint" />
                <CardContent className="p-4 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="bg-white/10 p-2 rounded-xl">
                        <User className="h-5 w-5 text-brand-mint" />
                      </div>
                      <div>
                        <h3 className="font-black text-sm tracking-tight">{nombre}</h3>
                        <div className="flex items-center gap-2 mt-0.5">
                          <Badge className="bg-brand-mint/20 hover:bg-brand-mint/30 text-brand-mint text-[9px] border-none px-2 py-0 h-4 font-black">
                            {prevision}
                          </Badge>
                          <span className="text-[10px] text-white/40 font-mono">{docId}</span>
                        </div>
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setAceptoTerminos(false)}
                      className="text-white/40 hover:text-white hover:bg-white/10 text-[10px] font-black gap-2 uppercase tracking-tighter"
                    >
                      <RefreshCw className="h-3 w-3" /> Cambiar
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </section>

          {/* Search Examen Block / Placeholder (Conditional Rendering) */}
          <div className={cn(
            "space-y-6",
            currentStep !== 2 && "hidden md:block" // Hide on mobile if not in step 2
          )}>
            {!pdfUrl && (
              <>
                {(!prevision || !aceptoTerminos) ? (
                  /* Placeholder card when no identification/prevision is set or terms not accepted */
                  <Card className="border-dashed border-2 bg-slate-50/30 border-slate-200 rounded-2xl animate-in fade-in duration-500">
                    <CardContent className="py-10 md:py-12 flex flex-col items-center text-center space-y-4">
                      <div className="bg-amber-50 p-4 rounded-2xl shadow-sm border border-amber-100 animate-pulse">
                        <AlertCircle className="h-8 w-8 text-amber-500" />
                      </div>
                      <div className="max-w-sm px-4">
                        <h3 className="font-black text-amber-600/60 text-sm md:text-base uppercase tracking-widest">
                          Identificación Requerida
                        </h3>
                        <h1 className="text-2xl font-black text-slate-800 tracking-tight">Paso Pendiente</h1>
                        <p className="text-slate-500 text-sm font-medium leading-relaxed">Para comenzar a buscar exámenes, primero ingresa tu <span className="text-brand-dark font-black">RUT o Pasaporte</span> en el panel de identificación.</p>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  /* Actual Exam Selection - Shown AFTER Prevision is selected */
                  <div ref={examSectionRef} className="space-y-6 md:space-y-10 animate-in fade-in zoom-in-95 duration-500">

                    {/* Mode 1: Individual Search */}
                    <section className={`space-y-4 md:space-y-6 transition-opacity ${packActivo ? 'opacity-50 pointer-events-none' : ''}`}>
                      <div className="flex items-center gap-3 px-1">
                        <div className="bg-brand-mint/10 p-2 rounded-xl">
                          <Search className="h-5 w-5 text-brand-mint" />
                        </div>
                        <div>
                          <h3 className="text-base md:text-xl font-black text-brand-dark tracking-tight">
                            Selección Individual
                          </h3>
                          <p className="text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-tighter">Buscador avanzado por nombre o código</p>
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
                      <section className="space-y-4 md:space-y-6 animate-in fade-in slide-in-from-top-3 duration-500">
                        <div className="flex items-center gap-3 px-1">
                          <div className="bg-brand-mint/10 p-2 rounded-xl">
                            <Activity className="h-5 w-5 text-brand-mint" />
                          </div>
                          <div>
                            <h3 className="text-base md:text-xl font-black text-brand-dark tracking-tight">Packs Preventivos</h3>
                            <p className="text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-tighter">Optimiza tu salud con chequeos dirigidos</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
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
          </div>

          {/* Selection Table */}
          <div className={cn(
            "space-y-4",
            currentStep !== 3 && "hidden md:block" // Hide on mobile if not in step 3
          )}>
            {selectedExams.length > 0 && (

              <div ref={resultsSectionRef} className="space-y-4 animate-in slide-in-from-bottom-5 duration-700 scroll-mt-[120px]">
                <div className="flex items-center justify-between px-1">
                  <div>
                    <h2 className="text-xl md:text-2xl font-black flex items-center gap-3 text-brand-dark tracking-tight">
                      <div className="bg-brand-mint/10 p-2 rounded-xl">
                        <Activity className="h-5 w-5 md:h-6 md:w-6 text-brand-mint" />
                      </div>
                      Lista de Selección
                    </h2>
                    <p className="text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">
                      {packActivo ? `Mostrando Pack: ${packActivo}` : 'Exámenes agregados a tu cotización'}
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
                      className="text-slate-400 hover:text-red-500 hover:bg-red-50 h-8 gap-2 text-[10px] font-black uppercase tracking-tighter transition-all rounded-lg"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      <span className="hidden sm:inline">Limpiar</span>
                    </Button>
                    <Badge variant="secondary" className="bg-brand-dark text-brand-mint hover:bg-brand-dark font-black px-3 py-1 rounded-full border-none">
                      {selectedExams.reduce((acc, curr) => acc + curr.cantidad, 0)} ítems
                    </Badge>
                  </div>
                </div>
                <CotizacionTable
                  items={selectedExams}
                  prevision={prevision}
                  onUpdateCantidad={(codigo, cant) => {
                    setSelectedExams(prev => {
                      const newExams = [...prev];
                      const idx = newExams.findIndex(i => i.examen.codigo === codigo);
                      if (idx > -1) {
                        newExams[idx].cantidad = cant;
                      }
                      return newExams;
                    });
                  }}
                  onRemove={(codigo) => setSelectedExams(prev => prev.filter(i => i.examen.codigo !== codigo))}
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
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{isFonasa ? 'Bono Fonasa' : 'Arancel Gral. (Isapre/Part.)'}</span>
                      <span className="text-base font-bold text-slate-600">${totalV1.toLocaleString('es-CL')}</span>
                    </div>
                    <div className="flex justify-between items-center bg-brand-mint/5 p-4 rounded-2xl border border-brand-mint/10">
                      <div>
                        <span className="text-[9px] font-black text-brand-mint uppercase tracking-tighter">{isFonasa ? 'Tu Copago' : 'Arancel Mi Vita'}</span>
                        <p className="text-[10px] text-slate-500 font-bold leading-none mt-1">{isFonasa ? 'Bono Fonasa' : 'Precio Preferencial (Tarjeta Mi Vita)'}</p>
                      </div>
                      <span className="text-2xl font-black text-brand-dark">${totalV2.toLocaleString('es-CL')}</span>
                    </div>
                    <Button
                      onClick={() => {
                        if (pdfUrl) window.open(`${API_URL}${pdfUrl}`, '_blank');
                        else handleGenerarPDF();
                      }}
                      disabled={!aceptoTerminos || !nombre || !prevision || isGenerating || (selectedExams.length === 0 && !pdfUrl)}
                      className={cn(
                        "w-full h-14 rounded-2xl font-black uppercase tracking-tight shadow-lg transition-all active:scale-95 border-b-4",
                        pdfUrl 
                          ? "bg-brand-mint hover:bg-brand-mint/90 text-brand-dark border-brand-mint/20" 
                          : "bg-emerald-500 hover:bg-emerald-600 text-white border-emerald-700 shadow-emerald-100"
                      )}
                    >
                      {isGenerating ? <RefreshCw className="h-5 w-5 animate-spin mr-3" /> : <FileDown className="h-5 w-5 mr-3" />}
                      {isGenerating ? 'Generando...' : pdfUrl ? 'Descargar PDF Oficial' : 'Generar y Descargar'}
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>


        {/* Right Column: Totals & Summary - Hidden on mobile, but values used in sticky bar */}
        <div className="space-y-6 lg:sticky lg:top-[120px] transition-all duration-500 h-fit hidden lg:block">
          {!isPatientChecked ? (
            <IntroCard />
          ) : (
            <Card className={cn(
              "border-none shadow-xl animate-in zoom-in-95 duration-500 rounded-3xl overflow-hidden relative",
              pdfUrl ? "bg-gradient-to-b from-brand-dark to-slate-900 text-white shadow-brand-mint/10" : "bg-white"
            )}>
              {pdfUrl && <div className="absolute top-0 right-0 w-32 h-32 bg-brand-mint/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none" />}
              <div className={cn("relative h-1.5 w-full", pdfUrl ? "bg-brand-mint" : "bg-gradient-to-r from-brand-mint to-brand-dark")} />
              <CardHeader className="relative z-10">
                {pdfUrl ? (
                  <div className="flex items-center gap-3 mb-2 animate-in fade-in slide-in-from-left-4 duration-500">
                    <div className="bg-brand-mint text-brand-dark p-2 rounded-full shadow-lg shadow-brand-mint/20">
                      <CheckCircle2 className="h-6 w-6" />
                    </div>
                    <div>
                      <CardTitle className="text-2xl font-black tracking-tight text-white">¡Cotización Lista!</CardTitle>
                      <CardDescription className="font-bold text-[10px] uppercase tracking-widest text-brand-mint/80 mt-1">
                        Presupuesto guardado y generado
                      </CardDescription>
                    </div>
                  </div>
                ) : (
                  <>
                    <CardTitle className="text-xl font-black flex items-center justify-between tracking-tight">
                      Resumen Cotización
                    </CardTitle>
                    <CardDescription className="font-bold text-[10px] uppercase tracking-widest text-slate-400">Cifras actualizadas</CardDescription>
                  </>
                )}
              </CardHeader>
              <CardContent className="space-y-6 py-4 relative z-10">
                <div className="flex justify-between items-center px-1">
                  <span className={cn("text-[10px] font-black uppercase tracking-widest", pdfUrl ? "text-white/50" : "text-slate-400")}>
                    {isFonasa ? 'Valor Bono Fonasa' : 'Arancel Gral. (Isapre/Part.)'}
                  </span>
                  <span className={cn("text-lg font-black font-mono", pdfUrl ? "text-white/80" : "text-slate-600")}>
                    ${totalV1.toLocaleString('es-CL')}
                  </span>
                </div>
                <Separator className={pdfUrl ? 'bg-white/5' : 'bg-slate-50'} />
                <div className={cn(
                  "flex justify-between items-end p-4 rounded-2xl border",
                  pdfUrl ? "bg-white/5 border-white/10 backdrop-blur-sm" : "bg-slate-50/50 border-slate-50"
                )}>
                  <div>
                    <span className={cn("text-[10px] font-black uppercase tracking-widest block mb-1", pdfUrl ? "text-white/60" : "text-slate-400")}>
                      {isFonasa ? 'Tu Copago Final' : 'Total a Pagar'}
                    </span>
                    <span className={cn("text-[9px] font-black uppercase tracking-tighter", pdfUrl ? "text-brand-mint" : "text-brand-mint")}>
                      {isFonasa ? 'A pagar en Vitacura' : 'Arancel Mi Vita (Preferencial)'}
                    </span>
                  </div>
                  <span className={cn("text-3xl font-black font-mono tracking-tighter", pdfUrl ? "text-white" : "text-brand-dark")}>
                    ${totalV2.toLocaleString('es-CL')}
                  </span>
                </div>

                {isFonasa && totalV2 > totalV1 && !pdfUrl && (
                  <div className="flex gap-2 p-3 bg-brand-dark/5 rounded-xl border border-brand-dark/5 animate-in fade-in slide-in-from-top-1 duration-500">
                    <AlertCircle className="h-3.5 w-3.5 text-brand-dark shrink-0 mt-0.5" />
                    <p className="text-[10px] text-brand-dark font-bold leading-relaxed tracking-tight">
                      Nota: Copago superior al bono por exámenes sin cobertura Fonasa.
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
                          <Button
                            className={cn(
                              "w-full h-14 text-base font-black shadow-xl transition-all duration-500 uppercase tracking-tight rounded-2xl",
                              isReady
                                ? "bg-brand-mint hover:bg-brand-mint/90 text-brand-dark shadow-brand-mint/20 hover:scale-[1.02] active:scale-95"
                                : "bg-slate-100 text-slate-300"
                            )}
                            disabled={!isReady}
                            onClick={handleGenerarPDF}
                          >
                            {isGenerating ? <RefreshCw className="mr-2 h-5 w-5 animate-spin" /> : <FileDown className="mr-2 h-6 w-6" />}
                            Generar Cotización
                          </Button>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent className="bg-brand-dark text-white border-none shadow-xl py-2 px-4 text-[10px] font-black uppercase tracking-widest animate-in zoom-in-95">
                        {isReady 
                          ? "Click para generar tu PDF oficial"
                          : !aceptoTerminos 
                            ? "Debes aceptar los términos y condiciones"
                            : selectedExams.length === 0
                              ? "Selecciona al menos un examen"
                              : "Ingresa Rut del paciente para continuar"
                        }
                      </TooltipContent>
                    </Tooltip>
                    <Button
                      variant="ghost"
                      className="w-full text-slate-400 hover:text-brand-dark hover:bg-slate-50 text-[10px] uppercase font-black tracking-widest mt-1"
                      onClick={reset}
                    >
                      <RefreshCw className="mr-2 h-3.5 w-3.5" /> Limpiar Todo
                    </Button>
                  </>
                ) : (
                  <>
                    <Button variant="secondary" className="w-full h-14 text-base font-black text-brand-dark bg-brand-mint hover:bg-brand-mint/90 shadow-lg shadow-brand-mint/20 rounded-2xl ring-2 ring-brand-mint/50 ring-offset-2 ring-offset-brand-dark scale-100 hover:scale-[1.02] transition-all duration-300" asChild>
                      <a href={pdfUrl ? `${API_URL}${pdfUrl}` : '#'} target="_blank" download="cotizacion.pdf" rel="noopener noreferrer">
                        <FileDown className="mr-2 h-6 w-6" /> Descargar PDF
                      </a>
                    </Button>
                    <Button variant="ghost" className="w-full text-white/40 hover:text-white hover:bg-white/10 font-bold text-xs uppercase tracking-widest mt-2" onClick={reset}>
                      <RefreshCw className="mr-2 h-4 w-4" /> Nueva Cotización
                    </Button>
                  </>
                )}

                <Separator className={pdfUrl ? 'bg-white/10' : 'bg-slate-50'} />

                {/* Branch info integrated inside the main card */}
                <div className="w-full space-y-3 py-2 text-left">
                  <div className="flex items-center gap-2 px-1">
                    <MapPin className={`h-4 w-4 ${pdfUrl ? 'text-brand-mint' : 'text-slate-400'}`} />
                    <h4 className={`text-[10px] font-black uppercase tracking-widest ${pdfUrl ? 'text-white' : 'text-slate-500'}`}>Lugar de atención</h4>
                  </div>
                  <div className={`p-4 rounded-2xl border flex flex-col gap-2 ${pdfUrl ? 'bg-white/10 border-white/10 text-white/80' : 'bg-slate-50/50 border-slate-100 text-slate-500'}`}>
                    <p className="text-[10px] leading-relaxed font-bold">
                      Sucursal Vitacura: Av. Vitacura #8620 • +56 2 2933 6740
                    </p>
                    <p className="text-[9px] leading-relaxed opacity-60 font-medium">
                      Dirigirse a Recepción del 3er piso - Policlínico Tabancura
                    </p>
                    <div className="flex gap-2 pt-2">
                      <a href="https://www.policlinicotabancura.cl" target="_blank" className={`flex-1 text-[9px] font-black text-center py-2 rounded-xl uppercase border transition-all ${pdfUrl ? 'border-white/20 text-white hover:bg-white/10' : 'border-slate-200 text-brand-dark bg-white hover:bg-slate-50 hover:border-slate-300 shadow-sm'}`}>Sitio Web</a>
                      <a href="https://ff.healthatom.io/FKV7ZY" target="_blank" className={`flex-1 text-[9px] font-black text-center py-2 rounded-xl uppercase border transition-all ${pdfUrl ? 'border-white/20 text-brand-mint bg-white hover:bg-white/90' : 'border-brand-mint/20 text-brand-mint bg-brand-mint/5 hover:bg-brand-mint/10 shadow-sm'}`}>Agendar Hora</a>
                    </div>
                  </div>
                </div>
              </CardFooter>
            </Card>
          )}
        </div>
      </main>

      {/* STICKY MOBILE ACTION BAR - Visible only on mobile when items are selected */}
      {selectedExams.length > 0 && isPatientChecked && (
        <div className="fixed bottom-0 left-0 right-0 z-50 lg:hidden animate-in slide-in-from-bottom-full duration-500 bg-brand-dark/95 backdrop-blur-md border-t border-white/10 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.3)]">
          <div className="p-4 pb-[calc(1.5rem+env(safe-area-inset-bottom,0px))] flex flex-col gap-3">

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
                  <span className="text-[8px] font-black uppercase text-white/20 tracking-widest leading-none mb-0.5">
                    {isFonasa ? 'Bono Fonasa' : 'Arancel Gral.'}
                  </span>
                  <span className="text-xs font-bold text-white/40 leading-none tabular-nums">
                    ${totalV1.toLocaleString('es-CL')}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between gap-4">
              <div className="flex flex-col">
                <span className="text-[10px] font-black text-brand-mint uppercase tracking-widest leading-none mb-1">
                  {isFonasa ? 'Total Copago' : 'Mi Vita (Pref.)'}
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
                      <FileDown className="mr-2 h-4 w-4" />
                      PDF
                    </Button>
                  ) : (
                    currentStep === 3 ? (
                      <Button
                        className={cn(
                          "w-full h-12 rounded-xl font-black uppercase text-xs shadow-lg transition-all active:scale-95",
                          aceptoTerminos && nombre && prevision
                            ? "bg-brand-mint hover:bg-brand-mint/90 text-brand-dark shadow-brand-mint/20"
                            : "bg-slate-700 text-white/30"
                        )}
                        disabled={!aceptoTerminos || !nombre || !prevision || isGenerating}
                        onClick={handleGenerarPDF}
                      >
                        {isGenerating ? <RefreshCw className="h-4 w-4 animate-spin" /> : "Generar"}
                      </Button>
                    ) : (
                      <Button
                        className="w-full h-12 bg-brand-mint text-brand-dark rounded-xl font-black uppercase text-xs shadow-lg shadow-brand-mint/20"
                        onClick={() => {
                          if (currentStep === 1 && nombre && prevision && aceptoTerminos) setCurrentStep(2);
                          else if (currentStep === 2 && selectedExams.length > 0) setCurrentStep(3);
                          else if (currentStep === 1) toast.info("Por favor completa tus datos");
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

          <DialogFooter className="mt-6 flex flex-col gap-2 sm:flex-col sm:space-x-0 w-full">
            <Button className="w-full bg-brand-dark text-brand-mint hover:bg-brand-dark/90 font-black h-12 sm:h-14 text-sm sm:text-base shadow-lg shadow-brand-dark/20 rounded-xl transition-all active:scale-95" onClick={confirmPackage}>
              Confirmar y Agregar
            </Button>
            <Button variant="ghost" className="w-full font-black h-10 sm:h-12 text-sm sm:text-base text-brand-dark hover:bg-slate-100 rounded-xl transition-all active:scale-95" onClick={() => {
              setIsConfirmOpen(false);
              setPendingPackage(null);
            }}>
              Volver
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
                  window.open('https://ff.healthatom.io/FKV7ZY', '_blank');
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
                  className="border-slate-200 text-slate-600 font-bold h-11 text-xs flex items-center justify-center gap-2"
                  asChild
                >
                  <a href={pdfUrl ? `${API_URL}${pdfUrl}` : '#'} target="_blank" download="cotizacion.pdf" rel="noopener noreferrer">
                    <Download className="h-4 w-4" />
                    Descargar PDF
                  </a>
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
                <span className="text-[11px] text-slate-500 font-medium">Sucursal Vitacura, Av. Vitacura #8620 (+56 2 2933 6740)</span>
                <span className="text-[10px] text-slate-400 font-bold">Dirigirse a Recepción del 3er Piso</span>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
