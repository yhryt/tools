"use client";

import { useState } from 'react';
import { Copy, Check, ExternalLink } from 'lucide-react';
import { Paper, generateBibTeX } from '@/app/utils/api';

interface PaperCardProps {
    paper: Paper;
}

export default function PaperCard({ paper }: PaperCardProps) {
    const [copied, setCopied] = useState(false);

    const handleCopyBibTeX = async () => {
        const bib = await generateBibTeX(paper);
        navigator.clipboard.writeText(bib);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const isArxiv = paper.source === 'arxiv';

    return (
        <div className="obsidian-card p-5 mb-4 border-l-4 border-l-transparent hover:border-l-[var(--primary)] text-left">
            <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded ${isArxiv ? 'bg-red-900/40 text-red-200' : 'bg-indigo-900/40 text-indigo-200'}`}>
                            {paper.source === 'arxiv' ? 'arXiv' : 'Semantic Scholar'}
                        </span>
                        <span className="text-gray-500 text-sm">{paper.year}</span>
                    </div>

                    <h3 className="text-lg font-bold text-gray-100 mb-2 leading-snug">
                        <a href={paper.url} target="_blank" rel="noreferrer" className="hover:text-[var(--primary)] transition-colors">
                            {paper.title}
                        </a>
                    </h3>

                    <div className="text-sm text-gray-400 mb-3">
                        {paper.authors.slice(0, 4).map(a => a.name).join(', ')}{paper.authors.length > 4 ? ' et al.' : ''}
                    </div>

                    {paper.abstract && (
                        <p className="text-sm text-gray-500 line-clamp-3 mb-4 leading-relaxed font-serif">
                            {paper.abstract}
                        </p>
                    )}
                </div>

                <button
                    onClick={handleCopyBibTeX}
                    className="p-2 rounded hover:bg-[#222] text-gray-400 hover:text-white transition-colors"
                    title="Copy BibTeX"
                >
                    {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                </button>
            </div>

            <div className="flex items-center gap-4 border-t border-[#222] pt-3 mt-1">
                <a
                    href={paper.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-mono text-gray-400 hover:text-[var(--primary)] flex items-center gap-1"
                >
                    READ FULL PAPER <ExternalLink className="w-3 h-3" />
                </a>
            </div>
        </div>
    );
}
