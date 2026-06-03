import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DocConvert — Free Document Converter",
  description:
    "Convert documents, images, and data files instantly. Supports DOCX, PDF, CSV, JSON, Markdown, HTML, PNG, JPG, and WebP. Client-side compression for large files.",
  keywords: [
    "document converter",
    "file converter",
    "DOCX to PDF",
    "CSV to JSON",
    "Markdown to HTML",
    "image converter",
    "free converter",
  ],
  openGraph: {
    title: "DocConvert — Free Document Converter",
    description: "Convert documents, images, and data files instantly. Free and private.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-mesh grid-pattern antialiased" style={{ fontFamily: "'Inter', sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
