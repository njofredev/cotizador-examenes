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
  const examLimit = 3;
  
  return (
    <Card 
      className={`relative cursor-pointer transition-all duration-500 group border-slate-100 hover:border-brand-dark hover:shadow-2xl rounded-2xl ${active ? 'border-brand-mint ring-2 ring-brand-mint/20 shadow-lg bg-brand-dark' : 'bg-white'} h-full overflow-hidden active:scale-[0.98] flex flex-col`}
      onClick={() => onSelect(paquete)}
    >
      <div className={`absolute top-3 right-3 transition-all duration-300 ${active ? 'opacity-100' : 'opacity-0 -translate-y-1 group-hover:opacity-100 group-hover:translate-y-0'}`}>
        <PlusCircle className="h-4 w-4 text-brand-mint" />
      </div>

      <CardHeader className="p-4 flex-none">
        <div className={`flex items-center gap-2 mb-1.5 transition-colors ${active ? 'text-brand-mint' : 'text-slate-400 group-hover:text-brand-mint'}`}>
          <Package className="h-3.5 w-3.5" />
          <span className="text-[9px] font-black uppercase tracking-widest opacity-80">Pack Preventivo</span>
        </div>
        <CardTitle className={`text-[14px] font-black leading-tight tracking-tight transition-colors duration-300 ${active ? 'text-white' : 'text-slate-800 group-hover:text-white'}`}>
          {paquete.nombre}
        </CardTitle>
      </CardHeader>

      <CardContent className="p-4 pt-0 flex-1 relative overflow-hidden flex flex-col justify-end min-h-[40px]">
        {/* DEFAULT VIEW: Shown on mobile and as desktop base state */}
        <div className={`transition-all duration-500 ${active ? 'opacity-0 -translate-y-4' : 'opacity-100 group-hover:opacity-0 group-hover:-translate-y-4'}`}>
          <p className={`text-[11px] font-bold transition-colors ${active ? 'text-white/40' : 'text-slate-400 group-hover:text-white/40'}`}>
            {paquete.examenes.length} exámenes especializados
          </p>
        </div>

        {/* DESKTOP HOVER PEEK: Only for screen sizes >= sm and triggered on hover or active */}
        <div className={`hidden sm:flex absolute inset-x-4 bottom-4 flex-col gap-2 transition-all duration-500 ${active ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8 group-hover:opacity-100 group-hover:translate-y-0'}`}>
          <ul className="space-y-1">
            {paquete.examenes.slice(0, examLimit).map((ex, i) => (
              <li key={i} className="flex items-center gap-1.5 text-[10px] font-bold text-white/90 leading-none">
                <div className="h-1 w-1 rounded-full bg-brand-mint shrink-0" />
                <span className="truncate">{ex.nombre}</span>
              </li>
            ))}
          </ul>
          {paquete.examenes.length > examLimit && (
            <p className="text-[9px] font-black text-brand-mint uppercase tracking-widest pl-2.5">
              + {paquete.examenes.length - examLimit} adicionales
            </p>
          )}
        </div>
      </CardContent>

      {/* Decorative hover bg - only for non-active states to avoid flickering */}
      {!active && (
        <div className="absolute inset-0 bg-brand-dark -z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      )}
    </Card>
  );
}

// Helper for conditional logic in JSX
function iif(condition: boolean, a: any, b: any) {
    return condition ? a : b;
}
