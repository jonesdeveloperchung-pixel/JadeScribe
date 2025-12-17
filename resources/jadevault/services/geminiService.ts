import { GoogleGenAI, Type } from "@google/genai";
import { ItemCode, PendantDescription } from "../types";

// Helper to convert File to Base64
const fileToGenerativePart = async (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      // Remove data URL prefix (e.g., "data:image/jpeg;base64,")
      const base64Data = base64String.split(',')[1];
      resolve(base64Data);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export const detectItemCodes = async (imageFile: File): Promise<ItemCode[]> => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) throw new Error("API Key not found");

  const ai = new GoogleGenAI({ apiKey });
  const base64Data = await fileToGenerativePart(imageFile);

  const prompt = `
    Analyze this image of a jewelry tray containing jade pendants. 
    Identify all visible item code tags. 
    The codes usually look like 'PA-0425_AF' or similar alphanumeric sequences.
    Return a list of detected codes and their approximate location (e.g., "Top Left", "Center").
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: {
        parts: [
          { inlineData: { mimeType: imageFile.type, data: base64Data } },
          { text: prompt }
        ]
      },
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            codes: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  code: { type: Type.STRING },
                  location: { type: Type.STRING }
                }
              }
            }
          }
        }
      }
    });

    const text = response.text;
    if (!text) return [];
    
    const data = JSON.parse(text);
    return data.codes || [];

  } catch (error) {
    console.error("Error detecting codes:", error);
    throw new Error("Failed to detect item codes. Please try again.");
  }
};

export const generateLuxuryDescription = async (imageFile: File, itemCode: string): Promise<PendantDescription> => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) throw new Error("API Key not found");

  const ai = new GoogleGenAI({ apiKey });
  const base64Data = await fileToGenerativePart(imageFile);

  const prompt = `
    You are an expert gemologist and luxury copywriter specializing in Jade.
    Focus exclusively on the jade pendant associated with the item code label "${itemCode}".
    
    Please provide:
    1. A refined Title.
    2. A detailed Visual Description (color tone, translucency, carving details).
    3. Cultural Symbolism (meaning of the motif, e.g., protection, wealth).
    4. A Poetic, Market-Ready Description suitable for a high-end catalog (calm, premium, timeless tone).
    
    Do not invent details not visible, but use evocative language for what is there.
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash", 
      contents: {
        parts: [
          { inlineData: { mimeType: imageFile.type, data: base64Data } },
          { text: prompt }
        ]
      },
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            itemCode: { type: Type.STRING },
            title: { type: Type.STRING },
            visualDescription: { type: Type.STRING },
            symbolism: { type: Type.STRING },
            poeticCopy: { type: Type.STRING },
          }
        }
      }
    });

    const text = response.text;
    if (!text) throw new Error("No description generated");

    const data = JSON.parse(text);
    return { ...data, itemCode };

  } catch (error) {
    console.error("Error generating description:", error);
    throw new Error("Failed to generate description.");
  }
};
