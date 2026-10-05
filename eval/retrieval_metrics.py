# eval/retrieval_metrics.py
# Step 2 of the evaluation: the six retrieval metrics.
# They answer one question in different ways: "did the right pages end up near the top of the list?"
#
# Inputs used by every metric:
#     chunks         = a ranked list of chunks (from vector search or a reranker), best first
#     relevant_pages = from eval_dataset.py, e.g. [(FCA, 7, 2), (FCA, 76, 2), (FCA, 77, 1)]
#     k              = how many chunks from the top to look at; 5, because only the Top 5 reach the LLM
#
# One rule used throughout: each relevant PAGE counts only once.
# A long page can be split into 2 chunks; if both appear, only the first one counts as a "find".

import math    # used by NDCG

def grades_in_order(chunks: list[dict], relevant_pages: list) -> list[int]:
    # turns the ranked chunks into a list of grades, one per position:
    #     2 = chunk from a page that contains the answer
    #     1 = chunk from a partly relevant page
    #     0 = not relevant, OR a page that was already counted higher up
    #
    # EXAMPLE: relevant pages 7 (grade 2), 76 (grade 2), 77 (grade 1)
    #     chunks in order:  p.76, p.3, p.7, p.76, p.9, p.77
    #     grades:           [2,   0,   2,   0,    0,   1]
    #                                       ^ second p.76 chunk: page already counted, so 0

    grade_of_page = {(source, page): grade for source, page, grade in relevant_pages}
    # a lookup table: (pdf, page) -> grade, e.g. {(FCA, 7): 2, (FCA, 76): 2, (FCA, 77): 1}

    seen = set()   # pages already counted, so a second chunk from the same page scores 0

    grades = []     # Empty list, which will get one grade per chunk, in the same order as the chunks.
    for chunk in chunks:    # goes through the ranked chunks
        page = (chunk["source"], chunk["page"])     # make a label for this chunk's page (PDF and page number)
        if page in grade_of_page and page not in seen:     # two checks both must be true
            grades.append(grade_of_page[page])         # add this page's grade to the list
            seen.add(page)          # second page won't be counted.
        else:
            grades.append(0)        # either the page isn't relevant, or it was already counted higher up.
    return grades             # [2, 0, 2, 0, 0, 1]

# hit@k
def hit_rate_at_k(grades: list[int], k:int) -> float:
    # EXAMPLE: grades [2, 0, 2, 0, 0, 1], k = 5  ->  yes  ->  1.0
    return 1.0 if any(grade > 0 for grade in grades[:k]) else 0.0
    # 1 if ANY relevant page is in the top k, otherwise 0
    # "did the LLM get at least one useful page?"


# precision@k
def precision_at_k(grades: list[int], k:int) -> float:
    # EXAMPLE: grades [2, 0, 2, 0, 0, 1], k = 5  ->  2 relevant out of 5  ->  0.4
    return sum(1 for grade in grades[:k] if grade > 0) / k
    # out of the top k chunks, what fraction are relevant pages?
    # "how much of what the LLM sees is useful?"


# recall@k
def recall_at_k(grades: list[int], relevant_pages: list, k:int) -> float:
    # Example: grades [2, 0, 2, 0, 0, 1], relevant_pages [(FCA, 7, 2), (FCA, 76, 2), (FCA, 77, 1)], k = 5
    # 2 relevant pages found out of 3 total relevant pages -> 0.666
    return sum(1 for grade in grades[:k] if grade > 0) / len(relevant_pages)
    # out of all the relevant pages, what fraction are in the top k chunks?


# MRR - Mean Reciprocal Rank
def reciprocal_rank(grades: list[int]) -> float:
    # EXAMPLE: grades [2, 0, 2, 0, 0, 1]  ->  first relevant at position 1  ->  1/1 = 1.0
    # "how high is the first useful page?"   1st -> 1.0,  2nd -> 0.5,  3rd -> 0.333,  15th -> 0.067
    # averaged over all questions, this becomes MRR (Mean Reciprocal Rank)
    for position, g in enumerate(grades, start=1):
        if g > 0:
            return 1.0 / position
    return 0.0

# Mean Average Precision (MAP)
def average_precision(grades: list[int], relevant_pages: list) -> float:
    # every time a relevant page appears, take the precision at that point, then average them
    # rewards putting ALL the relevant pages high, not just the first one
    # averaged over all questions, this becomes MAP (Mean Average Precision)
    #
    # EXAMPLE: grades [2, 0, 2, 0, 0, 1], 3 relevant pages
    #     relevant at position 1: precision so far = 1/1 = 1.0
    #     relevant at position 3: precision so far = 2/3 = 0.667
    #     relevant at position 6: precision so far = 3/6 = 0.5
    #     average precision = (1.0 + 0.667 + 0.5) / 3 = 0.722
    found = 0
    total = 0.0
    for position, grade in enumerate(grades, start=1):
        if grade > 0:
            found += 1
            total += found / position
    return total / len(relevant_pages)

# NDCG - Normalized Discounted Cumulative Gain
def ndcg_at_k(grades: list[int], relevant_pages: list, k: int) -> float:
    # EXAMPLE: grades [2, 0, 2, 0, 0, 1], k = 5    (gain = 2^grade - 1, so grade 2 -> 3, grade 1 -> 1)
    #     DCG       = 3/1 + 3/2                        = 4.5
    #     ideal     = 3/1 + 3/1.585 + 1/2              = 5.393   (grades 2, 2, 1 at positions 1, 2, 3)
    #     NDCG@5    = 4.5 / 5.393                      = 0.834
    dcg = sum((2 ** g - 1) / math.log2(position + 1) for position, g in enumerate(grades[:k], start=1))
    ideal_grades = sorted((grade for _, _, grade in relevant_pages), reverse=True)[:k]
    ideal_dcg = sum((2 ** g - 1) / math.log2(position + 1) for position, g in enumerate(ideal_grades, start=1))
    
    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0

def evaluate_retrieval(chunks: list[dict], relevant_pages: list, k: int = 5) -> dict:
    # runs all six metrics on one ranked list for one question, and returns them together in a dictionary
    # run_evaluation.py calls this once per question per configuration, then averages the results

    if not relevant_pages:
        return None
        # unanswerable question: there are no right pages, so retrieval can't be scored

    grades = grades_in_order(chunks, relevant_pages)
    return {
        f"hit_rate@{k}": hit_rate_at_k(grades, k),
        f"precision@{k}": precision_at_k(grades, k),
        f"recall@{k}": recall_at_k(grades, relevant_pages, k),
        "mrr": reciprocal_rank(grades),
        "map": average_precision(grades, relevant_pages),
        f"ndcg@{k}": ndcg_at_k(grades, relevant_pages, k)
    }
    # MRR and MAP look at the whole list (all 20 chunks), not just the top k, so they still give credit
    # for a relevant page that appears at position 6th or 15th, even though the LLM never sees it;
    # the @k metrics only look at the top 5 chunks.

if __name__ == "__main__":
    # running directly: python -m eval.retrieval_metrics

    # ---------- check 1: the example from the comments, no API calls ----------
    from eval.eval_dataset import FCA
    example_pages = [(FCA, 7, 2), (FCA, 76, 2), (FCA, 77, 1)] 
    # p.7 and p.76 contain the answer, p.77 partly answer for Q6, other grades (relevant answer, relevant answer, partly relevant answer) are 2, 2, 1
    example_chunks = [{"source": FCA, "page": p} for p in [76, 3, 7, 76, 9, 77]]
    # list of chunks in order, with duplicates and irrelevant pages from the FCA PDF, shown by page number for Q6.
    print("Worked example (should match the comments):")
    for name, value in evaluate_retrieval(example_chunks, example_pages).items():
        print(f"  {name:13}: {value:.3f}")

    # ---------- check 2: one real question, vector search only (1 embedding call) ----------
    from rag.retriever import retrieve
    from eval.eval_dataset import EVAL_DATASET

    case = EVAL_DATASET[5]  # "query": "What is the temporary permissions regime (TPR) for EEA payment firms?"
    chunks = retrieve(case["query"])
    print(f"\nReal question: {case['query']}")
    print(f"Relevant pages: {[(p, g) for _, p, g in case['relevant_pages']]}   (page, grade)")
    print(f"Vector search order (pages): {[c['page'] for c in chunks]}")
    # chunks - the 20 chunks from the retrieve()
    # c['page'] - takes the page number from each chunk.
    for name, value in evaluate_retrieval(chunks, case["relevant_pages"]).items():
        print(f"  {name:13}: {value:.3f}")
