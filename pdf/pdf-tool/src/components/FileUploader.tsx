import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FilePlus } from 'lucide-react';
import { cn } from '../lib/utils';


interface FileUploaderProps {
    onUpload: (files: File[]) => void;
    multiple?: boolean;
    className?: string;
}

export function FileUploader({ onUpload, multiple = true, className }: FileUploaderProps) {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles?.length > 0) {
            onUpload(acceptedFiles);
        }
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
        },
        multiple,
    });

    return (
        <div
            {...getRootProps()}
            className={cn(
                "relative group cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-300",
                isDragActive
                    ? "border-indigo-500 bg-indigo-50/50"
                    : "border-slate-200 hover:border-indigo-400 hover:bg-slate-50",
                className
            )}
        >
            <input {...getInputProps()} />
            <div className="p-12 flex flex-col items-center justify-center text-center gap-4">
                <div className={cn(
                    "p-4 rounded-full transition-all duration-300",
                    isDragActive ? "bg-indigo-100 text-indigo-600" : "bg-slate-100 text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-500"
                )}>
                    {isDragActive ? <FilePlus className="w-8 h-8" /> : <Upload className="w-8 h-8" />}
                </div>
                <div className="space-y-1">
                    <p className="text-lg font-medium text-slate-700">
                        {isDragActive ? "Drop files here" : "Click or drag files to upload"}
                    </p>
                    <p className="text-sm text-slate-400">
                        {multiple ? "Supports multiple PDF files" : "Upload a PDF file"}
                    </p>
                </div>
            </div>

            {/* Decorative background pattern */}
            <div className="absolute inset-0 -z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-tr from-indigo-50/0 via-indigo-50/50 to-indigo-50/0" />
            </div>
        </div>
    );
}
