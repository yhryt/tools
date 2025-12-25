import { PDFManager } from './components/PDFManager';
import { FileText } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg text-white">
              <FileText className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
              PDF Tools
            </h1>
          </div>
          <div className="text-sm text-slate-500">
            Secure client-side processing
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <PDFManager />
      </main>

      <footer className="border-t border-slate-200 bg-white mt-auto py-8">
        <div className="max-w-5xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>© 2024 PDF Tools. All processing happens in your browser.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
