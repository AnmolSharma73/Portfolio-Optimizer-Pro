/**
 * CLIENT-SIDE CONVERSION UTILITY
 * ==============================
 * 
 * This module handles:
 * 1. Constructing the FormData payload with the (possibly compressed) file
 * 2. Sending the POST request to /api/convert
 * 3. Receiving the converted file response
 * 4. Triggering a browser download for the user
 */

import { FORMAT_REGISTRY } from './formats';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ConversionRequest {
  /** The file to convert (already compressed if needed) */
  file: File;
  /** Target format key (e.g., 'pdf', 'json', 'html') */
  targetFormat: string;
}

export interface ConversionProgress {
  stage: 'uploading' | 'converting' | 'downloading' | 'complete' | 'error';
  message: string;
}

// ─── Main Conversion Function ───────────────────────────────────────────────

/**
 * Convert a file by sending it to the serverless API and triggering a download.
 * 
 * @param request - The file and target format
 * @param onProgress - Callback for progress updates shown in the UI
 */
export async function convertFile(
  request: ConversionRequest,
  onProgress: (progress: ConversionProgress) => void
): Promise<void> {
  const { file, targetFormat } = request;

  try {
    // ─── STAGE 1: Build the upload payload ──────────────────────────
    onProgress({ stage: 'uploading', message: 'Uploading file to converter...' });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('targetFormat', targetFormat);

    // ─── STAGE 2: Send to the serverless API ────────────────────────
    onProgress({ stage: 'converting', message: 'Converting your file...' });

    const response = await fetch('/api/convert', {
      method: 'POST',
      body: formData,
    });

    // ─── Handle API errors ──────────────────────────────────────────
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Conversion failed' }));
      throw new Error(errorData.error || `Server error: ${response.status}`);
    }

    // ─── STAGE 3: Receive and download the converted file ───────────
    onProgress({ stage: 'downloading', message: 'Preparing download...' });

    const blob = await response.blob();

    // Extract filename from Content-Disposition header, or generate one
    const contentDisposition = response.headers.get('Content-Disposition');
    let fileName = generateOutputFilename(file.name, targetFormat);
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match) fileName = match[1];
    }

    // ─── Trigger browser download ───────────────────────────────────
    triggerDownload(blob, fileName);

    onProgress({ stage: 'complete', message: 'File converted successfully!' });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'An unexpected error occurred';
    onProgress({ stage: 'error', message });
    throw error;
  }
}

// ─── Helper: Trigger a browser file download ─────────────────────────────────

/**
 * Creates a temporary <a> element to trigger a file download.
 * This approach works across all modern browsers.
 */
function triggerDownload(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();

  // Cleanup: revoke the object URL and remove the element
  setTimeout(() => {
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }, 100);
}

// ─── Helper: Generate output filename ─────────────────────────────────────────

/**
 * Generates a sensible output filename by replacing the source extension
 * with the target format's extension.
 * 
 * Example: "report.docx" + target "pdf" → "report.pdf"
 */
function generateOutputFilename(sourceName: string, targetFormat: string): string {
  const baseName = sourceName.replace(/\.[^/.]+$/, '');
  const targetInfo = FORMAT_REGISTRY[targetFormat];
  const extension = targetInfo ? targetInfo.extension : `.${targetFormat}`;
  return `${baseName}${extension}`;
}
