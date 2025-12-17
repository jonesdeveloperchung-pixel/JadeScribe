import React from 'react';
import { JadeItem } from '../types';

interface CatalogGridProps {
  items: JadeItem[];
  onSelectItem: (item: JadeItem) => void;
}

const CatalogGrid: React.FC<CatalogGridProps> = ({ items, onSelectItem }) => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-y-16 gap-x-12">
        {items.map((item) => (
          <div 
            key={item.id} 
            className="group cursor-pointer flex flex-col"
            onClick={() => onSelectItem(item)}
          >
            <div className="relative aspect-[4/5] overflow-hidden bg-stone-200 mb-6 shadow-sm group-hover:shadow-xl transition-all duration-500 rounded-sm">
              <img 
                src={item.imageUrl} 
                alt={item.title} 
                className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-stone-900/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            </div>
            
            <div className="flex flex-col items-center text-center space-y-2">
              <span className="text-xs font-mono text-stone-500 tracking-wider uppercase">{item.itemCode}</span>
              <h3 className="font-serif text-xl text-stone-900 group-hover:text-jade-800 transition-colors duration-300">
                {item.title}
              </h3>
              <div className="h-px w-8 bg-jade-300/50 group-hover:w-16 transition-all duration-300"></div>
            </div>
          </div>
        ))}
      </div>
      
      {items.length === 0 && (
        <div className="text-center py-24">
          <p className="text-stone-400 font-serif text-xl italic">The archive is currently empty.</p>
        </div>
      )}
    </div>
  );
};

export default CatalogGrid;
