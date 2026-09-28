# rag/retriever.py
# Stage 1 of the pipeline: fetch the Top 20 chunks for a question from Qdrant.
# Read-only: this repo never writes to the collection: ReRankEval's ingest.py built it
# rerankers.py reorders this list; compare.py shows it as the "before" ranking.

import os                                    # gives access to environment variables
from dotenv import load_dotenv               # load environment variables
from qdrant_client import QdrantClient       # Python talk to Qdrant cloud database
from rag.embedding import EuriEmbedder       # turn text into vectors

load_dotenv()       # reads the env

_client = QdrantClient(  # creates one connection to Qdrant, reused for every search in this file
    url=os.environ["QDRANT_URL"],
    # the address of your Qdrant Cloud cluster, taken from .env
    api_key=os.environ["QDRANT_API_KEY"],
    timeout=60,        # wait up to 60 seconds for Qdrant to reply before giving up
)

_COLLECTION = os.environ["QDRANT_COLLECTION"]   # the name of the collection to search: "payments_docs", where the 1,507 chunks live

_embedder = EuriEmbedder()     # creates the embedder once, so every question is turned into a vector the same way

CANDIDATE_K = 20   # chunks vector search hands to the reranker; the reranker later keeps only 5

def retrieve(query: str, top_k: int = CANDIDATE_K) -> list[dict]:
    # give it a question, get back the top_k most similar chunks
    # top_k is 20.

    query_vector = _embedder([query])[0]   # turns the question into a vector; the embedder expects a list. 
                                           # and take [0], the first (and only) vector it returns
    
    results = _client.query_points(collection_name=_COLLECTION, query=query_vector, limit=top_k)
    # asks Qdrant: in this collection, which chunks' vectors are closest to this question's vector?"
    # Qdrant returns the closest top_k chunks, already sorted from the most to least similar

    return [    # builds and returns a list with one small dictionary per chunk
        {
            "id": point.id,           # the chunk's unique ID in Qdrant, useful for matching same chunk across rerankers
            "vector_rank": rank,      # the chunk's position from vector search: 1 = most similar, 20 = least
            "score": point.score,     # how similar the chunk is to the question (cosine similarity, higher = closer)
            **point.payload           # unpacks the stored details of the chunk into this dictionary: text, source, page      
        }
        for rank, point in enumerate(results.points, start=1)   # going through Qdrant's results one by one, counts them as it goes, so each chunk gets rank
    ]

if __name__ == "__main__":
    # runs directly and not when another file imports retrieve()

    from eval.test_queries import TEST_QUERIES    # loads the 10 test questions, each with the PDF page that holds its answer

    case = TEST_QUERIES[7]                  # picks the 8th question 
    chunks = retrieve(case["query"])        # runs the vector search for that question and gets the Top 20 chunks
    print(case["query"])                    # shows the question 
    print(f"answer is on: {case['relevant_sources']}\n")     # shows which PDF and page hold the correct answer, then a blank line

    for c in chunks:            # goes through the 20 chunks one at a time, in vector-search order
        marker = "  <- answer page" if (c["source"], c["page"]) in case["relevant_sources"] else ""
        # if this chunk comes from the correct PDF and page, add a marker so it stands out otherwise add nothing
        
        print(f"{c['vector_rank']:2d} {c['score']:.3f} {c['source'][:45]:45s} p.{c['page']}{marker}")
        # prints one line per chunk: rank, score (3 decimals), PDF name (cut to 45 characters
        # and padded so columns line up), page number, and the marker if it's the answer page
