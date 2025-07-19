import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

serve(async (req) => {
  const { prompt } = await req.json();
  const apiKey = Deno.env.get("OPENAI_API_KEY");

  const openaiResponse = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: prompt }]
    }),
  });

  const data = await openaiResponse.json();
  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json" }
  });
});