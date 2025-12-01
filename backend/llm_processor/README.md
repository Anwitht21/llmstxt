# LLM Processor Module

Post-processing enhancement for llms.txt files using OpenRouter's OSS models.

## Overview

This module adds LLM-based enhancement to improve the quality of generated llms.txt files. It takes rule-based formatter output and refines it to create better organized, more informative documentation while strictly maintaining llmstxt.org spec compliance.

## Features

- **Post-processing approach**: Rule-based formatter runs first, LLM refines output
- **Strict validation**: Ensures spec compliance and URL integrity
- **Fallback safety**: Returns original content if LLM fails or produces invalid output
- **Cost efficient**: Uses free tier (Mistral Nemo) by default
- **Opt-in**: Disabled by default, users must explicitly enable

## Architecture

```
Rule-based Formatter → LLM Post-Processor → Spec Validator → Final Output
                              ↓ (on failure)
                          Fallback to original
```

## Configuration

Add to your `.env` file:

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=x-ai/grok-4.1-fast:free  # Free tier
LLM_ENHANCEMENT_ENABLED=True  # Global killswitch
LLM_TIMEOUT_SECONDS=30.0
LLM_MAX_RETRIES=3
LLM_TEMPERATURE=0.3
```

### Get an API Key

1. Visit https://openrouter.ai/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier: 50 requests/day with Mistral Nemo

## Usage

### WebSocket API

Users can opt-in to LLM enhancement via the `llmEnhance` parameter:

```json
{
  "url": "https://example.com",
  "maxPages": 50,
  "llmEnhance": true
}
```

### Auto-Recrawl

If `LLM_ENHANCEMENT_ENABLED=true`, all auto-recrawls will use LLM enhancement.

### Programmatic Usage

```python
from llm_processor import LLMProcessor

processor = LLMProcessor(log_fn)
result = await processor.process(llms_txt)

if result.success:
    enhanced_content = result.output
    print(f"Stats: {result.stats}")
else:
    print(f"Failed: {result.error}")
    # result.output contains original content
```

## What Gets Enhanced

The LLM improves:

1. **Section Organization**: Groups related pages logically
2. **Section Names**: "Getting Started" instead of "Docs"
3. **Descriptions**: Clear, informative descriptions under 150 chars
4. **Content Prioritization**: Most important content first
5. **Site Summary**: Better H1 and blockquote

## What Never Changes

- **URLs**: Never modified, added, or removed
- **URL order**: Only section grouping changes
- **Format**: Always follows llmstxt.org spec

## Validation

Strict checks ensure:

- ✓ Exactly one H1 title
- ✓ One blockquote (under 200 chars)
- ✓ All sections use H2
- ✓ All original URLs preserved
- ✓ No hallucinated URLs
- ✓ Correct link format
- ✓ Descriptions under 150 chars

If validation fails, original content is returned with error logged.

## Module Structure

```
llm_processor/
├── __init__.py          # Exports LLMProcessor, ProcessingResult
├── models.py            # ProcessingResult dataclass
├── client.py            # OpenRouter API client
├── prompts.py           # System prompt and few-shot examples
├── validator.py         # Spec compliance validation
└── processor.py         # Main orchestration logic
```