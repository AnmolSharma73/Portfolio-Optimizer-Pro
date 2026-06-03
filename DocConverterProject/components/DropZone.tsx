'use client';

import { useState, useCallback, useRef } from 'react';
import { detectFormat, formatFileSize, MAX_SERVERLESS_PAYLOAD, FORMAT_REGISTRY } from '@/utils/formats';
import StatusBadge from './StatusBadge';

interface DropZoneProps {
  onFileAccepted: (file: File, format: string) => void;
  disabled?: boolean;
}

// Map format categories to colors for the file type icon
const CATEGORY_COLORS: Record<string, { bg: string; text: string; icon: string }> = {
  document: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: '📄' },
  data: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', icon: '📊' },
  image: { bg: 'bg-purple-500/20', text: 'text-purple-400', icon: '🖼️' },
  markup: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: '🔗' },
};

export default function DropZone({ onFileAccepted, disabled }: DropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileFormat, setFileFormat] = useState<string | null>(null);
  const [sizeStatus, setSizeStatus] = useState<'idle' | 'under-limit' | 'over-limit'>('idle');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    setError(null);
    setSelectedFile(file);

    // Detect the file format
    const format = detectFormat(file);
    if (!format) {
      setError(`Unsupported file type: ${file.name.split('.').pop()?.toUpperCase() || 'Unknown'}`);
      setFileFormat(null);
      setSizeStatus('idle');
      return;
    }

    setFileFormat(format);

    // Check file size against the serverless limit
    if (file.size <= MAX_SERVERLESS_PAYLOAD) {
      setSizeStatus('under-limit');
    } else {
      setSizeStatus('over-limit');
    }

    // Pass the file up to the parent component
    onFileAccepted(file, format);
  }, [onFileAccepted]);

  // ─── Drag & Drop Handlers ─────────────────────────────────────────────

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragOver(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [disabled, handleFile]);

  const handleClick = useCallback(() => {
    if (!disabled) fileInputRef.current?.click();
  }, [disabled]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const formatInfo = fileFormat ? FORMAT_REGISTRY[fileFormat] : null;
  const categoryStyle = formatInfo ? CATEGORY_COLORS[formatInfo.category] : null;

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Drop Zone */}
      <div
        id="drop-zone"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`
          relative group cursor-pointer rounded-2xl border-2 border-dashed
          transition-all duration-500 ease-out
          ${
            isDragOver
              ? 'border-violet-400 bg-violet-500/10 scale-[1.02] shadow-2xl shadow-violet-500/20'
              : selectedFile
                ? 'border-white/20 bg-white/[0.04]'
                : 'border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]'
          }
          ${disabled ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        {/* Animated gradient border glow on hover */}
        <div className={`
          absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700
          bg-gradient-to-r from-violet-500/10 via-cyan-500/10 to-violet-500/10
          ${isDragOver ? '!opacity-100' : ''}
        `} />

        <div className="relative z-10 flex flex-col items-center gap-5 p-10">
          {!selectedFile ? (
            /* ─── Empty State ───────────────────────────── */
            <>
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20 flex items-center justify-center border border-white/10 group-hover:border-white/20 transition-all duration-500 group-hover:scale-110">
                  <svg
                    className={`w-7 h-7 transition-all duration-500 ${isDragOver ? 'text-violet-300 -translate-y-1' : 'text-slate-400 group-hover:text-violet-400'}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                </div>
                {/* Floating particles on drag */}
                {isDragOver && (
                  <>
                    <div className="absolute -top-2 -left-2 w-2 h-2 bg-violet-400 rounded-full animate-float-1" />
                    <div className="absolute -top-1 right-0 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-float-2" />
                    <div className="absolute -bottom-1 -right-2 w-2 h-2 bg-violet-300 rounded-full animate-float-3" />
                  </>
                )}
              </div>
              <div className="text-center">
                <p className="text-base font-medium text-white mb-1">
                  {isDragOver ? 'Release to drop' : 'Drop your file here'}
                </p>
                <p className="text-sm text-slate-500">
                  or <span className="text-violet-400 hover:text-violet-300 transition-colors">browse files</span>
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {['DOCX', 'PDF', 'CSV', 'JSON', 'MD', 'HTML', 'PNG', 'JPG', 'WebP'].map((fmt) => (
                  <span key={fmt} className="text-[10px] font-medium text-slate-500 bg-white/5 px-2 py-0.5 rounded-full">
                    {fmt}
                  </span>
                ))}
              </div>
            </>
          ) : (
            /* ─── File Selected State ───────────────────── */
            <>
              <div className="flex items-center gap-4 w-full">
                {/* File type icon */}
                <div className={`w-14 h-14 rounded-xl ${categoryStyle?.bg || 'bg-slate-500/20'} flex items-center justify-center flex-shrink-0 text-2xl`}>
                  {categoryStyle?.icon || '📁'}
                </div>

                {/* File details */}
                <div className="flex-1 min-w-0">
                  <p className="text-base font-semibold text-white truncate">{selectedFile.name}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className={`text-xs font-bold ${categoryStyle?.text || 'text-slate-400'} bg-white/5 px-2 py-0.5 rounded-md uppercase`}>
                      {fileFormat}
                    </span>
                    <span className="text-xs text-slate-500">{formatFileSize(selectedFile.size)}</span>
                  </div>
                </div>

                {/* Change file button */}
                <button
                  id="change-file"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    setFileFormat(null);
                    setSizeStatus('idle');
                    setError(null);
                  }}
                  className="flex-shrink-0 p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all duration-300"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>

              {/* Size Status Badge */}
              {sizeStatus === 'over-limit' && (
                <div className="w-full">
                  <StatusBadge
                    status="compressing"
                    originalSize={selectedFile.size}
                    message={`File exceeds serverless limits (${formatFileSize(selectedFile.size)}). Optimizing/compressing locally first...`}
                  />
                </div>
              )}
              {sizeStatus === 'under-limit' && (
                <div className="w-full">
                  <StatusBadge
                    status="under-limit"
                    originalSize={selectedFile.size}
                  />
                </div>
              )}
            </>
          )}

          {/* Error display */}
          {error && (
            <div className="w-full px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-sm text-rose-300">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".docx,.pdf,.csv,.json,.md,.html,.htm,.png,.jpg,.jpeg,.webp"
        onChange={handleInputChange}
      />
    </div>
  );
}
