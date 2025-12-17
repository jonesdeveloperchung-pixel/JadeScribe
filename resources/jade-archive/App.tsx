import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CatalogGrid from './components/CatalogGrid';
import ItemDetail from './components/ItemDetail';
import IngestModal from './components/IngestModal';
import { JadeItem } from './types';

// Seed data to make the app look good initially
const SEED_DATA: JadeItem[] = [
  {
    id: '1',
    itemCode: 'PA-0921_GY',
    title: 'Jade Pendant – Guanyin',
    descriptionHero: 'Carved from translucent icy jade, this pendant depicts Guanyin, the Bodhisattva of Compassion, in a posture of serene meditation. The stone possesses a watery luminosity that seems to glow from within, perfectly complementing the soft, fluid lines of the deity’s robes. The craftsmanship is exquisite, capturing a gentle benevolent expression that invites a sense of inner peace and spiritual clarity.',
    attributes: {
      color: 'Icy White with faint green floating flowers',
      carvingStyle: 'High relief with matte finish',
      finish: 'Glassy luster',
      symbolism: 'Compassion, mercy, and protection from harm.',
    },
    imageUrl: 'https://picsum.photos/seed/jade1/800/1000',
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    itemCode: 'PA-1104_DR',
    title: 'Jade Pendant – Coiled Dragon',
    descriptionHero: 'A powerful representation of the mythical dragon, coiled in dynamic tension, ready to ascend. The jade material is a rich, oily spinach green, lending the creature a sense of ancient gravitas and vitality. Every scale is meticulously detailed, creating a tactile texture that contrasts with the smooth, polished curves of the dragon’s body. It is a commanding piece, embodying authority and auspicious energy.',
    attributes: {
      color: 'Spinach Green (Dark)',
      carvingStyle: 'Openwork carving',
      finish: 'Greasy luster',
      symbolism: 'Power, strength, and good fortune.',
    },
    imageUrl: 'https://picsum.photos/seed/jade2/800/1000',
    createdAt: new Date().toISOString(),
  },
    {
    id: '3',
    itemCode: 'PA-0315_BB',
    title: 'Jade Pendant – Lucky Bamboo',
    descriptionHero: 'Minimalist and elegant, this pendant mimics the segmented form of a bamboo stalk. The jade is a vibrant apple green, symbolizing the fresh vitality of spring growth. The simple, geometric carving highlights the stone’s exceptional translucency and uniform color. It speaks of resilience and integrity—bending in the wind but never breaking.',
    attributes: {
      color: 'Apple Green',
      carvingStyle: 'Round carving (cylindrical)',
      finish: 'Vitreous',
      symbolism: 'Resilience, longevity, and step-by-step promotion.',
    },
    imageUrl: 'https://picsum.photos/seed/jade3/800/1000',
    createdAt: new Date().toISOString(),
  }
];

const App: React.FC = () => {
  const [items, setItems] = useState<JadeItem[]>(SEED_DATA);
  const [selectedItem, setSelectedItem] = useState<JadeItem | null>(null);
  const [isIngestOpen, setIsIngestOpen] = useState(false);

  // Lock body scroll when modal is open
  useEffect(() => {
    if (selectedItem || isIngestOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }, [selectedItem, isIngestOpen]);

  const handleSaveNewItem = (newItem: JadeItem) => {
    setItems(prev => [newItem, ...prev]);
  };

  return (
    <div className="min-h-screen bg-stone-50 text-stone-800 font-sans selection:bg-jade-200 selection:text-jade-900">
      
      {/* Main Layout */}
      <Header onOpenIngest={() => setIsIngestOpen(true)} />
      
      <main>
        <div className="bg-stone-100 py-16 text-center border-b border-stone-200">
          <div className="max-w-2xl mx-auto px-4">
            <h2 className="font-serif text-3xl md:text-4xl text-stone-800 mb-4 italic">
              "Gold has a price, but jade is priceless."
            </h2>
            <p className="text-stone-500 font-light tracking-wide text-sm">
              AN ARCHIVE OF IMPERIAL CRAFTSMANSHIP
            </p>
          </div>
        </div>
        
        <CatalogGrid 
          items={items} 
          onSelectItem={setSelectedItem} 
        />
      </main>

      <footer className="bg-stone-900 text-stone-400 py-12 border-t border-stone-800">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="font-serif text-lg text-stone-300 mb-2">JADE ARCHIVE</p>
          <p className="text-xs uppercase tracking-widest opacity-50">&copy; {new Date().getFullYear()} Catalog System</p>
        </div>
      </footer>

      {/* Overlays */}
      {selectedItem && (
        <ItemDetail 
          item={selectedItem} 
          onClose={() => setSelectedItem(null)} 
        />
      )}

      <IngestModal 
        isOpen={isIngestOpen} 
        onClose={() => setIsIngestOpen(false)}
        onSave={handleSaveNewItem}
      />

    </div>
  );
};

export default App;
