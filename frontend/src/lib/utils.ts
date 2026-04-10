import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatRut(value: string) {
  // Clean input and limit to 9 chars
  const clean = value.replace(/[^0-9kK]/g, '').slice(0, 9);
  if (clean.length <= 1) return clean;
  
  // Format as XXXXXXXX-X
  const body = clean.slice(0, -1);
  const dv = clean.slice(-1);
  return `${body}-${dv}`;
}
