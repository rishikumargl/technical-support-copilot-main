const OpenAI = require('openai');

const client = new OpenAI({
  apiKey: 'ollama',
  baseURL: 'http://localhost:11434/v1',
});

console.log('[CLASSIFIER] Using local Ollama at http://localhost:11434');

const technicalKeywords = [
  'error',
  'bug',
  'crash',
  'timeout',
  'failed',
  'exception',
  'code ',
  'troubleshoot',
  'debug',
  'fix',
  'config',
  'setup',
  'install',
  'deploy',
  'kubectl',
  'docker',
  'api',
  '502',
  '500',
  '403',
  '404',
];

async function classifyQuery(query) {
  console.log('[CLASSIFIER] Calling Ollama mistral...');
  try {
    const response = await client.chat.completions.create({
      model: 'mistral',
      messages: [
        {
          role: 'system',
          content: `You are a query classifier. You MUST respond with ONLY one word: either CHAT or RETRIEVE.

CHAT: General greetings, small talk, "how are you", "hello", conversational questions.
RETRIEVE: Technical questions, "what is", "how do", "define", "explain", definitions, documentation lookups, troubleshooting, configuration, error codes.

Examples:
- "hi" -> CHAT
- "what is RAG?" -> RETRIEVE
- "what is SOC?" -> RETRIEVE
- "how do I fix X?" -> RETRIEVE
- "hello there" -> CHAT

Respond with ONLY the word: CHAT or RETRIEVE`,
        },
        { role: 'user', content: query },
      ],
      temperature: 0.0,
      max_tokens: 10,
    });
    const classification = response.choices[0].message.content.trim().toUpperCase();
    console.log('[CLASSIFIER] Ollama response:', classification);

    if (classification.includes('RETRIEVE')) {
      return 'RETRIEVE';
    } else if (classification.includes('CHAT')) {
      return 'CHAT';
    } else {
      console.warn('[CLASSIFIER] Unexpected response, defaulting to RETRIEVE');
      return 'RETRIEVE';
    }
  } catch (error) {
    console.error('[CLASSIFIER] Ollama call failed:', error.message);
    console.error('[CLASSIFIER] Defaulting to RETRIEVE');
    return 'RETRIEVE';
  }
}

module.exports = { classifyQuery };
