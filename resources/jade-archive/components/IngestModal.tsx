import React, { useState, useRef } from 'react';
import { IconX, IconSparkles, IconCamera } from './Icons';
import { analyzeJadeImage } from '../services/geminiService';
import { JadeItem } from '../types';

interface IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (item: JadeItem) => void;
}

const IngestModal: React.FC<IngestModalProps> = ({ isOpen, onClose, onSave }) => {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedData, setAnalyzedData] = useState<Partial<JadeItem> | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setImagePreview(base64);
        setAnalyzedData(null); // Reset previous analysis
        setError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = async () => {
    if (!imagePreview) return;
    
    setIsAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeJadeImage(imagePreview);
      setAnalyzedData(result);
    } catch (err) {
      setError("Failed to analyze image. Please ensure the API Key is valid and try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSave = () => {
    if (analyzedData && imagePreview) {
      const newItem: JadeItem = {
        id: crypto.randomUUID(),
        imageUrl: imagePreview,
        title: analyzedData.title || "Untitled Jade",
        itemCode: analyzedData.itemCode || "UNKNOWN",
        descriptionHero: analyzedData.descriptionHero || "",
        attributes: analyzedData.attributes || { color: "", carvingStyle: "", finish: "", symbolism: "" },
        createdAt: new Date().toISOString(),
      };
      onSave(newItem);
      handleClose();
    }
  };

  const handleClose = () => {
    setImagePreview(null);
    setAnalyzedData(null);
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/60 backdrop-blur-sm p-4">
      <div className="bg-stone-50 w-full max-w-4xl max-h-[90vh] rounded-sm shadow-2xl flex flex-col overflow-hidden animate-fade-in-up">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200">
          <h2 className="font-serif text-xl text-stone-800">New Catalog Entry</h2>
          <button onClick={handleClose} className="text-stone-400 hover:text-stone-800 transition-colors">
            <IconX className="w-6 h-6" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8 flex flex-col md:flex-row gap-8">
          
          {/* Left: Image Upload */}
          <div className="w-full md:w-1/2 flex flex-col space-y-4">
            <div 
              className={`relative aspect-[3/4] bg-stone-100 border-2 border-dashed ${imagePreview ? 'border-stone-300' : 'border-stone-300 hover:border-jade-600'} rounded-sm flex flex-col items-center justify-center cursor-pointer transition-colors overflow-hidden group`}
              onClick={() => fileInputRef.current?.click()}
            >
              {imagePreview ? (
                <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                <div className="text-center p-6">
                  <IconCamera className="w-12 h-12 text-stone-400 mx-auto mb-3 group-hover:text-jade-600 transition-colors" />
                  <p className="text-stone-600 font-medium">Upload Pendant Image</p>
                  <p className="text-stone-400 text-sm mt-1">Click to browse (JPG, PNG)</p>
                </div>
              )}
              
              {imagePreview && (
                <div className="absolute bottom-4 right-4 bg-black/50 text-white text-xs px-2 py-1 rounded backdrop-blur-md opacity-0 group-hover:opacity-100 transition-opacity">
                  Click to replace
                </div>
              )}
              
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="image/*" 
                onChange={handleFileChange} 
              />
            </div>

            {imagePreview && !analyzedData && (
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className={`w-full py-3 rounded-sm flex items-center justify-center space-x-2 font-medium transition-all ${isAnalyzing ? 'bg-stone-200 text-stone-500' : 'bg-jade-800 text-white hover:bg-jade-900 shadow-lg hover:shadow-xl'}`}
              >
                {isAnalyzing ? (
                   <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-stone-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Analyzing with Gemini...</span>
                   </>
                ) : (
                  <>
                    <IconSparkles className="w-5 h-5" />
                    <span>Generate Description</span>
                  </>
                )}
              </button>
            )}
            
            {error && (
              <div className="bg-red-50 text-red-700 p-3 rounded text-sm border border-red-100">
                {error}
              </div>
            )}
          </div>

          {/* Right: Analysis Results Form */}
          <div className="w-full md:w-1/2 flex flex-col h-full">
             {!analyzedData ? (
               <div className="flex-1 flex flex-col items-center justify-center text-stone-400 border border-stone-100 rounded bg-stone-50/50 p-12 text-center">
                 <IconSparkles className="w-12 h-12 mb-4 opacity-20" />
                 <p>Upload an image and invoke Gemini to auto-generate the catalog entry.</p>
               </div>
             ) : (
               <div className="flex-1 flex flex-col space-y-6 animate-fade-in">
                 <div>
                   <label className="block text-xs font-bold text-stone-400 uppercase tracking-wider mb-1">Item Code</label>
                   <input 
                    type="text" 
                    value={analyzedData.itemCode} 
                    onChange={(e) => setAnalyzedData({...analyzedData, itemCode: e.target.value})}
                    className="w-full bg-transparent border-b border-stone-300 py-1 font-mono text-stone-600 focus:border-jade-600 focus:outline-none transition-colors"
                   />
                 </div>

                 <div>
                   <label className="block text-xs font-bold text-stone-400 uppercase tracking-wider mb-1">Title</label>
                   <input 
                    type="text" 
                    value={analyzedData.title} 
                    onChange={(e) => setAnalyzedData({...analyzedData, title: e.target.value})}
                    className="w-full bg-transparent border-b border-stone-300 py-1 font-serif text-2xl text-stone-900 focus:border-jade-600 focus:outline-none transition-colors"
                   />
                 </div>

                 <div>
                   <label className="block text-xs font-bold text-stone-400 uppercase tracking-wider mb-2">Description</label>
                   <textarea 
                    value={analyzedData.descriptionHero} 
                    onChange={(e) => setAnalyzedData({...analyzedData, descriptionHero: e.target.value})}
                    rows={6}
                    className="w-full bg-stone-100/50 border border-stone-200 rounded p-3 text-stone-700 leading-relaxed font-light focus:border-jade-600 focus:ring-1 focus:ring-jade-600 focus:outline-none resize-none"
                   />
                 </div>

                 <div className="grid grid-cols-2 gap-4">
                    {(['color', 'carvingStyle', 'finish', 'symbolism'] as const).map((key) => (
                      <div key={key}>
                        <label className="block text-xs font-bold text-stone-400 uppercase tracking-wider mb-1">{key}</label>
                        <input 
                          type="text" 
                          value={analyzedData.attributes?.[key] || ''} 
                          onChange={(e) => setAnalyzedData({
                            ...analyzedData, 
                            attributes: { ...analyzedData.attributes!, [key]: e.target.value }
                          })}
                          className="w-full bg-transparent border-b border-stone-300 py-1 text-sm text-stone-700 focus:border-jade-600 focus:outline-none"
                        />
                      </div>
                    ))}
                 </div>
               </div>
             )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-stone-100 border-t border-stone-200 flex justify-end space-x-4">
          <button onClick={handleClose} className="px-6 py-2 text-stone-600 hover:text-stone-900 font-medium transition-colors">
            Cancel
          </button>
          <button 
            onClick={handleSave} 
            disabled={!analyzedData}
            className={`px-8 py-2 rounded-sm font-medium transition-colors ${!analyzedData ? 'bg-stone-300 text-stone-500 cursor-not-allowed' : 'bg-stone-900 text-white hover:bg-jade-900'}`}
          >
            Save Entry
          </button>
        </div>
      </div>
    </div>
  );
};

export default IngestModal;
