import React, { useCallback } from 'react';

interface ImageUploaderProps {
  onFileSelect: (file: File) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onFileSelect }) => {
  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  return (
    <div className="w-full max-w-2xl mx-auto border-2 border-dashed border-stone-300 rounded-lg p-12 text-center hover:border-jade-500 transition-colors bg-white shadow-sm">
      <div className="mb-4">
        <svg className="mx-auto h-12 w-12 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <h3 className="mt-2 text-xl font-serif text-stone-800">Upload Tray Image</h3>
      <p className="mt-1 text-sm text-stone-500 mb-6">Select a high-quality photo of your jade collection.</p>
      
      <label className="cursor-pointer inline-block">
        <span className="bg-jade-900 text-white px-6 py-3 rounded-sm font-serif tracking-wider hover:bg-jade-800 transition-colors shadow-md">
          Select File
        </span>
        <input 
          type="file" 
          className="hidden" 
          accept="image/*"
          onChange={handleFileChange}
        />
      </label>
    </div>
  );
};

export default ImageUploader;