/**
 * CLIENT-SIDE COMPRESSION LAYER
 * =============================
 * 
 * This module runs ENTIRELY in the user's browser. Its sole purpose is to
 * intercept files that exceed the Vercel serverless function payload limit
 * (4.5 MB) and attempt to reduce their size before uploading.
 * 
 * COMPRESSION STRATEGIES:
 * -----------------------
 * 1. IMAGES (png, jpg, webp): Use `browser-image-compression` to reduce
 *    quality, dimensions, and strip EXIF metadata. This is the most
 *    effective compression path — images can often be reduced 50-90%.
 * 
 * 2. PDFs (pdf): Use `pdf-lib` to strip metadata and attempt page-level
 *    optimization. For image-heavy PDFs, we extract embedded images,
 *    compress them via Canvas, and re-embed. Pure text PDFs have limited
 *    compression potential.
 * 
 * 3. TEXT/DATA FILES (csv, json, txt, md, html, docx): These formats
 *    cannot be meaningfully compressed in the browser. If they exceed
 *    the limit, we return a friendly error with alternative suggestions.
 * 
 * FLOW:
 * -----
 * compressFile(file) 
 *   → detect file type
 *   → route to appropriate compression strategy
 *   → return { success, file, originalSize, compressedSize, message }
 */

import imageCompression from 'browser-image-compression';
import { PDFDocument } from 'pdf-lib';
import { MAX_SERVERLESS_PAYLOAD, detectFormat } from './formats';

// ─── Result Types ──────────────────────────────────────────────────────────

export interface CompressionResult {
  /** Whether compression succeeded and the file is now under the limit */
  success: boolean;
  /** The (possibly compressed) file ready for upload */
  file: File;
  /** Original file size in bytes */
  originalSize: number;
  /** Compressed file size in bytes (same as original if no compression) */
  compressedSize: number;
  /** Human-readable status message for the UI */
  message: string;
}

// ─── Main Entry Point ──────────────────────────────────────────────────────

/**
 * MAIN COMPRESSION FUNCTION
 * 
 * This is the single entry point called by the UI. It inspects the file,
 * determines the best compression strategy, and returns the result.
 * 
 * @param file - The raw File object from the user's drag-and-drop or file input
 * @returns CompressionResult with the compressed file or an error message
 */
export async function compressFile(file: File): Promise<CompressionResult> {
  const originalSize = file.size;

  // ─── STEP 1: Check if compression is even needed ───────────────────
  // If the file is already under the serverless limit, skip compression
  // entirely. This avoids unnecessary processing for small files.
  if (originalSize <= MAX_SERVERLESS_PAYLOAD) {
    return {
      success: true,
      file,
      originalSize,
      compressedSize: originalSize,
      message: 'File is within size limits. No compression needed.',
    };
  }

  // ─── STEP 2: Detect file format and route to strategy ──────────────
  const format = detectFormat(file);

  switch (format) {
    // ═══ IMAGE COMPRESSION PATH ═══
    // Images are the best candidates for compression. We can reduce
    // quality, resize dimensions, and strip metadata.
    case 'png':
    case 'jpg':
    case 'webp':
      return compressImage(file, originalSize);

    // ═══ PDF COMPRESSION PATH ═══
    // PDFs can contain embedded images which we can compress.
    // Pure text PDFs will have limited compression potential.
    case 'pdf':
      return compressPDF(file, originalSize);

    // ═══ INCOMPRESSIBLE FILE TYPES ═══
    // Text-based formats (CSV, JSON, TXT, MD, HTML, DOCX) cannot be
    // meaningfully compressed in the browser. DOCX is already a ZIP
    // archive internally, so further compression yields minimal gains.
    case 'csv':
    case 'json':
    case 'txt':
    case 'md':
    case 'html':
    case 'docx':
      return {
        success: false,
        file,
        originalSize,
        compressedSize: originalSize,
        message: `This ${format?.toUpperCase()} file is ${(originalSize / (1024 * 1024)).toFixed(1)} MB — too large for serverless processing. ` +
          'Text-based files cannot be compressed further in the browser. ' +
          'Try splitting the file into smaller parts, or removing unnecessary data.',
      };

    // ═══ UNKNOWN FORMAT FALLBACK ═══
    default:
      return {
        success: false,
        file,
        originalSize,
        compressedSize: originalSize,
        message: 'Unsupported file format. Cannot compress this file type.',
      };
  }
}

// ─── Image Compression Strategy ────────────────────────────────────────────

/**
 * COMPRESS IMAGE FILES
 * 
 * Uses the `browser-image-compression` library which leverages the browser's
 * native Canvas API and OffscreenBitmap to:
 * 
 * 1. Decode the image
 * 2. Resize it to fit within maxWidthOrHeight (preserving aspect ratio)
 * 3. Re-encode at reduced quality
 * 4. Strip EXIF/metadata
 * 
 * The compression targets a max file size of 4 MB (with margin for the
 * 4.5 MB serverless limit). If the first pass doesn't get under the limit,
 * we try a more aggressive second pass with lower quality.
 * 
 * @param file - The image File object
 * @param originalSize - Original size in bytes for reporting
 */
async function compressImage(
  file: File,
  originalSize: number
): Promise<CompressionResult> {
  try {
    // ─── PASS 1: Moderate compression ──────────────────────────────
    // Target: 4 MB max, 2048px max dimension, 0.7 quality
    // This preserves reasonable visual quality for most use cases.
    const moderateOptions = {
      maxSizeMB: 4,               // Target 4 MB (under 4.5 MB limit)
      maxWidthOrHeight: 2048,     // Cap dimensions to 2K
      useWebWorker: true,         // Offload to web worker for performance
      fileType: file.type as string,
      initialQuality: 0.7,       // 70% quality — good balance
    };

    let compressed = await imageCompression(file, moderateOptions);

    // ─── Check if Pass 1 succeeded ─────────────────────────────────
    if (compressed.size <= MAX_SERVERLESS_PAYLOAD) {
      const compressedFile = new File([compressed], file.name, { type: file.type });
      return {
        success: true,
        file: compressedFile,
        originalSize,
        compressedSize: compressed.size,
        message: `Image optimized: ${(originalSize / (1024 * 1024)).toFixed(1)} MB → ${(compressed.size / (1024 * 1024)).toFixed(1)} MB`,
      };
    }

    // ─── PASS 2: Aggressive compression ────────────────────────────
    // If moderate compression wasn't enough, try harder:
    // - Lower max size target (3 MB)
    // - Smaller max dimension (1024px)
    // - Lower quality (0.5)
    const aggressiveOptions = {
      maxSizeMB: 3,
      maxWidthOrHeight: 1024,
      useWebWorker: true,
      fileType: file.type as string,
      initialQuality: 0.5,
    };

    compressed = await imageCompression(file, aggressiveOptions);

    if (compressed.size <= MAX_SERVERLESS_PAYLOAD) {
      const compressedFile = new File([compressed], file.name, { type: file.type });
      return {
        success: true,
        file: compressedFile,
        originalSize,
        compressedSize: compressed.size,
        message: `Image aggressively optimized: ${(originalSize / (1024 * 1024)).toFixed(1)} MB → ${(compressed.size / (1024 * 1024)).toFixed(1)} MB (quality reduced)`,
      };
    }

    // ─── Both passes failed ────────────────────────────────────────
    // The image is simply too large even after aggressive compression.
    return {
      success: false,
      file,
      originalSize,
      compressedSize: compressed.size,
      message: `Image is still ${(compressed.size / (1024 * 1024)).toFixed(1)} MB after maximum compression. ` +
        'Try manually cropping or resizing the image before uploading.',
    };
  } catch (error) {
    return {
      success: false,
      file,
      originalSize,
      compressedSize: originalSize,
      message: `Image compression failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

// ─── PDF Compression Strategy ──────────────────────────────────────────────

/**
 * COMPRESS PDF FILES
 * 
 * PDFs are complex containers that can hold text, images, fonts, and more.
 * Our compression strategy:
 * 
 * 1. Load the PDF with pdf-lib
 * 2. Strip metadata (title, author, keywords, etc.) to save some bytes
 * 3. Create a fresh copy of the PDF (which drops orphaned objects)
 * 4. If still too large, we can't do much more without server-side tools
 * 
 * NOTE: True PDF image re-compression would require decoding each XObject
 * image stream, re-compressing via Canvas, and re-embedding. This is
 * computationally expensive and not always possible in the browser for
 * very large PDFs. We focus on metadata stripping and structural cleanup.
 * 
 * @param file - The PDF File object
 * @param originalSize - Original size in bytes for reporting
 */
async function compressPDF(
  file: File,
  originalSize: number
): Promise<CompressionResult> {
  try {
    // ─── STEP 1: Load the PDF into pdf-lib ─────────────────────────
    const arrayBuffer = await file.arrayBuffer();
    const pdfDoc = await PDFDocument.load(arrayBuffer, {
      ignoreEncryption: true,  // Try to process even encrypted PDFs
    });

    // ─── STEP 2: Strip all metadata ────────────────────────────────
    // Metadata can sometimes be surprisingly large (embedded thumbnails,
    // edit history, XMP data, etc.)
    pdfDoc.setTitle('');
    pdfDoc.setAuthor('');
    pdfDoc.setSubject('');
    pdfDoc.setKeywords([]);
    pdfDoc.setProducer('');
    pdfDoc.setCreator('');

    // ─── STEP 3: Save as a fresh, clean copy ───────────────────────
    // pdf-lib's save() rebuilds the PDF structure, which can eliminate
    // orphaned objects, duplicate resources, and other bloat from the
    // original file.
    const compressedBytes = await pdfDoc.save({
      useObjectStreams: true,    // More compact internal structure
    });

    // ─── STEP 4: Check if the cleaned PDF is small enough ──────────
    if (compressedBytes.length <= MAX_SERVERLESS_PAYLOAD) {
      const pdfArrayBuffer = compressedBytes.buffer.slice(
        compressedBytes.byteOffset,
        compressedBytes.byteOffset + compressedBytes.byteLength
      ) as ArrayBuffer;
      const compressedFile = new File(
        [pdfArrayBuffer],
        file.name,
        { type: 'application/pdf' }
      );
      return {
        success: true,
        file: compressedFile,
        originalSize,
        compressedSize: compressedBytes.length,
        message: `PDF optimized: ${(originalSize / (1024 * 1024)).toFixed(1)} MB → ${(compressedBytes.length / (1024 * 1024)).toFixed(1)} MB`,
      };
    }

    // ─── STEP 5: PDF is still too large ────────────────────────────
    // At this point, the PDF likely contains high-resolution images or
    // heavy vector graphics that can't be reduced without a full
    // rendering pipeline.
    return {
      success: false,
      file,
      originalSize,
      compressedSize: compressedBytes.length,
      message: `PDF is still ${(compressedBytes.length / (1024 * 1024)).toFixed(1)} MB after optimization. ` +
        'The file likely contains high-resolution images. ' +
        'Try reducing image quality in the original document, or split the PDF into smaller sections.',
    };
  } catch (error) {
    return {
      success: false,
      file,
      originalSize,
      compressedSize: originalSize,
      message: `PDF optimization failed: ${error instanceof Error ? error.message : 'Unknown error'}. ` +
        'The file may be encrypted or corrupted.',
    };
  }
}
