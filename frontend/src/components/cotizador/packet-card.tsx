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
      className={`relative cursor-pointer transition-all duration-300 group hover:bg-brand-dark hover:text-white hover:border-brand-dark hover:shadow-xl ${active ? 'border-primary ring-1 ring-primary shadow-md bg-brand-dark text-white' : ''} h-full overflow-hidden`}
      onClick={() => onSelect(paquete)}
    >
      <div className="absolute top-2 right-2 opacity-0 -translate-y-1 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300">
        <PlusCircle className="h-5 w-5 text-brand-mint" />
      </div>

      <CardHeader className="p-3 pb-1">
        <div className={`flex items-center gap-1.5 mb-1 transition-colors ${active ? 'text-brand-mint' : 'text-primary group-hover:text-brand-mint'}`}>
          <Package className="h-4 w-4" />
          <span className="text-[10px] font-extrabold uppercase tracking-widest opacity-80">Pack Preventivo</span>
        </div>
        <CardTitle className="text-sm font-bold leading-tight">
          {paquete.nombre}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        <p className={`text-[11px] line-clamp-1 transition-colors ${active ? 'text-white/70' : 'text-muted-foreground group-hover:text-white/70'}`}>
          Incluye {paquete.examenes.length} exámenes especializados.
        </p>
      </CardContent>
    </Card>
  );
}
