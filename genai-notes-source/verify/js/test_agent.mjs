import { GenerateContentResponse } from "@google/genai";
process.env.GEMINI_API_KEY = "dummy";
process.env.WEATHER_API_KEY = "dummy-weather";
const { ai, runAgent } = await import("./agent_improved.mjs");

function resp(parts) {
  const r = new GenerateContentResponse();
  r.candidates = [{ content: { role: "model", parts } }];
  return r;
}
const script = [
  resp([{ functionCall: { name: "cryptoCurrency", args: { coin: "bitcoin" } } },
        { functionCall: { name: "weatherInformation", args: { city: "Goa" } } }]),
  resp([{ text: "Bitcoin is ₹90,00,000 and Goa is 29°C and sunny." }]),
];
let call = 0;
ai.models.generateContent = async (params) => {
  console.log(`--- model call ${call + 1}: history has ${params.contents.length} messages`);
  return script[call++];
};
globalThis.fetch = async (url) => {
  console.log("fetch", url.replace(/key=[^&]+/, "key=***"));
  if (url.includes("weather")) return { ok: true, json: async () => ({ current: { temp_c: 29 } }) };
  return { ok: true, json: async () => ([{ id: "bitcoin", current_price: 9000000 }]) };
};
const history = [{ role: "user", parts: [{ text: "Bitcoin price and weather in Goa?" }] }];
const answer = await runAgent(history);
console.log("ANSWER:", answer);
console.log("history roles:", history.map(h => h.role + ":" + h.parts.map(p => Object.keys(p)[0]).join("+")).join(" | "));
