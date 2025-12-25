import { useState } from 'react';
import { FileUploader } from './FileUploader';
import { mergePdfs, splitPdf, imagesToPdf } from '../lib/pdfUtils';
import { Trash2, MoveUp, MoveDown, File as FileIcon, Download, Loader2, ArrowRightLeft, Image as ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';

type Mode = 'merge' | 'split' | 'img2pdf';

export function PDFManager() {
    const [mode, setMode] = useState<Mode>('merge');
    const [files, setFiles] = useState<File[]>([]);
    const [splitFile, setSplitFile] = useState<File | null>(null);
    const [range, setRange] = useState('');
    const [filename, setFilename] = useState('');
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const resetState = (newMode: Mode) => {
        setMode(newMode);
        setFiles([]);
        setSplitFile(null);
        setRange('');
        setFilename('');
        setError(null);
    }

    const handleMerge = async () => {
        if (files.length < 2) return;
        setProcessing(true);
        setError(null);
        try {
            const mergedPdf = await mergePdfs(files);
            downloadPdf(mergedPdf, filename || 'merged.pdf');
        } catch (err) {
            setError('Failed to merge PDFs. Please try again.');
            console.error(err);
        } finally {
            setProcessing(false);
        }
    };

    const handleSplit = async () => {
        if (!splitFile || !range) return;
        setProcessing(true);
        setError(null);
        try {
            const splitPdfBytes = await splitPdf(splitFile, range);
            downloadPdf(splitPdfBytes, filename || `split-${splitFile.name}`);
        } catch (err: any) {
            setError(err.message || 'Failed to split PDF.');
        } finally {
            setProcessing(false);
        }
    };

    const handleImgToPdf = async () => {
        if (files.length === 0) return;
        setProcessing(true);
        setError(null);
        try {
            const pdfBytes = await imagesToPdf(files);
            downloadPdf(pdfBytes, filename || 'images.pdf');
        } catch (err: any) {
            setError(err.message || 'Failed to convert images.');
        } finally {
            setProcessing(false);
        }
    }

    const downloadPdf = (bytes: Uint8Array, name: string) => {
        const finalName = name.toLowerCase().endsWith('.pdf') ? name : `${name}.pdf`;
        const blob = new Blob([bytes as any], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = finalName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const moveFile = (index: number, direction: 'up' | 'down') => {
        const newFiles = [...files];
        if (direction === 'up' && index > 0) {
            [newFiles[index], newFiles[index - 1]] = [newFiles[index - 1], newFiles[index]];
        } else if (direction === 'down' && index < files.length - 1) {
            [newFiles[index], newFiles[index + 1]] = [newFiles[index + 1], newFiles[index]];
        }
        setFiles(newFiles);
    };

    const removeFile = (index: number) => {
        setFiles(files.filter((_, i) => i !== index));
    };

    return (
        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden">
            <div className="flex border-b border-slate-100 overflow-x-auto">
                {(['merge', 'split', 'img2pdf'] as Mode[]).map((m) => (
                    <button
                        key={m}
                        onClick={() => resetState(m)}
                        className={cn(
                            "flex-1 py-4 px-2 text-center font-medium transition-colors relative whitespace-nowrap",
                            mode === m ? "text-indigo-600" : "text-slate-500 hover:text-slate-800"
                        )}
                    >
                        {m === 'merge' && 'Merge PDFs'}
                        {m === 'split' && 'Split PDF'}
                        {m === 'img2pdf' && 'Images to PDF'}
                        {mode === m && (
                            <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600" />
                        )}
                    </button>
                ))}
            </div>

            <div className="p-8">
                <AnimatePresence mode="wait">
                    {mode === 'merge' && (
                        <motion.div
                            key="merge"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-6"
                        >
                            <FileUploader
                                onUpload={(newFiles) => setFiles((prev) => [...prev, ...newFiles])}
                                multiple={true}
                            />

                            {/* File List for Merge */}
                            {files.length > 0 && <FileList files={files} moveFile={moveFile} removeFile={removeFile} />}

                            <div className="flex flex-col gap-4 pt-4 border-t border-slate-100">
                                <div className="flex flex-col gap-2">
                                    <label className="text-sm font-medium text-slate-700">Output Filename (Optional)</label>
                                    <input
                                        type="text"
                                        placeholder="merged.pdf"
                                        value={filename}
                                        onChange={(e) => setFilename(e.target.value)}
                                        className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                                    />
                                </div>
                                <div className="flex justify-end">
                                    <button
                                        onClick={handleMerge}
                                        disabled={files.length < 2 || processing}
                                        className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all w-full justify-center sm:w-auto"
                                    >
                                        {processing ? (
                                            <><Loader2 className="w-5 h-5 animate-spin" /> Merging...</>
                                        ) : (
                                            <><ArrowRightLeft className="w-5 h-5" /> Merge Files</>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {mode === 'split' && (
                        <motion.div
                            key="split"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-6"
                        >
                            {!splitFile ? (
                                <FileUploader
                                    onUpload={(files) => setSplitFile(files[0])}
                                    multiple={false}
                                />
                            ) : (
                                <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-4">
                                    <div className="inline-flex p-3 bg-white rounded-full text-indigo-600 shadow-sm">
                                        <FileIcon className="w-8 h-8" />
                                    </div>
                                    <div>
                                        <h3 className="font-medium text-slate-900">{splitFile.name}</h3>
                                        <p className="text-sm text-slate-500">{(splitFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                    <button
                                        onClick={() => setSplitFile(null)}
                                        className="text-sm text-red-600 hover:text-red-700 font-medium"
                                    >
                                        Change File
                                    </button>
                                </div>
                            )}

                            <div className="space-y-3">
                                <label className="block text-sm font-medium text-slate-700">
                                    Page Ranges to Keep
                                </label>
                                <input
                                    type="text"
                                    value={range}
                                    onChange={(e) => setRange(e.target.value)}
                                    placeholder="e.g. 1, 3-5, 8"
                                    className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                                />
                            </div>

                            <div className="flex flex-col gap-4 pt-4 border-t border-slate-100">
                                <div className="flex flex-col gap-2">
                                    <label className="text-sm font-medium text-slate-700">Output Filename (Optional)</label>
                                    <input
                                        type="text"
                                        placeholder="split-file.pdf"
                                        value={filename}
                                        onChange={(e) => setFilename(e.target.value)}
                                        className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                                    />
                                </div>
                                <div className="flex justify-end">
                                    <button
                                        onClick={handleSplit}
                                        disabled={!splitFile || !range || processing}
                                        className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all w-full justify-center sm:w-auto"
                                    >
                                        {processing ? (
                                            <><Loader2 className="w-5 h-5 animate-spin" /> Splitting...</>
                                        ) : (
                                            <><Download className="w-5 h-5" /> Split PDF</>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {mode === 'img2pdf' && (
                        <motion.div
                            key="img2pdf"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-6"
                        >
                            <FileUploader
                                onUpload={(newFiles) => setFiles((prev) => [...prev, ...newFiles])}
                                multiple={true}
                            />

                            {files.length > 0 && <FileList files={files} moveFile={moveFile} removeFile={removeFile} />}

                            <div className="flex flex-col gap-4 pt-4 border-t border-slate-100">
                                <div className="flex flex-col gap-2">
                                    <label className="text-sm font-medium text-slate-700">Output Filename (Optional)</label>
                                    <input
                                        type="text"
                                        placeholder="images.pdf"
                                        value={filename}
                                        onChange={(e) => setFilename(e.target.value)}
                                        className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                                    />
                                </div>
                                <div className="flex justify-end">
                                    <button
                                        onClick={handleImgToPdf}
                                        disabled={files.length === 0 || processing}
                                        className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all w-full justify-center sm:w-auto"
                                    >
                                        {processing ? (
                                            <><Loader2 className="w-5 h-5 animate-spin" /> Converting...</>
                                        ) : (
                                            <><ImageIcon className="w-5 h-5" /> Convert to PDF</>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg text-sm font-medium text-center"
                    >
                        {error}
                    </motion.div>
                )}
            </div>
        </div>
    );
}

function FileList({ files, moveFile, removeFile }: { files: File[], moveFile: (i: number, d: 'up' | 'down') => void, removeFile: (i: number) => void }) {
    return (
        <div className="space-y-2">
            <h3 className="font-medium text-slate-700">Selected Files</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                {files.map((file, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100 group">
                        <div className="p-2 bg-white rounded-md text-indigo-500 shadow-sm">
                            <FileIcon className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-900 truncate">{file.name}</p>
                            <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                                onClick={() => moveFile(index, 'up')}
                                disabled={index === 0}
                                className="p-1 hover:bg-slate-200 rounded text-slate-500 disabled:opacity-30"
                            >
                                <MoveUp className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => moveFile(index, 'down')}
                                disabled={index === files.length - 1}
                                className="p-1 hover:bg-slate-200 rounded text-slate-500 disabled:opacity-30"
                            >
                                <MoveDown className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => removeFile(index)}
                                className="p-1 hover:bg-red-100 text-slate-500 hover:text-red-600 rounded"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
