import os
import time
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(
    api_key=os.environ["EURI_API_KEY"],
    base_url=os.environ["EURI_BASE_URL"],
)
_CHAT_MODEL = os.environ["CHAT_MODEL"]

_total_tokens = 0
# running total across the current question, reset by reset_token_count() at the start of each run

def reset_token_count():
    global _total_tokens
    _total_tokens = 0

def get_token_count() -> int:
    return _total_tokens


class EuriChatModel:
    # single client wrapper so grading, rewriting, generation, and validation all use the same client
    def __call__(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        # model is optional: pass a different model string to override CHAT_MODEL for this one call
        used_model = model or _CHAT_MODEL

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            start = time.perf_counter()
            try:
                response = _client.chat.completions.create(
                    model=used_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                break
                # success: exit the retry loop
            except (openai.InternalServerError, openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError):
                if attempt == max_attempts:
                    raise
                    # out of retries, let the error surface for real
                wait = 5 * attempt
                print(f"  [{used_model}] server error, retrying in {wait}s (attempt {attempt}/{max_attempts})")
                time.sleep(wait)


        elapsed = time.perf_counter() - start
        # perf_counter measures wall-clock time, so this includes real network wait, not just CPU time

        tokens = response.usage.total_tokens if response.usage else "n/a"
        # usage may be missing on some providers, so this avoids crashing just to print a stat
        if isinstance(tokens, int):
            global _total_tokens
            _total_tokens += tokens
        print(f"  [{used_model}] {tokens} tokens, {elapsed:.1f}s")

        return response.choices[0].message.content