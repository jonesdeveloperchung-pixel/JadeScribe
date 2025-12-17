import React from 'react';
import { JadeItem } from '../types';
import { IconX } from './Icons';

interface ItemDetailProps {
  item: JadeItem;
  onClose: () => void;
}

const ItemDetail: React.FC<ItemDetailProps> = ({ item, onClose }) => {
  return (
    <div className="fixed inset-0 z-40 bg-stone-50 overflow-y-auto">
      <div className="relative min-h-screen flex flex-col lg:flex-row">
        
        {/* Close Button - Sticky */}
        <button 
          onClick={onClose}
          className="fixed top-6 right-6 z-50 p-2 bg-white/80 backdrop-blur rounded-full text-stone-500 hover:text-stone-900 hover:bg-white transition-all shadow-sm"
        >
          <IconX className="w-8 h-8" />
        </button>

        {/* Left: Image */}
        <div className="w-full lg:w-1/2 h-[60vh] lg:h-auto lg:min-h-screen bg-stone-100 relative">
          <img 
            src={item.imageUrl} 
            alt={item.title} 
            className="w-full h-full object-cover lg:fixed lg:w-[50vw] lg:h-full"
          />
        </div>

        {/* Right: Content */}
        <div className="w-full lg:w-1/2 bg-stone-50 p-8 md:p-16 lg:p-24 flex flex-col justify-center min-h-screen">
          <div className="max-w-xl mx-auto animate-fade-in-up">
            
            <div className="mb-8 border-b border-stone-200 pb-8">
               <p className="font-mono text-sm text-stone-500 mb-4 tracking-widest">{item.itemCode}</p>
               <h1 className="font-serif text-4xl md:text-5xl text-stone-900 leading-tight mb-6">
                 {item.title}
               </h1>
            </div>

            <div className="prose prose-stone prose-lg mb-12">
              <p className="font-light leading-relaxed text-stone-700 italic">
                {item.descriptionHero}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-8 gap-x-4">
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-stone-400 uppercase tracking-widest">Color</h4>
                <p className="text-stone-800">{item.attributes.color}</p>
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-stone-400 uppercase tracking-widest">Finish</h4>
                <p className="text-stone-800">{item.attributes.finish}</p>
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-stone-400 uppercase tracking-widest">Carving Style</h4>
                <p className="text-stone-800">{item.attributes.carvingStyle}</p>
              </div>
               <div className="space-y-1">
                <h4 className="text-xs font-bold text-stone-400 uppercase tracking-widest">Symbolism</h4>
                <p className="text-stone-800">{item.attributes.symbolism}</p>
              </div>
            </div>

            <div className="mt-16 pt-8 border-t border-stone-100 flex items-center justify-between text-xs text-stone-400 tracking-wider">
              <span>CATALOGUED ON {new Date(item.createdAt).toLocaleDateString()}</span>
              <span>GEMINI ANALYSIS VERIFIED</span>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default ItemDetail;
