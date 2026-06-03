'use client';

import { formatFileSize } from '@/utils/formats';

type BadgeStatus =
  | 'idle'
  | 'under-limit'
  | 'compressing'
  | 'compressed'
  | 'error'
  | 'uploading'
  | 'converting'
  | 'complete';

interface StatusBadgeProps {
  status: BadgeStatus;
  originalSize?: number;
  compressedSize?: number;
  message?: string;
}

const STATUS_CONFIG: Record<BadgeStatus, { color: string; bgColor: string; icon: string; label: string }> = {
  idle: {
    color: 'text-slate-400',
    bgColor: 'bg-slate-400/10 border-slate-400/20',
    icon: '○',
    label: 'Ready',
  },
  'under-limit': {
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10 border-emerald-400/20',
    icon: '✓',
    label: 'Within size limits',
  },
  compressing: {
    color: 'text-amber-400',
    bgColor: 'bg-amber-400/10 border-amber-400/20 animate-pulse',
    icon: '⟳',
    label: 'Optimizing locally...',
  },
  compressed: {
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10 border-emerald-400/20',
    icon: '✓',
    label: 'Optimized',
  },
  error: {
    color: 'text-rose-400',
    bgColor: 'bg-rose-400/10 border-rose-400/20',
    icon: '✕',
    label: 'Cannot process',
  },
  uploading: {
    color: 'text-blue-400',
    bgColor: 'bg-blue-400/10 border-blue-400/20 animate-pulse',
    icon: '↑',
    label: 'Uploading...',
  },
  converting: {
    color: 'text-violet-400',
    bgColor: 'bg-violet-400/10 border-violet-400/20 animate-pulse',
    icon: '⟳',
    label: 'Converting...',
  },
  complete: {
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10 border-emerald-400/20',
    icon: '✓',
    label: 'Complete!',
  },
};

export default function StatusBadge({ status, originalSize, compressedSize, message }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];

  if (status === 'idle') return null;

  return (
    <div className={`inline-flex flex-col gap-1 px-4 py-2.5 rounded-xl border ${config.bgColor} transition-all duration-500`}>
      <div className="flex items-center gap-2">
        <span className={`text-sm ${config.color} ${status === 'compressing' || status === 'converting' ? 'animate-spin-slow' : ''}`}>
          {config.icon}
        </span>
        <span className={`text-sm font-medium ${config.color}`}>
          {config.label}
        </span>
        {originalSize !== undefined && (
          <span className="text-xs text-slate-500">
            {formatFileSize(originalSize)}
            {compressedSize !== undefined && compressedSize !== originalSize && (
              <> → {formatFileSize(compressedSize)}</>
            )}
          </span>
        )}
      </div>
      {message && (
        <p className="text-xs text-slate-400 max-w-sm leading-relaxed">{message}</p>
      )}
    </div>
  );
}
