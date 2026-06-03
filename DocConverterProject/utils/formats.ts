/**
 * FORMAT MAPPING & CONVERSION MATRIX
 * -----------------------------------
 * This module defines all supported file formats, their MIME types,
 * file extensions, and which target formats each source can convert to.
 */

export interface FormatInfo {
  extension: string;
  mimeType: string;
  label: string;
  category: 'document' | 'data' | 'image' | 'markup';
}

// Master registry of all supported formats
export const FORMAT_REGISTRY: Record<string, FormatInfo> = {
  // Documents
  docx: {
    extension: '.docx',
    mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    label: 'Word Document',
    category: 'document',
  },
  pdf: {
    extension: '.pdf',
    mimeType: 'application/pdf',
    label: 'PDF',
    category: 'document',
  },
  txt: {
    extension: '.txt',
    mimeType: 'text/plain',
    label: 'Plain Text',
    category: 'document',
  },

  // Data
  csv: {
    extension: '.csv',
    mimeType: 'text/csv',
    label: 'CSV',
    category: 'data',
  },
  json: {
    extension: '.json',
    mimeType: 'application/json',
    label: 'JSON',
    category: 'data',
  },

  // Markup
  md: {
    extension: '.md',
    mimeType: 'text/markdown',
    label: 'Markdown',
    category: 'markup',
  },
  html: {
    extension: '.html',
    mimeType: 'text/html',
    label: 'HTML',
    category: 'markup',
  },

  // Images
  png: {
    extension: '.png',
    mimeType: 'image/png',
    label: 'PNG Image',
    category: 'image',
  },
  jpg: {
    extension: '.jpg',
    mimeType: 'image/jpeg',
    label: 'JPEG Image',
    category: 'image',
  },
  webp: {
    extension: '.webp',
    mimeType: 'image/webp',
    label: 'WebP Image',
    category: 'image',
  },
};

/**
 * CONVERSION MATRIX
 * Maps each source format to its available target formats.
 */
export const CONVERSION_MATRIX: Record<string, string[]> = {
  docx: ['pdf', 'html', 'txt'],
  pdf: ['txt'],
  csv: ['json'],
  json: ['csv'],
  md: ['html'],
  html: ['md'],
  png: ['jpg', 'webp'],
  jpg: ['png', 'webp'],
  webp: ['png', 'jpg'],
};

/**
 * Detect the format key from a file's name or MIME type.
 */
export function detectFormat(file: File): string | null {
  const ext = file.name.split('.').pop()?.toLowerCase();

  // Handle jpeg -> jpg normalization
  if (ext === 'jpeg') return 'jpg';

  if (ext && FORMAT_REGISTRY[ext]) return ext;

  // Fallback: check MIME types
  for (const [key, info] of Object.entries(FORMAT_REGISTRY)) {
    if (info.mimeType === file.type) return key;
  }

  return null;
}

/**
 * Get available target formats for a given source format.
 */
export function getTargetFormats(sourceFormat: string): FormatInfo[] {
  const targets = CONVERSION_MATRIX[sourceFormat] || [];
  return targets.map((key) => FORMAT_REGISTRY[key]).filter(Boolean);
}

/**
 * Human-readable file size string.
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

/**
 * The maximum payload size for Vercel serverless functions (in bytes).
 * We use 4.5 MB as the safe limit (Vercel's limit is ~4.5 MB for request body).
 */
export const MAX_SERVERLESS_PAYLOAD = 4.5 * 1024 * 1024; // 4,718,592 bytes
