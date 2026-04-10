'use client';

import * as React from 'react';
import { Search, Package, PlusCircle, Zap } from 'lucide-react';
import { Command as CommandPrimitive } from 'cmdk';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/badge';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from '../ui/command';
import { Examen } from '../../lib/api';

interface ExamSearchProps {
  examenes: Examen[];
  onSelect: (examen: Examen) => void;
  onSearchChange?: (isSearching: boolean) => void;
  selectedIds?: string[];
  disabled?: boolean;
  placeholder?: string;
}

export function ExamSearch({
  examenes,
  onSelect,
  onSearchChange,
  selectedIds = [],
  disabled,
  placeholder = "Busca por nombre o código (Ej: 301041, Hemograma, Glucosa...)"
}: ExamSearchProps) {
  const [search, setSearch] = React.useState('');
  const [isFocused, setIsFocused] = React.useState(false);

  // 1. Prioritize UI responsiveness: Let search state update instantly, 
  // while the heavy filtering happens on a deferred value.
  const deferredSearch = React.useDeferredValue(search);

  // 2. High Performance Filtering: Filter the list EXTERNALLY.
  const filteredExamenes = React.useMemo(() => {
    if (!deferredSearch.trim()) {
      return [];
    }

    const keywords = deferredSearch.toLowerCase().split(/\s+/).filter(Boolean);
    const results = [];

    for (const ex of examenes) {
      const target = `${ex.nombre} ${ex.codigo} ${ex.busqueda || ''}`.toLowerCase();
      if (keywords.every(k => target.includes(k))) {
        results.push(ex);
      }
      if (results.length >= 100) break;
    }

    return results;
  }, [examenes, deferredSearch]);

  // Notify parent of search activity
  React.useEffect(() => {
    onSearchChange?.(search.length > 0);
  }, [search, onSearchChange]);

  return (
    <div className={cn(
      "w-full transition-all duration-500 animate-in fade-in slide-in-from-top-2",
      disabled && "opacity-50 pointer-events-none cursor-not-allowed grayscale"
    )}>
      <Command
        className={cn(
          "rounded-2xl border bg-white shadow-sm overflow-hidden transition-all duration-300 p-0",
          isFocused ? "border-brand-mint ring-4 ring-brand-mint/5 shadow-xl" : "border-slate-200"
        )}
        shouldFilter={false}
      >
        <div className="flex items-center border-b border-slate-100 bg-white sticky top-0 z-10 h-16 pr-4">
          <div className="flex items-center justify-center h-full w-14 shrink-0 px-1">
            {search && filteredExamenes.length > 0 ? (
              <div className="bg-brand-mint/10 p-2 rounded-xl">
                <Zap className="h-5 w-5 text-brand-mint animate-pulse" />
              </div>
            ) : (
              <div className="bg-slate-50 p-2 rounded-xl">
                <Search className={cn("h-5 w-5 transition-colors", isFocused ? "text-brand-mint" : "text-slate-400")} />
              </div>
            )}
          </div>

          <CommandPrimitive.Input
            placeholder={placeholder}
            value={search}
            onValueChange={setSearch}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            className="flex h-full w-full bg-transparent py-3 text-base outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-50 font-medium border-none focus:ring-0"
          />

          {selectedIds.length > 0 && (
            <Badge className="ml-2 bg-brand-mint text-white border-none text-[10px] h-7 px-3 font-black shrink-0 uppercase tracking-tighter shadow-sm flex items-center gap-1.5">
              <PlusCircle className="h-3 w-3" />
              {selectedIds.length} Seleccionados
            </Badge>
          )}
        </div>

        {search && (
          <CommandList className={cn(
            "max-h-[320px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 bg-slate-50/10 animate-in slide-in-from-top-1 duration-300",
            "opacity-100"
          )}>
            {filteredExamenes.length === 0 ? (
              <CommandEmpty className="py-12 flex flex-col items-center justify-center text-slate-400 gap-3">
                <Package className="h-10 w-10 opacity-10" />
                <p className="text-sm font-medium">No se encontraron exámenes</p>
              </CommandEmpty>
            ) : (
              <CommandGroup
                heading={
                  <div className="flex justify-between items-center w-full pr-2">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest px-1">
                      Resultados de Búsqueda
                    </span>
                    <span className="text-[9px] text-slate-300 font-bold uppercase tracking-tighter">
                      Encontrados: {filteredExamenes.length}
                    </span>
                  </div>
                }
                className="p-2"
              >
                {filteredExamenes.map((examen) => {
                  const isSelected = selectedIds.includes(examen.codigo);
                  return (
                    <CommandItem
                      key={examen.codigo}
                      value={`${examen.nombre} ${examen.codigo}`}
                      onSelect={() => {
                        onSelect(examen);
                        setSearch('');
                      }}
                      className={cn(
                        "group flex items-center gap-3 px-3 py-2 rounded-xl cursor-pointer transition-all m-1",
                        isSelected ? "bg-brand-mint/10" : "hover:bg-white hover:shadow-md border border-transparent hover:border-slate-100"
                      )}
                    >
                      <div className={cn(
                        "h-8 w-8 rounded-lg flex items-center justify-center shrink-0 transition-colors",
                        isSelected ? "bg-brand-mint text-white" : "bg-slate-100 group-hover:bg-brand-mint/10 text-slate-400 group-hover:text-brand-mint"
                      )}>
                        <PlusCircle className="h-4 w-4" />
                      </div>

                      <div className="flex items-center justify-between flex-1 gap-4 overflow-hidden">
                        <div className="flex flex-col gap-0.5 overflow-hidden">
                          <span
                            className={cn(
                              "text-xs font-bold truncate transition-colors",
                              isSelected ? "text-brand-dark" : "text-slate-700"
                            )}
                            title={examen.nombre}
                          >
                            {examen.nombre}
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="text-[9px] text-slate-400 font-mono font-bold">
                              #{examen.codigo}
                            </span>
                          </div>
                        </div>

                        <div className="shrink-0">
                          {isSelected ? (
                            <Badge className="bg-brand-dark text-brand-mint border-0 text-[8px] h-4.5 px-2 uppercase font-black tracking-tighter shadow-sm">
                              Agregado
                            </Badge>
                          ) : (
                            <span className="text-[10px] text-brand-mint opacity-0 group-hover:opacity-100 font-black uppercase tracking-tighter transition-all translate-x-1 group-hover:translate-x-0">
                              Añadir +
                            </span>
                          )}
                        </div>
                      </div>
                    </CommandItem>
                  );
                })}
              </CommandGroup>
            )}
          </CommandList>
        )}

        <div className="bg-slate-50/50 p-2 border-t border-slate-100 flex justify-between items-center px-4 h-8 text-[9px] text-slate-400 font-bold uppercase tracking-widest">
          <span className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-mint animate-pulse" />
            Valores actualizados en tiempo real
          </span>
          <span className="text-slate-300 normal-case font-medium italic">
            {search ? "Selecciona para añadir" : "Escriba para ver resultados"}
          </span>
        </div>
      </Command>
    </div>
  );
}
