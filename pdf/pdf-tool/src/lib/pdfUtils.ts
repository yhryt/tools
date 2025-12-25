import { PDFDocument } from 'pdf-lib';

export async function mergePdfs(files: File[]): Promise<Uint8Array> {
    const mergedPdf = await PDFDocument.create();

    for (const file of files) {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await PDFDocument.load(arrayBuffer);
        const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
        copiedPages.forEach((page) => mergedPdf.addPage(page));
    }

    return await mergedPdf.save();
}

export async function splitPdf(file: File, rangeStr: string): Promise<Uint8Array> {
    const arrayBuffer = await file.arrayBuffer();
    const sourcePdf = await PDFDocument.load(arrayBuffer);
    const totalPages = sourcePdf.getPageCount();

    const newPdf = await PDFDocument.create();

    // Parse range string "1, 3-5, 9" (1-based) to indices (0-based)
    const pagesToKeep = new Set<number>();
    const parts = rangeStr.split(',').map(s => s.trim());

    for (const part of parts) {
        if (part.includes('-')) {
            const [start, end] = part.split('-').map(Number);
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) {
                    if (i >= 1 && i <= totalPages) {
                        pagesToKeep.add(i - 1);
                    }
                }
            }
        } else {
            const page = Number(part);
            if (!isNaN(page) && page >= 1 && page <= totalPages) {
                pagesToKeep.add(page - 1);
            }
        }
    }

    const indices = Array.from(pagesToKeep).sort((a, b) => a - b);

    if (indices.length === 0) {
        throw new Error('No valid pages selected');
    }

    const copiedPages = await newPdf.copyPages(sourcePdf, indices);
    copiedPages.forEach((page) => newPdf.addPage(page));

    return await newPdf.save();
}

export async function imagesToPdf(files: File[]): Promise<Uint8Array> {
    const pdfDoc = await PDFDocument.create();

    for (const file of files) {
        const arrayBuffer = await file.arrayBuffer();
        let image;

        if (file.type === 'image/jpeg' || file.type === 'image/jpg') {
            image = await pdfDoc.embedJpg(arrayBuffer);
        } else if (file.type === 'image/png') {
            image = await pdfDoc.embedPng(arrayBuffer);
        } else {
            continue; // Skip unsupported
        }

        const page = pdfDoc.addPage([image.width, image.height]);
        page.drawImage(image, {
            x: 0,
            y: 0,
            width: image.width,
            height: image.height,
        });
    }

    return await pdfDoc.save();
}
