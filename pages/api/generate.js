import { OpenAI } from 'openai';
import cors from 'cors';

// Initialize CORS middleware
const corsMiddleware = cors({
  origin: '*',
  methods: ['POST'],
});

// Helper function to run middleware
function runMiddleware(req, res, fn) {
  return new Promise((resolve, reject) => {
    fn(req, res, (result) => {
      if (result instanceof Error) {
        return reject(result);
      }
      return resolve(result);
    });
  });
}

export default async function handler(req, res) {
  // Run the CORS middleware
  await runMiddleware(req, res, corsMiddleware);

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const { prompt, mode } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
    
    // Juici agent system prompt
    const systemPrompt = `You are juici, a high-performance general assistant built for real-world tasks. You can summarize, create, research, and plan with precision. You're fast, direct, and helpful — but always professional. Your goal is to make things happen, not just answer questions. You're built by juici.ai and deployed for general business use.`;
    
    // Modify the prompt based on mode if provided
    let modifiedPrompt = prompt;
    if (mode) {
      switch (mode) {
        case 'summarize':
          modifiedPrompt = `Please summarize the following concisely while preserving key information: ${prompt}`;
          break;
        case 'expand':
          modifiedPrompt = `Please expand on the following with more detail and depth: ${prompt}`;
          break;
        case 'rewrite':
          modifiedPrompt = `Please rewrite the following in a clear, professional style: ${prompt}`;
          break;
        case 'task':
          modifiedPrompt = `Please create a structured plan or outline for the following task: ${prompt}`;
          break;
      }
    }

    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: modifiedPrompt }
      ],
      temperature: 0.7,
      max_tokens: 2000,
    });

    return res.status(200).json({
      success: true,
      data: response.choices[0].message.content
    });
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Something went wrong'
    });
  }
}