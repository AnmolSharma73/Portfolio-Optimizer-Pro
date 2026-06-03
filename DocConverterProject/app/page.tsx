'use client';

import { useState, useCallback } from 'react';
import Header from '@/components/Header';
import DropZone from '@/components/DropZone';
import ConversionPanel from '@/components/ConversionPanel';
import ConversionHistory from '@/components/ConversionHistory';
import StatusBadge from '@/components/StatusBadge';
import { compressFile, CompressionResult } from '@/utils/compressor';
import { convertFile, ConversionProgress } from '@/utils/converter';
import { MAX_SERVERLESS_PAYLOAD, formatFileSize } from '@/utils/formats';
import type { HistoryEntry } from '@/components/ConversionHistory';

export default function Home() {
  // ─── State ──────────────────────────────────────────────────────────────
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [sourceFormat, setSourceFormat] = useState<string | null>(null);
  const [compressionResult, setCompressionResult] = useState<CompressionResult | null>(null);
  const [compressionStatus, setCompressionStatus] = useState<
    'idle' | 'compressing' | 'compressed' | 'error'
  >('idle');
  const [conversionProgress, setConversionProgress] = useState<ConversionProgress | null>(null);
  const [isConverting, setIsConverting] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  // ─── File Accepted Handler ──────────────────────────────────────────────
  // This fires when DropZone detects a valid file. We then decide whether
  // to compress it before queuing for conversion.
  const handleFileAccepted = useCallback(async (file: File, format: string) => {
    setCurrentFile(file);
    setSourceFormat(format);
    setCompressionResult(null);
    setCompressionStatus('idle');
    setConversionProgress(null);

    // ─── SIZE CHECK: Does this file need compression? ─────────────────
    if (file.size > MAX_SERVERLESS_PAYLOAD) {
      // File exceeds 4.5 MB — trigger client-side compression
      setCompressionStatus('compressing');

      try {
        const result = await compressFile(file);
        setCompressionResult(result);

        if (result.success) {
          // Compression succeeded! Update the file reference to the
          // compressed version for conversion.
          setCurrentFile(result.file);
          setCompressionStatus('compressed');
        } else {
          // Compression failed or file type can't be compressed.
          // Show the error message but don't block the UI.
          setCompressionStatus('error');
        }
      } catch {
        setCompressionStatus('error');
        setCompressionResult({
          success: false,
          file,
          originalSize: file.size,
          compressedSize: file.size,
          message: 'An unexpected error occurred during compression.',
        });
      }
    } else {
      // File is under the limit — no compression needed
      setCompressionStatus('idle');
    }
  }, []);

  // ─── Convert Handler ───────────────────────────────────────────────────
  const handleConvert = useCallback(async (targetFormat: string) => {
    if (!currentFile || !sourceFormat) return;

    setIsConverting(true);
    setConversionProgress(null);

    try {
      await convertFile(
        { file: currentFile, targetFormat },
        (progress) => setConversionProgress(progress)
      );

      // Add to history on success
      setHistory((prev) => [
        {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          sourceFileName: currentFile.name,
          sourceFormat,
          targetFormat,
          originalSize: currentFile.size,
          timestamp: new Date(),
          success: true,
        },
        ...prev,
      ]);
    } catch {
      // Add failed conversion to history
      setHistory((prev) => [
        {
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          sourceFileName: currentFile.name,
          sourceFormat,
          targetFormat,
          originalSize: currentFile.size,
          timestamp: new Date(),
          success: false,
        },
        ...prev,
      ]);
    } finally {
      setIsConverting(false);
    }
  }, [currentFile, sourceFormat]);

  // ─── Clear History ──────────────────────────────────────────────────────
  const handleClearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-8 -mt-8">
        {/* Hero Section */}
        <div className="text-center mb-10 animate-in">
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-3">
            <span className="text-gradient">Convert</span>{' '}
            <span className="text-white">Any File</span>
          </h2>
          <p className="text-slate-400 text-base sm:text-lg max-w-xl mx-auto leading-relaxed">
            Drop your document, image, or data file below. Large files are{' '}
            <span className="text-violet-400 font-medium">automatically optimized</span>{' '}
            in your browser before conversion.
          </p>
        </div>

        {/* Drop Zone */}
        <DropZone
          onFileAccepted={handleFileAccepted}
          disabled={isConverting}
        />

        {/* Compression Status (shows when compressing large files) */}
        {compressionStatus !== 'idle' && compressionResult && (
          <div className="w-full max-w-2xl mx-auto mt-4 animate-in">
            <StatusBadge
              status={
                compressionStatus === 'compressing'
                  ? 'compressing'
                  : compressionStatus === 'compressed'
                    ? 'compressed'
                    : 'error'
              }
              originalSize={compressionResult.originalSize}
              compressedSize={compressionResult.compressedSize}
              message={compressionResult.message}
            />
          </div>
        )}

        {/* Conversion Panel (appears when a file is selected) */}
        <ConversionPanel
          sourceFormat={sourceFormat}
          onConvert={handleConvert}
          progress={conversionProgress}
          disabled={compressionStatus === 'error' || compressionStatus === 'compressing'}
        />

        {/* Conversion History */}
        <ConversionHistory
          entries={history}
          onClear={handleClearHistory}
        />

        {/* Footer Info */}
        <div className="mt-12 text-center animate-in" style={{ animationDelay: '0.3s' }}>
          <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-600">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-emerald-400/50 rounded-full" />
              <span>Files processed locally</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-violet-400/50 rounded-full" />
              <span>Auto-compression for large files</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-cyan-400/50 rounded-full" />
              <span>Max {formatFileSize(MAX_SERVERLESS_PAYLOAD)} per upload</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
