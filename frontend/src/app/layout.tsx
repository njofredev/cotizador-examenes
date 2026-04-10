import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "../components/ui/tooltip";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Cotizador Digital | Policlínico Tabancura",
  description: "Plataforma de cotización de exámenes preventivos y aranceles Fonasa/Particular.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${inter.className} antialiased bg-slate-50`}>
        <TooltipProvider>{children}</TooltipProvider>
      </body>
    </html>
  );
}
