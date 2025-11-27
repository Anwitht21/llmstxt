import time
import asyncio
import inspect
from typing import Callable
from .models import ProcessingResult
from .client import OpenRouterClient, RateLimitError
from .prompts import build_messages
from .validator import extract_urls, validate_llms_txt, truncate_descriptions
from config import settings

class LLMProcessor:
    def __init__(self, log_fn: Callable[[str], None] | None = None):
        self._log_fn = log_fn or (lambda x: None)
        self._is_async_log = inspect.iscoroutinefunction(log_fn) if log_fn else False

    async def log(self, message: str):
        if self._is_async_log:
            await self._log_fn(message)
        else:
            self._log_fn(message)

    async def process(self, llms_txt: str) -> ProcessingResult:
        start_time = time.time()

        if not settings.openrouter_api_key:
            return ProcessingResult.failure_result(llms_txt, "OpenRouter API key not configured")

        original_urls = extract_urls(llms_txt)
        await self.log(f"Extracted {len(original_urls)} URLs from original content")

        client = OpenRouterClient(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            temperature=settings.llm_temperature,
            log_fn=self._log_fn if not self._is_async_log else (lambda x: None)
        )

        try:
            messages = build_messages(llms_txt)
            await self.log(f"Calling OpenRouter API with model {settings.openrouter_model}...")
            enhanced_content = await client.complete(messages)

            is_valid, errors = validate_llms_txt(enhanced_content, original_urls)

            if not is_valid:
                error_msg = f"Validation failed: {'; '.join(errors[:3])}"
                await self.log(f"LLM output validation failed, using original")
                await self.log(error_msg)
                return ProcessingResult.failure_result(llms_txt, error_msg)

            enhanced_content = truncate_descriptions(enhanced_content)

            elapsed_time = time.time() - start_time
            stats = {
                "model": settings.openrouter_model,
                "time_seconds": round(elapsed_time, 2),
                "original_length": len(llms_txt),
                "enhanced_length": len(enhanced_content),
                "url_count": len(original_urls)
            }

            await self.log(f"Enhancement successful in {stats['time_seconds']}s")
            return ProcessingResult.success_result(enhanced_content, stats)

        except RateLimitError as e:
            return ProcessingResult.failure_result(llms_txt, f"Rate limit exceeded: {str(e)}")

        except Exception as e:
            error_msg = f"LLM processing error: {str(e)}"
            await self.log(error_msg)
            return ProcessingResult.failure_result(llms_txt, error_msg)
