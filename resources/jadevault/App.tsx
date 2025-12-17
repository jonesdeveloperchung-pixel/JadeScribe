import React, { useState, useEffect } from 'react';
import { detectItemCodes, generateLuxuryDescription } from './services/geminiService';
import { ItemCode, PendantDescription, AppState } from './types';
import ImageUploader from './components/ImageUploader';
import Spinner from './components/Spinner';
import Button from './components/Button';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [itemCodes, setItemCodes] = useState<ItemCode[]>([]);
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [description, setDescription] = useState<PendantDescription | null>(null);
  const [appState, setAppState] = useState<AppState>(AppState.IDLE);
  const [error, setError] = useState<string | null>(null);

  // Clean up object URL to prevent memory leaks
  useEffect(() => {
    return () => {
      if (imagePreview) URL.revokeObjectURL(imagePreview);
    };
  }, [imagePreview]);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setImagePreview(URL.createObjectURL(selectedFile));
    setAppState(AppState.ANALYZING_CODES);
    setError(null);
    setItemCodes([]);
    setSelectedCode(null);
    setDescription(null);

    try {
      const codes = await detectItemCodes(selectedFile);
      setItemCodes(codes);
      setAppState(AppState.SELECTING_ITEM);
    } catch (err: any) {
      setError(err.message || "Failed to analyze image");
      setAppState(AppState.ERROR);
    }
  };

  const handleCodeSelect = async (code: string) => {
    if (!file) return;
    setSelectedCode(code);
    setAppState(AppState.GENERATING_DESCRIPTION);
    setError(null);

    try {
      const result = await generateLuxuryDescription(file, code);
      setDescription(result);
      setAppState(AppState.VIEWING_RESULT);
    } catch (err: any) {
      setError(err.message || "Failed to generate description");
      setAppState(AppState.ERROR); // Or stay in selecting state with error toast
    }
  };

  const handleReset = () => {
    setFile(null);
    setImagePreview(null);
    setAppState(AppState.IDLE);
    setItemCodes([]);
    setDescription(null);
  };

  return (
    <div className="min-h-screen bg-stone-50 text-stone-800 font-sans selection:bg-jade-200">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-jade-900 rounded-sm flex items-center justify-center text-white font-serif italic text-lg">J</div>
            <h1 className="text-2xl font-serif text-jade-950 tracking-wide">JADE<span className="text-jade-700">VAULT</span></h1>
          </div>
          <div className="text-xs tracking-widest uppercase text-stone-500 hidden sm:block">Automated Cataloging System</div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Intro / Upload State */}
        {appState === AppState.IDLE && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in-up">
            <div className="text-center mb-12 max-w-2xl">
              <h2 className="text-4xl font-serif text-stone-900 mb-4">The Art of Documentation</h2>
              <p className="text-lg text-stone-600 font-light">
                Upload your inventory tray. Our system will identify item codes and generate 
                market-ready, luxury descriptions emphasizing symbolism and aesthetics.
              </p>
            </div>
            <ImageUploader onFileSelect={handleFileSelect} />
          </div>
        )}

        {/* Workspace State */}
        {appState !== AppState.IDLE && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">
            
            {/* Left Column: Image Viewer */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              <div className="bg-white p-4 rounded-sm shadow-sm border border-stone-200">
                <div className="aspect-[4/5] relative bg-stone-100 overflow-hidden rounded-sm">
                  {imagePreview && (
                    <img 
                      src={imagePreview} 
                      alt="Jade Tray" 
                      className="w-full h-full object-contain"
                    />
                  )}
                  {/* Overlay for Scanning State */}
                  {appState === AppState.ANALYZING_CODES && (
                    <div className="absolute inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center">
                      <div className="text-center">
                        <Spinner />
                        <p className="mt-4 font-serif text-jade-900 animate-pulse">Scanning Inventory...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <Button variant="secondary" onClick={handleReset} className="self-start text-sm">
                ← Upload New Image
              </Button>
            </div>

            {/* Right Column: Interaction & Results */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              
              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-sm">
                  <p className="text-red-700 font-medium">{error}</p>
                </div>
              )}

              {/* Item Selection List */}
              {(appState === AppState.SELECTING_ITEM || appState === AppState.GENERATING_DESCRIPTION || appState === AppState.VIEWING_RESULT) && (
                <div className="bg-white border border-stone-200 shadow-sm rounded-sm p-6">
                  <h3 className="text-lg font-serif text-stone-900 mb-4 border-b border-stone-100 pb-2">
                    Detected Inventory ({itemCodes.length})
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                    {itemCodes.map((item) => (
                      <button
                        key={item.code}
                        onClick={() => handleCodeSelect(item.code)}
                        disabled={appState === AppState.GENERATING_DESCRIPTION}
                        className={`
                          text-sm py-2 px-3 rounded-sm border transition-all text-left group relative overflow-hidden
                          ${selectedCode === item.code 
                            ? 'bg-jade-900 text-white border-jade-900 shadow-md' 
                            : 'bg-stone-50 border-stone-200 text-stone-600 hover:border-jade-400 hover:text-jade-900'}
                        `}
                      >
                        <span className="font-mono tracking-tight font-medium relative z-10">{item.code}</span>
                        <span className="block text-[10px] opacity-70 relative z-10">{item.location || 'Detected'}</span>
                        
                        {selectedCode === item.code && appState === AppState.GENERATING_DESCRIPTION && (
                           <div className="absolute bottom-0 left-0 h-1 bg-white/30 animate-pulse w-full"></div>
                        )}
                      </button>
                    ))}
                    {itemCodes.length === 0 && !error && (
                      <div className="col-span-full text-stone-400 italic text-sm py-4 text-center">
                        No codes detected automatically. Please ensure labels are visible.
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Description Result */}
              <div className="flex-1 min-h-[400px]">
                {appState === AppState.GENERATING_DESCRIPTION && (
                  <div className="h-full flex flex-col items-center justify-center bg-white border border-stone-200 border-dashed rounded-sm p-12 text-center">
                     <Spinner />
                     <h4 className="mt-4 font-serif text-xl text-jade-900">Curating Description</h4>
                     <p className="text-stone-500 mt-2 max-w-xs">Analyzing translucency, carving motifs, and cultural significance for <span className="font-mono text-stone-800">{selectedCode}</span>...</p>
                  </div>
                )}

                {appState === AppState.VIEWING_RESULT && description && (
                  <div className="bg-white border-t-4 border-jade-700 shadow-lg p-8 md:p-10 rounded-sm animate-fade-in relative overflow-hidden">
                    {/* Background decoration */}
                    <div className="absolute top-0 right-0 -mt-16 -mr-16 w-64 h-64 bg-jade-50 rounded-full blur-3xl opacity-50 pointer-events-none"></div>

                    <div className="relative z-10">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <p className="text-xs font-bold tracking-widest text-jade-700 uppercase mb-1">Item Code: {description.itemCode}</p>
                          <h2 className="text-3xl font-serif text-stone-900 leading-tight">{description.title}</h2>
                        </div>
                        <div className="hidden sm:block">
                           <span className="inline-block px-3 py-1 bg-stone-100 text-stone-500 text-xs tracking-wider rounded-full border border-stone-200">
                             Jadeite
                           </span>
                        </div>
                      </div>

                      <div className="prose prose-stone max-w-none">
                        <div className="mb-8">
                          <p className="text-lg text-stone-600 italic font-serif leading-relaxed border-l-2 border-jade-200 pl-6 py-2">
                            "{description.poeticCopy}"
                          </p>
                        </div>

                        <div className="grid md:grid-cols-2 gap-8 mt-8">
                          <div>
                            <h4 className="text-sm font-bold uppercase tracking-widest text-stone-400 mb-3 border-b border-stone-100 pb-1">Visual Characteristics</h4>
                            <p className="text-stone-700 leading-relaxed text-sm">
                              {description.visualDescription}
                            </p>
                          </div>
                          <div>
                            <h4 className="text-sm font-bold uppercase tracking-widest text-stone-400 mb-3 border-b border-stone-100 pb-1">Symbolism & Meaning</h4>
                            <p className="text-stone-700 leading-relaxed text-sm">
                              {description.symbolism}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="mt-10 pt-6 border-t border-stone-100 flex gap-3">
                         <Button onClick={() => {
                            navigator.clipboard.writeText(
                              `Code: ${description.itemCode}\nTitle: ${description.title}\n\n${description.poeticCopy}\n\nVisuals: ${description.visualDescription}\nSymbolism: ${description.symbolism}`
                            );
                            alert("Copied to clipboard!");
                         }} variant="outline" className="flex-1 text-sm py-2">
                           Copy to Clipboard
                         </Button>
                         <Button variant="primary" className="flex-1 text-sm py-2">
                           Save to Inventory
                         </Button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;