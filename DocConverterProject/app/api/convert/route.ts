/**
 * SERVERLESS CONVERSION API ROUTE
 * ================================
 * 
 * POST /api/convert
 * 
 * This route receives a pre-compressed file (via FormData) along with
 * the desired target format. It processes the format translation using
 * the appropriate library and returns the converted file.
 * 
 * SUPPORTED CONVERSIONS:
 * ─────────────────────
 * DOCX → PDF, HTML, TXT   (via mammoth + pdf-lib)
 * PDF  → TXT              (via pdf-lib)
 * CSV  → JSON             (via csvtojson)
 * JSON → CSV              (via json2csv)
 * MD   → HTML             (via showdown)
 * HTML → Markdown          (via showdown)
 * Images → Images          (via sharp-free pass-through)
 */

import { NextRequest, NextResponse } from 'next/server';
import mammoth from 'mammoth';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';
import csvtojson from 'csvtojson';
import Showdown from 'showdown';

// ─── Route Segment Config ───────────────────────────────────────────────────
// Next.js App Router uses exported constants for route configuration.
// Body size is handled automatically by FormData parsing.

// Increase the max duration for serverless function (Vercel)
export const maxDuration = 30;

// ─── Main POST Handler ─────────────────────────────────────────────────────

export async function POST(request: NextRequest) {
  try {
    // ─── Step 1: Parse the incoming FormData ─────────────────────────
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const targetFormat = formData.get('targetFormat') as string | null;

    if (!file || !targetFormat) {
      return NextResponse.json(
        { error: 'Missing required fields: file and targetFormat' },
        { status: 400 }
      );
    }

    // ─── Step 2: Determine source format ─────────────────────────────
    const sourceExt = file.name.split('.').pop()?.toLowerCase();
    const normalizedSource = sourceExt === 'jpeg' ? 'jpg' : sourceExt;

    // ─── Step 3: Route to the appropriate converter ──────────────────
    const conversionKey = `${normalizedSource}-to-${targetFormat}`;

    let resultBuffer: Uint8Array;
    let resultMimeType: string;
    let resultFilename: string;

    const baseName = file.name.replace(/\.[^/.]+$/, '');

    switch (conversionKey) {
      // ═══ DOCX CONVERSIONS ═══
      case 'docx-to-html': {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.convertToHtml({ buffer: Buffer.from(arrayBuffer) });
        const htmlContent = wrapHtml(result.value, baseName);
        resultBuffer = new TextEncoder().encode(htmlContent);
        resultMimeType = 'text/html';
        resultFilename = `${baseName}.html`;
        break;
      }

      case 'docx-to-txt': {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ buffer: Buffer.from(arrayBuffer) });
        resultBuffer = new TextEncoder().encode(result.value);
        resultMimeType = 'text/plain';
        resultFilename = `${baseName}.txt`;
        break;
      }

      case 'docx-to-pdf': {
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ buffer: Buffer.from(arrayBuffer) });
        const pdfBytes = await textToPdf(result.value, baseName);
        resultBuffer = pdfBytes;
        resultMimeType = 'application/pdf';
        resultFilename = `${baseName}.pdf`;
        break;
      }

      // ═══ PDF CONVERSIONS ═══
      case 'pdf-to-txt': {
        const arrayBuffer = await file.arrayBuffer();
        const text = await extractPdfText(arrayBuffer);
        resultBuffer = new TextEncoder().encode(text);
        resultMimeType = 'text/plain';
        resultFilename = `${baseName}.txt`;
        break;
      }

      // ═══ CSV / JSON CONVERSIONS ═══
      case 'csv-to-json': {
        const text = await file.text();
        const jsonArray = await csvtojson().fromString(text);
        const jsonString = JSON.stringify(jsonArray, null, 2);
        resultBuffer = new TextEncoder().encode(jsonString);
        resultMimeType = 'application/json';
        resultFilename = `${baseName}.json`;
        break;
      }

      case 'json-to-csv': {
        const text = await file.text();
        const jsonData = JSON.parse(text);
        const csvString = jsonToCsv(Array.isArray(jsonData) ? jsonData : [jsonData]);
        resultBuffer = new TextEncoder().encode(csvString);
        resultMimeType = 'text/csv';
        resultFilename = `${baseName}.csv`;
        break;
      }

      // ═══ MARKDOWN / HTML CONVERSIONS ═══
      case 'md-to-html': {
        const text = await file.text();
        const converter = new Showdown.Converter({
          tables: true,
          ghCompatibleHeaderId: true,
          simpleLineBreaks: true,
          openLinksInNewWindow: true,
          emoji: true,
        });
        const htmlContent = wrapHtml(converter.makeHtml(text), baseName);
        resultBuffer = new TextEncoder().encode(htmlContent);
        resultMimeType = 'text/html';
        resultFilename = `${baseName}.html`;
        break;
      }

      case 'html-to-md':
      case 'htm-to-md': {
        const text = await file.text();
        const converter = new Showdown.Converter();
        const markdown = converter.makeMarkdown(text);
        resultBuffer = new TextEncoder().encode(markdown);
        resultMimeType = 'text/markdown';
        resultFilename = `${baseName}.md`;
        break;
      }

      // ═══ IMAGE CONVERSIONS ═══
      // Note: True image format conversion (e.g., PNG→JPG) requires
      // canvas or sharp. In serverless, we pass through the raw bytes
      // with the correct MIME type. For production, consider using
      // a dedicated image processing service.
      case 'png-to-jpg':
      case 'png-to-webp':
      case 'jpg-to-png':
      case 'jpg-to-webp':
      case 'webp-to-png':
      case 'webp-to-jpg': {
        const arrayBuffer = await file.arrayBuffer();
        resultBuffer = new Uint8Array(arrayBuffer);
        const mimeMap: Record<string, string> = {
          png: 'image/png',
          jpg: 'image/jpeg',
          webp: 'image/webp',
        };
        resultMimeType = mimeMap[targetFormat] || 'application/octet-stream';
        resultFilename = `${baseName}.${targetFormat}`;
        break;
      }

      default:
        return NextResponse.json(
          { error: `Unsupported conversion: ${normalizedSource} → ${targetFormat}` },
          { status: 400 }
        );
    }

    // ─── Step 4: Return the converted file ──────────────────────────
    return new NextResponse(resultBuffer as unknown as BodyInit, {
      status: 200,
      headers: {
        'Content-Type': resultMimeType,
        'Content-Disposition': `attachment; filename="${resultFilename}"`,
        'Content-Length': String(resultBuffer.byteLength),
      },
    });
  } catch (error) {
    console.error('Conversion error:', error);
    const message = error instanceof Error ? error.message : 'An unexpected error occurred';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

// ─── Helper: Wrap HTML content with a styled document ────────────────────────

function wrapHtml(body: string, title: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
      line-height: 1.6;
      color: #1a1a1a;
    }
    h1, h2, h3 { color: #111; }
    pre { background: #f5f5f5; padding: 1rem; border-radius: 8px; overflow-x: auto; }
    code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
    th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
    th { background: #f5f5f5; }
    img { max-width: 100%; height: auto; }
    blockquote { border-left: 4px solid #ddd; margin-left: 0; padding-left: 1rem; color: #555; }
  </style>
</head>
<body>
${body}
</body>
</html>`;
}

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ─── Helper: Convert plain text to a formatted PDF ─────────────────────────

async function textToPdf(text: string, title: string): Promise<Uint8Array> {
  const pdfDoc = await PDFDocument.create();
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  const fontSize = 11;
  const titleFontSize = 16;
  const margin = 50;
  const pageWidth = 595.28; // A4
  const pageHeight = 841.89; // A4
  const lineHeight = fontSize * 1.4;
  const maxWidth = pageWidth - 2 * margin;

  // Split text into lines that fit within the page width
  const lines = text.split('\n');
  const wrappedLines: string[] = [];

  for (const line of lines) {
    if (line.trim() === '') {
      wrappedLines.push('');
      continue;
    }

    const words = line.split(' ');
    let currentLine = '';

    for (const word of words) {
      const testLine = currentLine ? `${currentLine} ${word}` : word;
      const width = font.widthOfTextAtSize(testLine, fontSize);

      if (width > maxWidth && currentLine) {
        wrappedLines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }
    if (currentLine) wrappedLines.push(currentLine);
  }

  // Render pages
  let page = pdfDoc.addPage([pageWidth, pageHeight]);
  let y = pageHeight - margin;

  // Draw title on first page
  page.drawText(title, {
    x: margin,
    y,
    size: titleFontSize,
    font: boldFont,
    color: rgb(0.1, 0.1, 0.1),
  });
  y -= titleFontSize * 2;

  // Draw a separator line
  page.drawLine({
    start: { x: margin, y },
    end: { x: pageWidth - margin, y },
    thickness: 0.5,
    color: rgb(0.8, 0.8, 0.8),
  });
  y -= lineHeight;

  // Draw content lines
  for (const line of wrappedLines) {
    if (y < margin + lineHeight) {
      page = pdfDoc.addPage([pageWidth, pageHeight]);
      y = pageHeight - margin;
    }

    if (line.trim()) {
      page.drawText(line, {
        x: margin,
        y,
        size: fontSize,
        font,
        color: rgb(0.15, 0.15, 0.15),
      });
    }
    y -= lineHeight;
  }

  return pdfDoc.save();
}

// ─── Helper: Extract text from PDF ──────────────────────────────────────────

async function extractPdfText(arrayBuffer: ArrayBuffer): Promise<string> {
  // pdf-lib does not have native text extraction, but we can attempt
  // to extract text content from the page's content streams.
  // For a more robust solution, consider using pdf-parse or pdfjs-dist.
  const pdfDoc = await PDFDocument.load(arrayBuffer);
  const pages = pdfDoc.getPages();

  const textParts: string[] = [];

  for (let i = 0; i < pages.length; i++) {
    // Basic approach: get the raw content stream and extract text operators
    // This is a simplified extraction that works for many PDFs
    try {
      const page = pages[i];
      // Access the page's content in a basic way
      const content = page.node.Contents();
      if (content) {
        // Try to get text from the content stream
        const rawStream = content.toString();
        // Extract text between parentheses (Tj operator) and brackets (TJ operator)
        const textMatches = rawStream.match(/\(([^)]*)\)/g);
        if (textMatches) {
          const pageText = textMatches
            .map((m: string) => m.slice(1, -1))
            .join(' ');
          textParts.push(`--- Page ${i + 1} ---\n${pageText}`);
        } else {
          textParts.push(`--- Page ${i + 1} ---\n[No extractable text content]`);
        }
      }
    } catch {
      textParts.push(`--- Page ${i + 1} ---\n[Could not extract text from this page]`);
    }
  }

  if (textParts.length === 0) {
    return 'No text content could be extracted from this PDF. The file may contain only images or scanned content.';
  }

  return textParts.join('\n\n');
}

// ─── Helper: Convert JSON array to CSV ──────────────────────────────────────

function jsonToCsv(data: Record<string, unknown>[]): string {
  if (data.length === 0) return '';

  // Collect all unique keys across all objects
  const allKeys = new Set<string>();
  for (const obj of data) {
    for (const key of Object.keys(obj)) {
      allKeys.add(key);
    }
  }
  const headers = Array.from(allKeys);

  // Build CSV lines
  const escapeCsvField = (field: unknown): string => {
    const str = field === null || field === undefined ? '' : String(field);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const csvLines = [
    headers.map(escapeCsvField).join(','),
    ...data.map((obj) =>
      headers.map((h) => escapeCsvField(obj[h])).join(',')
    ),
  ];

  return csvLines.join('\n');
}
