import { GoogleGenAI, Type } from "@google/genai";
import "dotenv/config";

export const ai = new GoogleGenAI({});
const MAX_STEPS = 8;                        // stop runaway loops

async function cryptoCurrency({ coin }) {
  const url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=inr&ids="
    + encodeURIComponent(coin);             // never paste model text raw into a URL
  const res = await fetch(url);
  if (!res.ok) throw new Error(`CoinGecko returned HTTP ${res.status}`);
  return res.json();
}

async function weatherInformation({ city }) {
  const key = process.env.WEATHER_API_KEY;  // key from .env, never in code
  const url = `https://api.weatherapi.com/v1/current.json?key=${key}`
    + `&q=${encodeURIComponent(city)}&aqi=no`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Weather API returned HTTP ${res.status}`);
  return res.json();
}

const toolFunctions = { cryptoCurrency, weatherInformation };

const tools = [{
  functionDeclarations: [
    {
      name: "cryptoCurrency",
      description: "Current price and market data of a cryptocurrency like bitcoin or ethereum",
      parameters: {
        type: Type.OBJECT,
        properties: { coin: { type: Type.STRING, description: "Coin id, e.g. bitcoin" } },
        required: ["coin"],
      },
    },
    {
      name: "weatherInformation",
      description: "Current weather of a city like London or Goa",
      parameters: {
        type: Type.OBJECT,
        properties: { city: { type: Type.STRING, description: "City name, e.g. Goa" } },
        required: ["city"],
      },
    },
  ],
}];

export async function runAgent(history) {
  for (let step = 1; step <= MAX_STEPS; step++) {
    const result = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: history,
      config: { tools },
    });

    const calls = result.functionCalls ?? [];
    history.push(result.candidates[0].content);     // keep the model's own turn as-is

    if (calls.length === 0) return result.text;       // no tool needed → final answer

    const responses = [];
    for (const { name, args } of calls) {             // handle EVERY call, not only [0]
      let output;
      try {
        if (!toolFunctions[name]) throw new Error(`Unknown tool: ${name}`);
        output = await toolFunctions[name](args);
      } catch (err) {
        output = { error: err.message };              // the model sees the failure
      }
      responses.push({ functionResponse: { name, response: { result: output } } });
    }
    history.push({ role: "user", parts: responses });
  }
  return "Sorry, I could not finish within the step limit.";
}
