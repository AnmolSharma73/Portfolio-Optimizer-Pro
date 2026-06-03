'use client';

import { useState } from 'react';

const SUPPORTED_FORMATS = [
  { from: 'DOCX', to: ['PDF', 'HTML', 'TXT'] },
  { from: 'PDF', to: ['TXT'] },
  { from: 'CSV', to: ['JSON'] },
  { from: 'JSON', to: ['CSV'] },
  { from: 'Markdown', to: ['HTML'] },
  { from: 'HTML', to: ['Markdown'] },
  { from: 'PNG', to: ['JPG', 'WebP'] },
  { from: 'JPG', to: ['PNG', 'WebP'] },
  { from: 'WebP', to: ['PNG', 'JPG'] },
];

export default function Header() {
  const [showFormats, setShowFormats] = useState(false);

  return (
    <header className="relative z-10 w-full">
      <div className="max-w-5xl mx-auto flex items-center justify-between px-6 py-5">
        {/* Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-violet-500/25">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 3v5a1 1 0 001 1h5" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 13l2 2 4-4" />
              </svg>
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-950 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">DocConvert</h1>
            <p className="text-xs text-slate-400 font-medium">Free Document Converter</p>
          </div>
        </div>

        {/* Supported Formats Button */}
        <div className="relative">
          <button
            id="formats-toggle"
            onClick={() => setShowFormats(!showFormats)}
            className="group flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-300 text-sm text-slate-300 hover:text-white"
          >
            <svg className="w-4 h-4 text-violet-400 group-hover:text-violet-300 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Supported Formats
            <svg className={`w-3 h-3 transition-transform duration-300 ${showFormats ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Formats Dropdown */}
          {showFormats && (
            <div className="absolute right-0 top-full mt-2 w-80 rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-white/10 shadow-2xl shadow-black/50 p-4 animate-in">
              <div className="grid gap-2">
                {SUPPORTED_FORMATS.map((fmt) => (
                  <div
                    key={fmt.from}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    <span className="text-xs font-bold text-violet-400 bg-violet-400/10 px-2 py-0.5 rounded-md min-w-[52px] text-center">
                      {fmt.from}
                    </span>
                    <svg className="w-3 h-3 text-slate-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    <div className="flex flex-wrap gap-1">
                      {fmt.to.map((t) => (
                        <span key={t} className="text-xs text-cyan-300 bg-cyan-400/10 px-2 py-0.5 rounded-md">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
