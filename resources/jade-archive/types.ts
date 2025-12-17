export interface JadeAttributes {
  color: string;
  carvingStyle: string;
  finish: string;
  symbolism: string;
}

export interface JadeItem {
  id: string;
  itemCode: string;
  title: string;
  descriptionHero: string; // The poetic primary description
  attributes: JadeAttributes;
  imageUrl: string;
  createdAt: string;
}

export interface GenerationState {
  isGenerating: boolean;
  error: string | null;
}
