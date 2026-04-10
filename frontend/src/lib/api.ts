import axios from 'axios';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://apicotizador.policlinicotabancura.cl';

export interface Examen {
  codigo: string;
  nombre: string;
  valor_bono_fonasa: number;
  valor_copago: number;
  valor_particular_general: number;
  valor_particular_preferencial: number;
  busqueda: string;
}

export interface Paquete {
  nombre: string;
  examenes: {
    codigo: string | null;
    nombre: string;
    cantidad: number;
  }[];
}

export const getExamenes = () => axios.get<Examen[]>(`${API_URL}/api/examenes`);
export const getPaquetes = () => axios.get<Paquete[]>(`${API_URL}/api/paquetes`);
export const getPaciente = (docId: string) => axios.get(`${API_URL}/api/paciente/${docId}`);
export const postCotizar = (data: any) => axios.post(`${API_URL}/api/cotizar`, data);
