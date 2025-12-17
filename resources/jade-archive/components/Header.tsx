import React from 'react';
import { IconPlus } from './Icons';

interface HeaderProps {
  onOpenIngest: () => void;
}

const Header: React.FC<HeaderProps> = ({ onOpenIngest }) => {
  return (
    <header className="sticky top-0 z-50 bg-stone-50/95 backdrop-blur-sm border-b border-stone-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 bg-jade-800 rounded-sm flex items-center justify-center text-stone-50 font-serif font-bold text-xl">
            J
          </div>
          <div>
            <h1 className="font-serif text-2xl text-stone-800 tracking-wide">JADE ARCHIVE</h1>
            <p className="text-xs text-stone-500 uppercase tracking-widest">Collection & Catalog</p>
          </div>
        </div>
        
        <button 
          onClick={onOpenIngest}
          className="group flex items-center space-x-2 bg-stone-900 text-white px-5 py-2.5 rounded-sm hover:bg-jade-900 transition-colors duration-300"
        >
          <IconPlus className="w-4 h-4 text-stone-300 group-hover:text-white transition-colors" />
          <span className="text-sm font-medium tracking-wide">NEW ENTRY</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
