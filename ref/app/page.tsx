"use client";

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, TrendingUp, LogOut } from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import PaperCard from '@/components/PaperCard';
import { searchPapers, Paper } from '@/app/utils/api';
import { signOut } from 'next-auth/react'; // Client side signout

export default function Home() {
    const [papers, setPapers] = useState<Paper[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [query, setQuery] = useState('');
    const [hasSearched, setHasSearched] = useState(false);

    const [japaneseOnly, setJapaneseOnly] = useState(false);
    const [sortByPopularity, setSortByPopularity] = useState(false);

    const handleSearch = async (searchQuery: string) => {
        setIsLoading(true);
        setQuery(searchQuery);
        try {
            const results = await searchPapers(searchQuery);
            setPapers(results);
            setHasSearched(true);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    const displayedPapers = useMemo(() => {
        let result = [...papers];

        if (japaneseOnly) {
            const jpRegex = /[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF]/;
            result = result.filter(p => jpRegex.test(p.title) || (p.abstract && jpRegex.test(p.abstract)));
        }

        if (sortByPopularity) {
            result.sort((a, b) => (b.citationCount || 0) - (a.citationCount || 0));
        }

        return result;
    }, [papers, japaneseOnly, sortByPopularity]);

    return (
        <main className="min-h-screen p-6 md:p-12 max-w-4xl mx-auto flex flex-col items-center relative">

            <div className="absolute top-4 right-4">
                <button
                    onClick={() => signOut({ callbackUrl: '/login' })}
                    className="flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors"
                >
                    <LogOut className="w-4 h-4" /> Sign Out
                </button>
            </div>

            <motion.div
                layout
                className={`w-full flex flex-col items-center mb-10 transition-all ${hasSearched ? 'mt-4' : 'mt-[20vh]'}`}
            >
                <h1 className="text-3xl font-bold tracking-tight text-white mb-6">
                    Research<span className="text-[var(--primary)]">Obsidian</span>
                </h1>

                <SearchBar onSearch={handleSearch} isLoading={isLoading} />

                <div className="flex flex-wrap gap-4 mt-6 justify-center">
                    <button
                        onClick={() => setSortByPopularity(!sortByPopularity)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${sortByPopularity
                                ? 'bg-[var(--primary)] text-white shadow-[0_0_10px_var(--primary)]'
                                : 'bg-[#111] text-gray-400 border border-[#333] hover:border-gray-500'
                            }`}
                    >
                        <TrendingUp className="w-4 h-4" />
                        Sort by Popularity
                    </button>

                    <button
                        onClick={() => setJapaneseOnly(!japaneseOnly)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${japaneseOnly
                                ? 'bg-[var(--primary)] text-white shadow-[0_0_10px_var(--primary)]'
                                : 'bg-[#111] text-gray-400 border border-[#333] hover:border-gray-500'
                            }`}
                    >
                        <Filter className="w-4 h-4" />
                        Japanese Only
                    </button>
                </div>
            </motion.div>

            <div className="w-full">
                {isLoading && (
                    <div className="text-center py-10 text-gray-500 animate-pulse">
                        Searching across multiple databases...
                    </div>
                )}

                {!isLoading && hasSearched && displayedPapers.length === 0 && (
                    <div className="text-center py-10 text-gray-600">
                        {papers.length > 0 ? "No papers match your filter." : "No papers found."}
                    </div>
                )}

                <div className="space-y-1">
                    {displayedPapers.map((paper) => (
                        <PaperCard key={paper.paperId} paper={paper} />
                    ))}
                </div>
            </div>
        </main>
    );
}
