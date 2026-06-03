'use client';

import { useState, useEffect } from 'react';
import { getTargetFormats, FormatInfo } from '@/utils/formats';
import { ConversionProgress } from '@/utils/converter';

interface ConversionPanelProps {
  sourceFormat: string | null;
  onConvert: (targetFormat: string) => void;
  progress: ConversionProgress | null;
  disabled?: boolean;
}

export default function ConversionPanel({
  sourceFormat,
  onConvert,
  progress,
  disabled,
}: ConversionPanelProps) {
  const [targetFormat, setTargetFormat] = useState<string>('');
  const [targets, setTargets] = useState<FormatInfo[]>([]);

  useEffect(() => {
    if (sourceFormat) {
      const available = getTargetFormats(sourceFormat);
      setTargets(available);
      // Auto-select first target
      if (available.length > 0) {
        setTargetFormat(available[0].extension.replace('.', ''));
      }
    } else {
      setTargets([]);
      setTargetFormat('');
    }
  }, [sourceFormat]);

  if (!sourceFormat) return null;

  const isConverting = progress?.stage === 'uploading' || progress?.stage === 'converting' || progress?.stage === 'downloading';
  const isComplete = progress?.stage === 'complete';
  const isError = progress?.stage === 'error';

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 animate-in">
      <div className="rounded-2xl bg-white/[0.03] border border-white/[0.08] p-6 backdrop-blur-sm">
        {/* Format Selection */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex items-center gap-3 flex-1">
            {/* Source format badge */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-violet-400 bg-violet-400/10 px-3 py-1.5 rounded-lg uppercase">
                {sourceFormat}
              </span>
            </div>

            {/* Arrow */}
            <div className="relative">
              <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              {isConverting && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </div>

            {/* Target format selector */}
            <div className="flex gap-2 flex-wrap">
              {targets.map((t) => {
                const fmt = t.extension.replace('.', '');
                const isSelected = targetFormat === fmt;
                return (
                  <button
                    key={fmt}
                    id={`target-${fmt}`}
                    onClick={() => setTargetFormat(fmt)}
                    disabled={isConverting}
                    className={`
                      px-3 py-1.5 rounded-lg text-sm font-bold uppercase transition-all duration-300
                      ${isSelected
                        ? 'bg-cyan-400/20 text-cyan-300 border border-cyan-400/30 shadow-lg shadow-cyan-500/10'
                        : 'bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10 hover:text-white'
                      }
                      ${isConverting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                  >
                    {fmt}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Convert Button */}
          <button
            id="convert-button"
            onClick={() => onConvert(targetFormat)}
            disabled={!targetFormat || isConverting || disabled}
            className={`
              relative px-6 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300
              ${isConverting
                ? 'bg-violet-500/20 text-violet-300 cursor-wait'
                : isComplete
                  ? 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30'
                  : 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white hover:from-violet-500 hover:to-cyan-500 hover:shadow-lg hover:shadow-violet-500/25 active:scale-95'
              }
              ${disabled || !targetFormat ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isConverting ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </span>
            ) : isComplete ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                Done!
              </span>
            ) : (
              'Convert'
            )}
          </button>
        </div>

        {/* Progress / Status Message */}
        {progress && (
          <div className={`mt-4 flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-500 ${
            isError
              ? 'bg-rose-500/10 border border-rose-500/20'
              : isComplete
                ? 'bg-emerald-500/10 border border-emerald-500/20'
                : 'bg-white/[0.03] border border-white/[0.06]'
          }`}>
            {/* Progress icon */}
            <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
              isError ? 'bg-rose-400/20 text-rose-400' :
              isComplete ? 'bg-emerald-400/20 text-emerald-400' :
              'bg-violet-400/20 text-violet-400'
            }`}>
              {isError ? (
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : isComplete ? (
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <div className="w-3 h-3 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
              )}
            </div>
            <p className={`text-sm ${
              isError ? 'text-rose-300' : isComplete ? 'text-emerald-300' : 'text-slate-300'
            }`}>
              {progress.message}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
