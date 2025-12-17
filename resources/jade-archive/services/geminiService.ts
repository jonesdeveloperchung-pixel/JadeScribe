import { GoogleGenAI, Type, Schema } from "@google/genai";
import { JadeItem } from "../types";

// Initialize Gemini Client
// Note: process.env.API_KEY is assumed to be available in the environment
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const jadeSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    title: {
      type: Type.STRING,
      description: "Format: Jade Pendant – [Motif/Figure Name]. E.g., Jade Pendant – Guanyin",
    },
    itemCode: {
      type: Type.STRING,
      description: "The item code found in the image (e.g., on a tag). If none found, generate a plausible one like PA-0425_AF.",
    },
    descriptionHero: {
      type: Type.STRING,
      description: "A poetic, refined paragraph (80-150 words) focusing on visual beauty, craftsmanship, and cultural resonance. Tone: Elegant, calm, reverent.",
    },
    attributes: {
      type: Type.OBJECT,
      properties: {
        color: { type: Type.STRING, description: "e.g., Imperial Green, Lavender, Icy White" },
        carvingStyle: { type: Type.STRING, description: "e.g., Relief carving, Openwork, Smooth polish" },
        finish: { type: Type.STRING, description: "e.g., High gloss, Matte, Glassy" },
        symbolism: { type: Type.STRING, description: "Cultural meaning of the motif." },
      },
      required: ["color", "carvingStyle", "finish", "symbolism"],
    },
  },
  required: ["title", "itemCode", "descriptionHero", "attributes"],
};

export const analyzeJadeImage = async (base64Image: string): Promise<Partial<JadeItem>> => {
  try {
    // Strip header if present to get pure base64
    const cleanBase64 = base64Image.replace(/^data:image\/(png|jpeg|jpg|webp);base64,/, "");

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: "image/jpeg", // Assuming JPEG for simplicity, API handles most standard types
              data: cleanBase64,
            },
          },
          {
            text: `Analyze this jade pendant. Act as a world-class luxury curator.
            
            1. Identify the motif (e.g., Buddha, Bamboo, Dragon).
            2. Extract the item code if visible on a tag (OCR). If not, generate a placeholder.
            3. Write a 'Hero Paragraph' description. It MUST be poetic, elegant, and culturally respectful. Avoid commercial slang. Focus on light, texture, and form.
            4. Extract visual attributes.
            
            Return JSON matching the schema.`,
          },
        ],
      },
      config: {
        responseMimeType: "application/json",
        responseSchema: jadeSchema,
        temperature: 0.4, // Lower temperature for more consistent, grounded descriptions
      },
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");

    const data = JSON.parse(text);
    
    return {
      title: data.title,
      itemCode: data.itemCode,
      descriptionHero: data.descriptionHero,
      attributes: data.attributes,
    };

  } catch (error) {
    console.error("Gemini Analysis Failed:", error);
    throw error;
  }
};
