"use client";

import { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchBarProps {
    onSearch: (query: string) => void;
    isLoading: boolean;
}

export default function SearchBar({ onSearch, isLoading }: SearchBarProps) {
    const [input, setInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim()) {
            onSearch(input);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-xl relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-500" />
            </div>
            <input
                type="text"
                className="w-full pl-12 pr-4 py-3 rounded-lg bg-[#111] border border-[#333] text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all"
                placeholder="Search arXiv, Semantic Scholar & OpenAlex..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
            />
        </form>
    );
}
