'use client';

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Package, PlusCircle } from 'lucide-react';
import { Paquete } from '../../lib/api';

interface PacketCardProps {
  paquete: Paquete;
  active: boolean;
  onSelect: (paquete: Paquete) => void;
}

export function PacketCard({ paquete, active, onSelect }: PacketCardProps) {
  return (
    <Card 
      className={`relative cursor-pointer transition-all duration-300 group hover:bg-brand-dark hover:text-white border-slate-100 hover:border-brand-dark hover:shadow-2xl rounded-2xl ${active ? 'border-brand-mint ring-2 ring-brand-mint/20 shadow-lg bg-brand-dark text-white' : 'bg-white'} h-full overflow-hidden active:scale-95`}
      onClick={() => onSelect(paquete)}
    >
      <div className={`absolute top-3 right-3 transition-all duration-300 ${active ? 'opacity-100' : 'opacity-0 -translate-y-1 group-hover:opacity-100 group-hover:translate-y-0'}`}>
        <PlusCircle className="h-5 w-5 text-brand-mint" />
      </div>

      <CardHeader className="p-4 pb-1">
        <div className={`flex items-center gap-2 mb-1.5 transition-colors ${active ? 'text-brand-mint' : 'text-primary group-hover:text-brand-mint'}`}>
          <Package className="h-4 w-4" />
          <span className="text-[10px] font-black uppercase tracking-widest opacity-80">Pack Preventivo</span>
        </div>
        <CardTitle className="text-[15px] font-black leading-tight tracking-tight">
          {paquete.nombre}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-1">
        <p className={`text-[11px] font-bold line-clamp-1 transition-colors ${active ? 'text-white/60' : 'text-slate-400 group-hover:text-white/60'}`}>
          {paquete.examenes.length} exámenes especializados
        </p>
      </CardContent>
    </Card>
  );
}
