'use client';

import { formatFileSize } from '@/utils/formats';

export interface HistoryEntry {
  id: string;
  sourceFileName: string;
  sourceFormat: string;
  targetFormat: string;
  originalSize: number;
  timestamp: Date;
  success: boolean;
}

interface ConversionHistoryProps {
  entries: HistoryEntry[];
  onClear: () => void;
}

export default function ConversionHistory({ entries, onClear }: ConversionHistoryProps) {
  if (entries.length === 0) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-400 flex items-center gap-2">
          <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Recent Conversions
        </h3>
        <button
          id="clear-history"
          onClick={onClear}
          className="text-xs text-slate-500 hover:text-rose-400 transition-colors px-2 py-1 rounded-lg hover:bg-rose-400/10"
        >
          Clear
        </button>
      </div>

      <div className="space-y-2">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="group flex items-center gap-4 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] hover:border-white/10 transition-all duration-300"
          >
            {/* Status icon */}
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
              entry.success
                ? 'bg-emerald-400/10 text-emerald-400'
                : 'bg-rose-400/10 text-rose-400'
            }`}>
              {entry.success ? (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </div>

            {/* File info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium truncate">{entry.sourceFileName}</p>
              <p className="text-xs text-slate-500">
                {formatFileSize(entry.originalSize)} · {entry.timestamp.toLocaleTimeString()}
              </p>
            </div>

            {/* Conversion arrow */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className="text-xs font-bold text-violet-400 bg-violet-400/10 px-2 py-0.5 rounded-md uppercase">
                {entry.sourceFormat}
              </span>
              <svg className="w-3 h-3 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              <span className="text-xs font-bold text-cyan-400 bg-cyan-400/10 px-2 py-0.5 rounded-md uppercase">
                {entry.targetFormat}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
