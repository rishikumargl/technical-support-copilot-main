# HuggingFace Inference Integration

## Overview

The RAG system now uses **HuggingFace Inference API** for generating responses instead of OpenAI. This leverages the Llama 3.1 8B Instruct model through HuggingFace's serverless inference.

## Configuration

### Environment Variables

All configuration is in `rag/.env`:

```env
# Your HuggingFace API Token
HF_TOKEN=hf_your_token_here

# Model to use for inference
HF_INFERENCE_MODEL=meta-llama/Llama-3.1-8B-Instruct:novita
```

### How It Works

The inference service:
1. Uses HuggingFace's OpenAI-compatible API endpoint
2. Sends retrieved context + query to the model
3. Gets back a response from Llama 3.1 8B
4. Formats it with source attribution

## Components

### InferenceService (`inference_service.py`)

Main class for handling LLM inference:

```python
from inference_service import InferenceService

# Initialize
inference = InferenceService()

# Generate simple response
response = inference.generate_response(
    query="What is this?",
    context="Optional context here"
)

# Generate response with sources
result = inference.answer_with_sources(
    query="What is the policy?",
    search_results=[...search results...]
)

print(result['answer'])        # The AI response
print(result['sources'])       # Source documents
print(result['confidence'])    # Confidence score
```

## Usage in RAG Pipeline

### 1. Search Phase
```python
from hybrid_search import HybridSearchEngine

search = HybridSearchEngine(qdrant_client)
results = search.retrieve_relevant_chunks(
    query="What is the leave policy?",
    search_type="hybrid",
    top_k=5
)
```

### 2. Generation Phase
```python
from inference_service import InferenceService

inference = InferenceService()
answer = inference.answer_with_sources(
    query="What is the leave policy?",
    search_results=results
)
```

### 3. Complete Flow in Interactive Mode

Run `ask_questions.py`:
```bash
cd rag
python ask_questions.py
```

Then ask:
```
YOU: What is the leave policy?
```

The system will:
1. Search for relevant chunks
2. Display top results with scores
3. Generate an AI response using HuggingFace
4. Show confidence and sources

## API Details

### HuggingFace Inference API

**Endpoint:** `https://router.huggingface.co/v1`

**Authentication:** HF_TOKEN from environment

**Model:** `meta-llama/Llama-3.1-8B-Instruct:novita`

**Interface:** OpenAI-compatible chat completions

```python
# Behind the scenes, InferenceService does:
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

completion = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct:novita",
    messages=[
        {"role": "system", "content": "System prompt..."},
        {"role": "user", "content": "User query..."}
    ],
    temperature=0.7,
    max_tokens=512
)
```

## Methods

### `generate_response()`

Generate a response for a query with optional context.

```python
response = inference.generate_response(
    query="What is X?",
    context="Context about X...",
    system_prompt="Custom system prompt...",  # Optional
    temperature=0.7,  # 0-1, lower = more focused
    max_tokens=512    # Max response length
)
```

### `answer_with_sources()`

Generate an answer using search results as context, returning sources.

```python
result = inference.answer_with_sources(
    query="What is the leave policy?",
    search_results=search_engine.retrieve_relevant_chunks(...),
    temperature=0.7,
    max_tokens=512
)

# Returns:
{
    "answer": "The leave policy states...",
    "sources": [
        {
            "document": "HR Policy",
            "version": "1.0",
            "department": "HR",
            "category": "Policy",
            "confidence": 0.95
        }
    ],
    "confidence": 0.95,
    "model": "meta-llama/Llama-3.1-8B-Instruct:novita"
}
```

### `stream_response()`

Stream responses as they are generated (if supported).

```python
for chunk in inference.stream_response(query="What is X?"):
    print(chunk, end="", flush=True)
```

## Integration with Backend

Update backend to use inference service:

```python
from rag.inference_service import InferenceService
from rag.hybrid_search import HybridSearchEngine

@app.post('/api/chat/query')
def chat_query(data):
    question = data['question']
    
    # Search
    search_results = search_engine.retrieve_relevant_chunks(
        query=question,
        search_type="hybrid",
        top_k=5
    )
    
    # Generate response
    result = inference.answer_with_sources(question, search_results)
    
    return {
        "answer": result['answer'],
        "sources": result['sources'],
        "confidence": result['confidence']
    }
```

## Testing

Test the inference service directly:

```bash
python rag/inference_service.py
```

This will run tests:
1. Simple query test
2. Query with context
3. Answer with sources

## Advantages

✅ **Free Tier:** HuggingFace offers free inference API
✅ **Open Source:** Using open-source Llama model
✅ **No API Keys Needed:** Just use your HF token
✅ **OpenAI Compatible:** Drop-in replacement interface
✅ **Streaming Support:** Can stream responses
✅ **Multiple Models:** Can use other HF models

## Switching Models

Change the model in `.env`:

```env
# Other available models:
# HF_INFERENCE_MODEL=meta-llama/Llama-2-7b-chat:trt
# HF_INFERENCE_MODEL=mistralai/Mistral-7B-Instruct-v0.1:trt
# HF_INFERENCE_MODEL=NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO:trt

HF_INFERENCE_MODEL=meta-llama/Llama-3.1-8B-Instruct:novita
```

Then initialize a new InferenceService:

```python
inference = InferenceService(
    model="mistralai/Mistral-7B-Instruct-v0.1:trt"
)
```

## Performance Notes

- **Response Time:** 5-15 seconds depending on prompt length
- **Token Limit:** Up to 512 tokens per response (configurable)
- **Rate Limiting:** Free tier has usage limits
- **Cold Start:** First request may take longer (model loading)

## Troubleshooting

### "HF_TOKEN not found"
```bash
# Make sure .env has:
HF_TOKEN=hf_xxxxxxxxxxxx

# Or set environment variable:
export HF_TOKEN=hf_xxxxxxxxxxxx
```

### "Model not found"
```bash
# Check model name in .env
# Format: namespace/model:variant

# Valid examples:
meta-llama/Llama-3.1-8B-Instruct:novita
mistralai/Mistral-7B-Instruct-v0.1:trt
```

### "Rate limit exceeded"
- HuggingFace free tier has usage limits
- Upgrade to pro tier for higher limits
- Or self-host the model locally

### Slow responses
- First request loads the model (slow)
- Subsequent requests are faster
- Model stays warm for ~1 hour of inactivity
- Use a self-hosted solution for production

## Next Steps

1. **Backend Integration:** Update backend endpoints to use inference
2. **Frontend Updates:** Show AI responses in chat interface
3. **Streaming:** Implement response streaming for better UX
4. **Caching:** Cache responses for common queries
5. **Custom System Prompts:** Fine-tune response behavior

## Files

- `inference_service.py` - Main inference service class
- `ask_questions.py` - Interactive demo with AI responses
- `rag/.env` - Configuration (HF_TOKEN, model name)

## Resources

- HuggingFace Inference API: https://huggingface.co/inference-api
- Llama 3.1 Model Card: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
- OpenAI API Docs: https://platform.openai.com/docs/api-reference (for SDK usage)
