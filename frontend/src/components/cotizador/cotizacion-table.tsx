'use client';

import * as React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Trash2, Plus, Minus, Info, HelpCircle } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Examen } from '@/lib/api';

interface SelectedExamen {
  examen: Examen;
  cantidad: number;
}

interface CotizacionTableProps {
  items: SelectedExamen[];
  prevision: string;
  onUpdateCantidad: (codigo: string, cantidad: number) => void;
  onRemove: (codigo: string) => void;
  disabled?: boolean;
  isPackActive?: boolean;
}

export function CotizacionTable({ 
  items, 
  prevision, 
  onUpdateCantidad, 
  onRemove, 
  disabled, 
  isPackActive 
}: CotizacionTableProps) {
  if (items.length === 0) return null;

  const isFonasa = prevision === 'Fonasa';

  return (
    <div className="rounded-xl border bg-card overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-slate-50 border-b border-slate-100">
            <TableHead className="w-[85px] text-[10px] font-bold uppercase tracking-wider text-slate-400 pl-4">
              <div className="flex items-center gap-1">
                Cod.
                <Tooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="h-3 w-3 cursor-help text-slate-300 hover:text-brand-mint transition-colors" />
                  </TooltipTrigger>
                  <TooltipContent className="bg-brand-dark text-white border-none shadow-xl py-2 px-3 text-[10px] font-medium leading-relaxed max-w-[180px]">
                    Los códigos numéricos tienen cobertura Fonasa. Los códigos con letras son exclusivamente particulares.
                  </TooltipContent>
                </Tooltip>
              </div>
            </TableHead>
            <TableHead className="min-w-[150px] text-[10px] font-bold uppercase tracking-wider text-slate-400">Examen</TableHead>
            <TableHead className="text-center w-[95px] text-[10px] font-bold uppercase tracking-wider text-slate-400">Cant.</TableHead>
            <TableHead className="text-right w-[90px] text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {isFonasa ? 'Bono' : 'P. Gral'}
            </TableHead>
            <TableHead className="text-right w-[95px] text-[10px] font-bold uppercase tracking-wider text-slate-400 pr-2">
              {isFonasa ? 'Copago' : 'P. Pref'}
            </TableHead>
            {!disabled && !isPackActive && <TableHead className="w-[45px] pr-4"></TableHead>}
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => {
            const { examen, cantidad } = item;
            const v1 = isFonasa ? examen.valor_bono_fonasa : examen.valor_particular_general;
            const v2 = isFonasa ? (examen.valor_bono_fonasa > 0 ? examen.valor_copago : examen.valor_particular_general) : examen.valor_particular_preferencial;

            return (
              <TableRow key={examen.codigo} className="hover:bg-slate-50/50 border-b border-slate-50 transition-colors last:border-none">
                <TableCell className="font-medium text-[9px] text-slate-400 pl-4 py-2">{examen.codigo}</TableCell>
                <TableCell className="py-2">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="max-w-[180px] sm:max-w-[250px] lg:max-w-[320px] truncate cursor-help group flex items-center gap-1.5">
                        <span className="text-xs font-bold text-slate-700 group-hover:text-brand-mint transition-colors tracking-tight">{examen.nombre}</span>
                        <Info className="h-3 w-3 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-xs font-medium">
                      {examen.nombre}
                    </TooltipContent>
                  </Tooltip>
                </TableCell>
                <TableCell className="py-2">
                  <div className="flex items-center justify-center gap-1.5">
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-6 w-6 rounded-md border-slate-200"
                      onClick={() => onUpdateCantidad(examen.codigo, Math.max(1, cantidad - 1))}
                      disabled={disabled || isPackActive || cantidad <= 1}
                    >
                      <Minus className="h-2.5 w-2.5" />
                    </Button>
                    <span className="w-5 text-center text-[13px] font-bold text-slate-700">{cantidad}</span>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-6 w-6 rounded-md border-slate-200"
                      onClick={() => onUpdateCantidad(examen.codigo, Math.min(20, cantidad + 1))}
                      disabled={disabled || isPackActive || cantidad >= 20}
                    >
                      <Plus className="h-2.5 w-2.5" />
                    </Button>
                  </div>
                </TableCell>
                <TableCell className="text-right text-xs font-medium text-slate-600">
                  ${(v1 * cantidad).toLocaleString('es-CL')}
                </TableCell>
                <TableCell className="text-right text-sm font-black text-brand-dark pr-2">
                  ${(v2 * cantidad).toLocaleString('es-CL')}
                </TableCell>
                {!disabled && !isPackActive && (
                  <TableCell className="pr-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors"
                      onClick={() => onRemove(examen.codigo)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
