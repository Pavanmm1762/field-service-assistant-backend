# AI Provider Migration

The application now depends on one internal AI service interface:

```python
await ai_service.chat(...)
await ai_service.chat_with_tools(...)
await ai_service.embed(...)
await ai_service.analyze_image(...)
```

Provider SDKs are isolated in:

```text
app/services/ai/adapters/gemini.py
app/services/ai/adapters/openai_compatible.py
```

Business logic should use `get_ai_service()` from `app.services.ai.factory`.
Do not import Gemini, OpenAI, vLLM, Ollama, Azure OpenAI, OpenRouter, or Groq
clients outside adapter modules.

## Folder Structure

```text
app/
+-- services/
    +-- ai/
        +-- ai_service.py
        +-- factory.py
        +-- interfaces.py
        +-- adapters/
            +-- openai_compatible.py
            +-- gemini.py
```

## Configuration

Gemini:

```env
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.5-flash
LLM_EMBEDDING_MODEL=gemini-embedding-001
LLM_VISION_MODEL=gemini-2.5-flash
```

vLLM or another OpenAI-compatible server:

```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=Qwen3-30B-A3B
LLM_API_KEY=dummy
LLM_EMBEDDING_MODEL=Qwen3-Embedding
LLM_VISION_MODEL=Qwen3-30B-A3B
```

OpenAI, Ollama, Azure OpenAI, OpenRouter, Groq, and LiteLLM-style gateways
should use `LLM_PROVIDER=openai_compatible` with the provider's base URL,
model, and API key.

For Azure OpenAI, set:

```env
LLM_PROVIDER=openai_compatible
LLM_API_TYPE=azure
LLM_BASE_URL=https://your-resource.openai.azure.com
LLM_API_VERSION=2024-02-15-preview
LLM_MODEL=your-deployment-name
LLM_API_KEY=your-azure-openai-key
```

## Migration Steps

1. Replace `GEMINI_API_KEY` with `LLM_API_KEY`. The old variable is still read
   as a fallback for existing environments.
2. Add `LLM_PROVIDER` and model variables to `.env`.
3. Install the new dependency:

```bash
pip install -r requirements.txt
```

4. Keep application code provider-agnostic by using `get_ai_service()`.
5. To add LiteLLM later, point `LLM_BASE_URL` at the LiteLLM gateway and keep
   `LLM_PROVIDER=openai_compatible`.
