import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(api_key=os.environ["EURI_API_KEY"],
                 base_url=os.environ["EURI_BASE_URL"],
)
_EMBED_MODEL = os.environ["EURI_EMBED_MODEL"]

BATCH_LIMIT = 100
# the EURI/Gemini embedding API rejects a single request with more than 100 items


class EuriEmbedder: 
    # Single client wrapper so ingestion and query-time embedding always use the same model
    def __call__(self, texts: list[str], on_progress=None) -> list[list[float]]:
        all_vectors = []
        total_batches = (len(texts) + BATCH_LIMIT - 1) // BATCH_LIMIT
        # rounds up, so a partial last batch still counts as one full batch
        
        for batch_num, start in enumerate(range(0, len(texts), BATCH_LIMIT), start=1):
            batch = texts[start:start + BATCH_LIMIT]
            # slices texts into groups of at most 100, so each API call stays within the limit

            response = _client.embeddings.create(model=_EMBED_MODEL, input=batch)
            all_vectors.extend(item.embedding for item in response.data)

            if on_progress:
                on_progress(batch_num, total_batches)

        return all_vectors