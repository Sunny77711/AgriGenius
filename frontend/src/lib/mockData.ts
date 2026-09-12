import type { ChatResponse, HealthResponse } from './types';

export const mockChatResponse1: ChatResponse = {
  answer: "For wheat crop irrigation, the first irrigation should be given at the Crown Root Initiation (CRI) stage, which is 20-25 days after sowing. The second irrigation is at the tillering stage (40-45 days), and the third at the late jointing stage (60-65 days). Make sure to apply light irrigation and avoid waterlogging.",
  language: "en",
  grounded: true,
  confidence: "high",
  sources: [
    {
      rank: 1,
      text: "Farmer asked about irrigation scheduling for wheat crop. First irrigation must be provided at CRI stage (20-25 days). Second irrigation at tillering stage (40-45 days). Ensure adequate moisture.",
      similarity: 0.89,
      metadata: {
        Crop: "Wheat",
        DistrictName: "BASTI",
        QueryType: "Water Management",
        StateName: "UTTAR PRADESH",
        source: "KCC"
      }
    },
    {
      rank: 2,
      text: "Advised farmer to apply light irrigation in wheat field at CRI stage. Do not overwater as it affects root development.",
      similarity: 0.82,
      metadata: {
        Crop: "Wheat",
        DistrictName: "LUCKNOW",
        QueryType: "Water Management",
        StateName: "UTTAR PRADESH",
        source: "KCC"
      }
    }
  ]
};

export const mockChatResponseHindi: ChatResponse = {
  answer: "गेहूं की फसल में पहली सिंचाई बुवाई के 20-25 दिन बाद (CRI अवस्था) करनी चाहिए। दूसरी सिंचाई 40-45 दिन (कल्ले निकलने की अवस्था) और तीसरी सिंचाई 60-65 दिन बाद करनी चाहिए। खेत में पानी रुकने न दें।",
  language: "hi",
  grounded: true,
  confidence: "high",
  sources: [
    {
      rank: 1,
      text: "किसान ने गेहूं में सिंचाई के बारे में पूछा। पहली सिंचाई 20-25 दिन (CRI स्टेज) पर करने की सलाह दी गई। दूसरी 40-45 दिन पर।",
      similarity: 0.91,
      metadata: {
        Crop: "Wheat",
        DistrictName: "GORAKHPUR",
        QueryType: "Water Management",
        StateName: "UTTAR PRADESH",
        source: "KCC"
      }
    }
  ]
};

export const mockHealthResponse: HealthResponse = {
  status: "ok",
  collection_count: 347944,
  model: "l3cube-pune/hindi-sentence-bert-nli"
};
