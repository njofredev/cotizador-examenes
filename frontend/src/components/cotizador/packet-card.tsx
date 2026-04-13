'use client';

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Package, PlusCircle, CheckCircle2 } from 'lucide-react';
import { Paquete } from '../../lib/api';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "../ui/tooltip";

interface PacketCardProps {
  paquete: Paquete;
  active: boolean;
  onSelect: (paquete: Paquete) => void;
}

export function PacketCard({ paquete, active, onSelect }: PacketCardProps) {
  return (
    <Card 
      className={`relative cursor-pointer transition-all duration-300 group hover:border-brand-dark hover:shadow-2xl rounded-2xl ${active ? 'border-brand-mint ring-2 ring-brand-mint/20 shadow-lg bg-brand-dark text-white' : 'bg-white border-slate-100'} h-full overflow-hidden active:scale-95`}
      onClick={() => onSelect(paquete)}
    >
      {/* DEFAULT CONTENT: Title and count */}
      <div className={`transition-all duration-500 ${active ? 'opacity-0 scale-95' : 'group-hover:opacity-0 group-hover:scale-95'}`}>
        <div className={`absolute top-3 right-3 transition-all duration-300 ${active ? 'opacity-100' : 'opacity-0 -translate-y-1 group-hover:opacity-100 group-hover:translate-y-0'}`}>
          <PlusCircle className="h-5 w-5 text-brand-mint" />
        </div>

        <CardHeader className="p-4 pb-1">
          <div className={`flex items-center gap-2 mb-1.5 transition-colors ${active ? 'text-brand-mint' : 'text-primary group-hover:text-brand-mint'}`}>
            <Package className="h-4 w-4" />
            <span className="text-[10px] font-black uppercase tracking-widest opacity-80">Pack Preventivo</span>
          </div>
          <CardTitle className="text-[15px] font-black leading-tight tracking-tight text-slate-800">
            {paquete.nombre}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 pt-1">
          <p className="text-[11px] font-bold text-slate-400">
            {paquete.examenes.length} exámenes especializados
          </p>
        </CardContent>
      </div>

      {/* HOVER/ACTIVE OVERLAY: Mini list of exams */}
      <div className={`absolute inset-0 bg-brand-dark p-4 flex flex-col justify-center transition-all duration-500 ${active ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 pointer-events-none'}`}>
        <div className="space-y-3">
          <div className="flex items-center gap-2 border-b border-white/10 pb-2">
            <Package className="h-3.5 w-3.5 text-brand-mint" />
            <span className="text-[9px] font-black uppercase tracking-widest text-brand-mint/80">Incluye este Pack</span>
          </div>
          <ul className="space-y-1.5">
            {paquete.examenes.slice(0, iif(paquete.examenes.length > 6, 5, 6)).map((ex, i) => (
              <li key={i} className="flex items-start gap-2 text-[10px] font-bold text-white leading-tight">
                <CheckCircle2 className="h-3 w-3 text-brand-mint shrink-0 mt-0.5" />
                <span className="line-clamp-2">{ex.nombre}</span>
              </li>
            ))}
            {paquete.examenes.length > (iif(paquete.examenes.length > 6, 5, 6)) && (
              <li className="text-[9px] font-black text-brand-mint/50 uppercase tracking-tighter pl-5 pt-1">
                + {paquete.examenes.length - 5} adicionales
              </li>
            )}
          </ul>
        </div>
      </div>
    </Card>
  );
}

// Helper for conditional logic in JSX
function iif(condition: boolean, a: any, b: any) {
    return condition ? a : b;
}
