"use server";

import { XMLParser } from 'fast-xml-parser';

export interface Paper {
    paperId: string;
    source: 'semantic-scholar' | 'arxiv' | 'openalex';
    title: string;
    authors: { name: string }[];
    year: number | string;
    abstract: string | null;
    url: string;
    citationCount?: number;
    isOpenAccess: boolean;
}

const SEMANTIC_URL = 'https://api.semanticscholar.org/graph/v1/paper/search';
const ARXIV_URL = 'https://export.arxiv.org/api/query';
const OPENALEX_URL = 'https://api.openalex.org/works';

const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "@_"
});

async function fetchSemanticScholar(query: string, limit: number): Promise<Paper[]> {
    try {
        const params = new URLSearchParams({
            query,
            limit: limit.toString(),
            fields: 'paperId,title,authors,year,abstract,tldr,url,citationCount,isOpenAccess'
        });

        const res = await fetch(`${SEMANTIC_URL}?${params.toString()}`);
        if (!res.ok) return [];
        const data = await res.json();

        return (data.data || []).map((p: any) => ({
            paperId: p.paperId,
            source: 'semantic-scholar',
            title: p.title,
            authors: p.authors || [],
            year: p.year,
            abstract: p.tldr?.text || p.abstract,
            url: p.url,
            citationCount: p.citationCount,
            isOpenAccess: p.isOpenAccess
        }));
    } catch (e) {
        console.error("Semantic Scholar Error:", e);
        return [];
    }
}

async function fetchArxiv(query: string, limit: number): Promise<Paper[]> {
    try {
        // arXiv API expects 'search_query=all:term'
        const params = new URLSearchParams({
            search_query: `all:${query}`,
            start: '0',
            max_results: limit.toString()
        });

        const res = await fetch(`${ARXIV_URL}?${params.toString()}`);
        if (!res.ok) return [];
        const text = await res.text();
        const data = parser.parse(text);

        const entries = data.feed?.entry;
        if (!entries) return [];

        // entries can be an array or single object
        const list = Array.isArray(entries) ? entries : [entries];

        return list.map((entry: any) => {
            // Authors can be array or single
            const auths = Array.isArray(entry.author) ? entry.author : [entry.author];

            return {
                paperId: entry.id,
                source: 'arxiv',
                title: entry.title.replace(/\n/g, ' ').trim(),
                authors: auths.map((a: any) => ({ name: a.name })),
                year: new Date(entry.published).getFullYear(),
                abstract: entry.summary.replace(/\n/g, ' ').trim(),
                url: entry.id,
                citationCount: undefined,
                isOpenAccess: true
            };
        });
    } catch (e) {
        console.error("arXiv Error:", e);
        return [];
    }
}

async function fetchOpenAlex(query: string, limit: number): Promise<Paper[]> {
    try {
        const params = new URLSearchParams({
            search: query,
            per_page: limit.toString()
        });

        const res = await fetch(`${OPENALEX_URL}?${params.toString()}`);
        if (!res.ok) return [];
        const data = await res.json();

        return (data.results || []).map((work: any) => ({
            paperId: work.id,
            source: 'openalex',
            title: work.title,
            authors: (work.authorships || []).map((a: any) => ({ name: a.author.display_name })),
            year: work.publication_year,
            abstract: work.abstract_inverted_index ? 'Abstract available in full record' : null,
            url: work.doi || work.landing_page_url,
            citationCount: work.cited_by_count,
            isOpenAccess: work.open_access?.is_oa || false
        }));
    } catch (e) {
        console.error("OpenAlex Error:", e);
        return [];
    }
}

export async function searchPapers(query: string): Promise<Paper[]> {
    const [semantic, arxiv, openalex] = await Promise.all([
        fetchSemanticScholar(query, 10),
        fetchArxiv(query, 10),
        fetchOpenAlex(query, 10)
    ]);

    // Interleave results
    const combined: Paper[] = [];
    const maxLength = Math.max(semantic.length, arxiv.length, openalex.length);

    for (let i = 0; i < maxLength; i++) {
        if (semantic[i]) combined.push(semantic[i]);
        if (arxiv[i]) combined.push(arxiv[i]);
        if (openalex[i]) combined.push(openalex[i]);
    }

    return combined;
}

export async function generateBibTeX(paper: Paper): Promise<string> {
    const authorText = paper.authors.map(a => a.name).join(' and ');
    return `@article{${paper.source}_${paper.year},
  title = {${paper.title}},
  author = {${authorText}},
  year = {${paper.year}},
  url = {${paper.url}}
}`;
}
