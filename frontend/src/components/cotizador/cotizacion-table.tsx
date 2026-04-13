'use client';

import * as React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Trash2, Plus, Minus, Info, HelpCircle } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "../ui/tooltip";
import { Examen } from '../../lib/api';

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
    <div className="space-y-4">
      {/* Desktop Table: Hidden on small screens */}
      <div className="rounded-xl border bg-card overflow-hidden hidden md:block shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 border-b border-slate-100">
              <TableHead className="w-[85px] text-[10px] font-black uppercase tracking-widest text-slate-400 pl-6">
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
              <TableHead className="min-w-[150px] text-[10px] font-black uppercase tracking-widest text-slate-400">Nombre del Examen</TableHead>
              <TableHead className="text-center w-[110px] text-[10px] font-black uppercase tracking-widest text-slate-400">Cantidad</TableHead>
              <TableHead className="text-right w-[110px] text-[10px] font-black uppercase tracking-widest text-slate-400">
                {isFonasa ? 'Bono Unit.' : 'P. Gral'}
              </TableHead>
              <TableHead className="text-right w-[110px] text-[10px] font-black uppercase tracking-widest text-slate-400 pr-6">
                {isFonasa ? 'Copago Total' : 'P. Pref'}
              </TableHead>
              {!disabled && !isPackActive && <TableHead className="w-[50px] pr-6"></TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => {
              const { examen, cantidad } = item;
              const v1 = isFonasa ? examen.valor_bono_fonasa : examen.valor_particular_general;
              const v2 = isFonasa ? (examen.valor_bono_fonasa > 0 ? examen.valor_copago : examen.valor_particular_general) : examen.valor_particular_preferencial;

              return (
                <TableRow key={examen.codigo} className="hover:bg-slate-50/50 border-b border-slate-50 transition-colors last:border-none">
                  <TableCell className="font-mono text-[9px] text-slate-400 pl-6 py-4">{examen.codigo}</TableCell>
                  <TableCell className="py-4">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="max-w-[180px] sm:max-w-[250px] lg:max-w-[320px] truncate cursor-help group flex items-center gap-2">
                          <span className="text-[13px] font-bold text-slate-700 group-hover:text-brand-mint transition-colors tracking-tight">{examen.nombre}</span>
                          <Info className="h-3.5 w-3.5 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                        </div>
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs text-xs font-semibold py-2 px-3">
                        {examen.nombre}
                      </TooltipContent>
                    </Tooltip>
                  </TableCell>
                  <TableCell className="py-2">
                    <div className="flex items-center justify-center gap-2">
                      <Button
                        variant="outline"
                        size="icon"
                        className="h-7 w-7 rounded-lg border-slate-200 shadow-sm hover:border-brand-mint hover:text-brand-mint transition-all"
                        onClick={() => onUpdateCantidad(examen.codigo, Math.max(1, cantidad - 1))}
                        disabled={disabled || isPackActive || cantidad <= 1}
                      >
                        <Minus className="h-3 w-3" />
                      </Button>
                      <span className="w-6 text-center text-sm font-black text-slate-800">{cantidad}</span>
                      <Button
                        variant="outline"
                        size="icon"
                        className="h-7 w-7 rounded-lg border-slate-200 shadow-sm hover:border-brand-mint hover:text-brand-mint transition-all"
                        onClick={() => onUpdateCantidad(examen.codigo, Math.min(20, cantidad + 1))}
                        disabled={disabled || isPackActive || cantidad >= 20}
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-xs font-bold text-slate-400">
                    ${(v1 * cantidad).toLocaleString('es-CL')}
                  </TableCell>
                  <TableCell className="text-right text-[15px] font-black text-brand-dark pr-6">
                    ${(v2 * cantidad).toLocaleString('es-CL')}
                  </TableCell>
                  {!disabled && !isPackActive && (
                    <TableCell className="pr-6">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-9 w-9 text-slate-300 hover:text-red-500 hover:bg-red-50 transition-all rounded-xl"
                        onClick={() => onRemove(examen.codigo)}
                      >
                        <Trash2 className="h-4.5 w-4.5" />
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Card List: Hidden on desktop */}
      <div className="grid grid-cols-1 gap-3 md:hidden">
        {items.map((item) => {
          const { examen, cantidad } = item;
          const v1 = isFonasa ? examen.valor_bono_fonasa : examen.valor_particular_general;
          const v2 = isFonasa ? (examen.valor_bono_fonasa > 0 ? examen.valor_copago : examen.valor_particular_general) : examen.valor_particular_preferencial;

          return (
            <div key={examen.codigo} className="bg-white rounded-2xl p-3.5 border border-slate-100 shadow-sm relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-1 h-full bg-brand-mint" />
              
              {/* Row 1: Code & Name */}
              <div className="flex justify-between items-start gap-3 mb-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="shrink-0 text-[9px] font-black text-brand-mint font-mono tracking-tighter bg-brand-mint/5 px-1.5 py-0.5 rounded-md border border-brand-mint/10">
                    #{examen.codigo}
                  </span>
                  <h4 className="text-[14px] font-black text-slate-800 leading-tight tracking-tight truncate">
                    {examen.nombre}
                  </h4>
                </div>
                {!disabled && !isPackActive && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all shrink-0 -mt-1 -mr-1"
                    onClick={() => onRemove(examen.codigo)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>

              {/* Row 2: Pricing Details (Small text) */}
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-3 px-0.5">
                <div className="flex items-center gap-1">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">P. Gral:</span>
                  <span className="text-[10px] font-bold text-slate-500 tabular-nums">${(v1 * cantidad).toLocaleString('es-CL')}</span>
                </div>
                <div className="flex items-center gap-1 border-l border-slate-100 pl-3">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">
                    {isFonasa ? 'Bono:' : 'P. Pref:'}
                  </span>
                  <span className="text-[10px] font-black text-brand-mint tabular-nums">${(v2 * cantidad).toLocaleString('es-CL')}</span>
                </div>
              </div>

              {/* Row 3: Action & Total */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-50">
                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 rounded-lg border-slate-200 bg-white shadow-sm flex items-center justify-center active:scale-95 transition-all"
                    onClick={() => onUpdateCantidad(examen.codigo, Math.max(1, cantidad - 1))}
                    disabled={disabled || isPackActive || cantidad <= 1}
                  >
                    <Minus className="h-3.5 w-3.5" />
                  </Button>
                  <span className="text-sm font-black text-slate-800 w-4 text-center font-mono">{cantidad}</span>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 rounded-lg border-slate-200 bg-white shadow-sm flex items-center justify-center active:scale-95 transition-all"
                    onClick={() => onUpdateCantidad(examen.codigo, Math.min(20, cantidad + 1))}
                    disabled={disabled || isPackActive || cantidad >= 20}
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>
                </div>

                <div className="text-right">
                  <span className="text-[14px] font-black text-brand-dark leading-none tracking-tighter tabular-nums">
                    ${(v2 * cantidad).toLocaleString('es-CL')}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
