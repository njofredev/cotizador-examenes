import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "../components/ui/tooltip";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Cotizador Digital | Policlínico Tabancura",
  description: "Plataforma de cotización de exámenes preventivos y aranceles Fonasa/Particular.",
  icons: {
    icon: "/logo_vec.svg",
  },
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
        {/* Script para avisar al padre (WordPress) la altura del contenido */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                function sendHeight() {
                  var height = document.body.scrollHeight;
                  window.parent.postMessage({ type: 'resize', height: height }, '*');
                }
                window.addEventListener('load', sendHeight);
                window.addEventListener('resize', sendHeight);
                // Reportar cada vez que el DOM cambie (por si se abren modales o expansiones)
                var observer = new MutationObserver(sendHeight);
                observer.observe(document.body, { attributes: true, childList: true, subtree: true });
                // Reportar periódicamente por si acaso
                setInterval(sendHeight, 1000);
              })();
            `,
          }}
        />
      </body>
    </html>
  );
}
