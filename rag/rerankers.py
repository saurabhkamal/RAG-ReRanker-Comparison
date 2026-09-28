# rag/rerankers.py
# Stage 2 of the pipeline: reorder the Top 20 chunks from retriever.py by how well they answer the question.
# All four rerankers will live in this file; each takes the same 20 chunks and returns them reordered.
# generate.py keeps only the first 5; compare.py shows the full before/after order.

import time       # used to measure how long each reranker takes
import torch      # runs the model's calculations
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# AutoTokenizer: turns text into the number IDs the model reads
# AutoModelForSequenceClassification: loads a model that outputs one score per input; our cross-encoder is this kind

TOP_N = 5    # reranked chunks go to the LLM in the end




def _apply_scores(chunks: list[dict], scores: list[float]) -> list[dict]:     # shared helper used by every reranker
    # takes the chunks and their new scores, puts the scores on the chunks
    # chunks: the chunks from vector search, e.g. [A, B, C]
    # scores: one new score per chunk, in the same order, e.g. [2.1, 6.5, -1.3]
    # -> list[dict]: it gives back a list of chunks

    # ---------- 1. Put each score onto a copy of its chunk ----------

    scored = [{**chunk, "rerank_score": float(score)} for chunk, score in zip(chunks, scores)]
    # zip(chunks, scores) lines the two lists up side by side:
    #     (A, 2.1)   (B, 6.5)   (C, -1.3)
    #
    # "for chunk, score in ..." takes each pair one at a time,
    #  {**chunk, "rerank_score": float(score)} builds a NEW dictionary:
    #       **chunk copies everything already in the chunk (id, text, source, page, vector_rank, score)
    #       "rerank_score": ... adds one new entry holding the reranker's score


    # ---------- 2: sort by the new score, best first ----------
    
    scored.sort(key=lambda c: c["rerank_score"], reverse=True)
    # key=... tells sort WHAT to compare:  look at c["rerank_score"]
    # lambda: "given c, return its rerank_score"
    # result: scored = [B (6.5),  A (2.1),  C (-1.3)]

    # ---------- 3: number the new order ----------

    for new_rank, chunk in enumerate(scored, start=1):
        chunk["rerank_rank"] = new_rank
        # enumerate hands out each chunk with a counter starting at 1:
        #     (1, B)   (2, A)   (3, C)
        # each chunk gets its new position written onto it
        #
        # result:
        #     B: rerank_rank 1   (vector_rank was 2)  -> moved up
        #     A: rerank_rank 2   (vector_rank was 1)  -> moved down
        #     C: rerank_rank 3   (vector_rank was 3)  -> stayed
        #
        # the old vector_rank is still on every chunk, which is how
        # compare.py would show "was 2nd, now 1st"
    
    return scored   
        # all chunks, in the reranker's order, each carrying:
        # its old rank (vector_rank), its new score (rerank_score), and its new rank (rerank_rank)


class CrossEncoderReRanker:
    # reranker 1: a small model that reads the question and a chunk TOGETHER and outputs one relevance score

    name = "cross-encoder"     # a short label used when printing results

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # loads the model's tokenizer, which splits the text into pieces and turns them into numbers
        # this model was trained on real search questions paired with passages that answer them
        # first run downloads it from Hugging Face; later runs reuse the saved copy

        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        # loads the cross-encoder model itself  (about 90 MB on the first run)

        self.model.eval()     # switches the model to "use" mode instead of "training" mode, so results are stable

    def __call__(self, query: str, chunks: list[dict]) -> list[dict]:
        # lets you use the reranker like a function: reranker(query, chunks)

        texts = [chunk["text"] for chunk in chunks]    # takes just the text out of each of the 20 chunks

        inputs = self.tokenizer(
            [query] * len(texts),    # the question repeated 20 times, one copy for each chunk
            texts,                 # the 20 chunk texts; the tokenizer joins each one with its copy of the question into ONE input
            padding=True,          # pads shorter inputs so all 20 have the same length and can be processed together
            truncation=True,        
            max_length=512,        # cuts any input longer than 512 tokens, the most this model can read at once
            return_tensors="pt",   # returns the inputs in the format torch expects
        )

        with torch.no_grad():
            # We are only scoring, not training, so torch can skip the extra bookkeeping and run faster
            scores = self.model(**inputs).logits.squeeze(-1).tolist()
            # runs all 20 questions + chunk inputs through the model at once
            # .logits hold the raw scores; .squeeze(-1) and .tolist() turn them into a plain list of 20 numbers
            # higher = more relevant; negative is fine, only the order matters

        
        return _apply_scores(chunks, scores)     # attach scores, sort, and number the new ranks



if __name__ == "__main__":

    from rag.retriever import retrieve              # stage 1: fetch the Top 20 chunks for a question from Qdrant to rerank
    from eval.test_queries import TEST_QUERIES      # the 10 labelled test questions
    case = TEST_QUERIES[7]                      # same PCI DSS Requirement 3 question as on retriever.py, so you can compare against that output
    chunks = retrieve(case["query"])            # runs the vector search for that question and gets the Top 20 chunks

    reranker = CrossEncoderReRanker()          # load the model once before the timer starts, so loading time isn't counted as reranking time

    start = time.perf_counter()
    reranked = reranker(case["query"], chunks)
    elapsed = time.perf_counter() - start
    # measures only the reranking itself

    print(case["query"])
    print(f"answer is on: {case['relevant_sources']}")
    print(f"{reranker.name}: reranked {len(chunks)} chunks in {elapsed:.2f}s\n")

    print(" new  old  move    score  source / page")
    # column headings: new rank, old vector rank, how far it moved, the reranker's score, where the chunk is from

    for c in reranked:    # goes through the chunks in the reranker's new order

        move = c["vector_rank"] - c["rerank_rank"]
        # positive = moved up, negative = moved down, 0 = stayed put
        # e.g. was 7th, now 2nd: 7 - 2 = +5

        move_label = f"+{move}" if move > 0 else str(move) if move < 0 else "="
        # plain text like +5, -3 or =, so it prints correctly in Git Bash

        marker = "  <- answer page" if (c["source"], c["page"]) in case["relevant_sources"] else ""

        print(f"{c['rerank_rank']:4d} {c['vector_rank']:4d}  {move_label:>4} {c['rerank_score']:8.3f}  {c['source'][:30]} p.{c['page']}{marker}")
        # one line per chunk: new rank, old rank, movement, score, PDF name (cut to 30 characters), page, marker

        if c["rerank_rank"] == TOP_N:
            print("  ---- only the chunks above this line go to the LLM ----")
            # draws a line under the 5th chunk, to show where the cut happens
