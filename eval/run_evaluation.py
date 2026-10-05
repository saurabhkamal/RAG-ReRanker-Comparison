# eval/run_evaluation.py
# Step 4 of the evaluation: runs every question through the chosen configuration(s) and saves all the scores.
#
#     for each question:
#         retrieve the Top 20 once
#         for each configuration in CONFIGURATIONS (default: just "cohere"):
#             rank the 20 chunks           -> retrieval metrics on the ranked list (retrieval_metrics.py)
#             keep the Top 5, write answer -> generation metrics from the judge   (generation_metrics.py)
#             save the result to results/results.json straight away
#
# Progress is saved after EVERY result. If the run stops (network error)
# run the same command again: finished results are skipped and it continues where it stopped.
#
# Run all 33 questions:          python -m eval.run_evaluation
# Quick test, first 2 questions: python -m eval.run_evaluation 2

import json
import sys
import time
from pathlib import Path
 
from rag.retriever import retrieve
from rag.rerankers import CrossEncoderReRanker, LLMReRanker, CohereReRanker, JinaReRanker, TOP_N
from rag.generate import generate_answer
from eval.eval_dataset import EVAL_DATASET
from eval.retrieval_metrics import evaluate_retrieval
from eval.generation_metrics import evaluate_generation



RESULTS_FILE = Path("results/results.json")
# where every result is saved; report.py reads this file later
 
CONFIGURATIONS = ["cohere"]     # options: "vector" (no reranking), "cross", "llm", "cohere", "jina"

def load_results() -> list[dict]:
    # reads the results saved so far, or starts with an empty list on the first run
    if RESULTS_FILE.exists():
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    return []

def save_results(results: list[dict]) -> None:
    # writes ALL results to the file; called after every single result, so nothing is lost if the run stops
    RESULTS_FILE.parent.mkdir(exist_ok=True)
    # creates the results/ folder the first time
    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


def make_rerankers() -> dict:
    # creates only the rerankers listed in CONFIGURATIONS, once; if one can't start
    # (e.g. Windows blocks torch for the cross-encoder), it is skipped with a warning instead of stopping
    rerankers = {}
    for name, reranker_class in [("cross", CrossEncoderReRanker), ("llm", LLMReRanker),
                                 ("cohere", CohereReRanker), ("jina", JinaReRanker)]:
        if name not in CONFIGURATIONS:
            continue
            # not chosen: don't create it (and don't load its model or use its API)
        try:
            rerankers[name] = reranker_class()
        except Exception as error:
            print(f"WARNING: skipping '{name}', it could not start: {error}")
    return rerankers


if __name__ == "__main__":
    how_many = int(sys.argv[1]) if len(sys.argv) > 1 else len(EVAL_DATASET)
    # how many questions to run: the number you type after the command, or all 33 if you type none

    rerankers = make_rerankers()
    # creates the reranker(s) you chose; by default just Cohere

    configurations = [config for config in CONFIGURATIONS if config == "vector" or config in rerankers]
    # the configurations that can actually run; by default ["cohere"]

    results = load_results()
    # loads results already saved from earlier runs (empty the first time)

    done = {(r["question"], r["config"]) for r in results}
    # which question + configuration pairs are already finished, e.g. {(1, "cohere"), (2, "cohere")}

    for number, case in enumerate(EVAL_DATASET[:how_many], start=1):
        # goes through the questions one by one; number = 1, 2, 3 ...; case = that question's entry

        todo = [config for config in configurations if (number, config) not in done]
        # what's still left to do for this question, e.g. ["cohere"], or [] if it's already done

        if not todo:
            continue
            # already finished: skip this question, no API calls, no tokens spent

        print(f"\nQuestion {number}/{how_many}: {case['query']}")
        # shows which question is being worked on

        chunks = retrieve(case["query"])
        # Stage 1: the Top 20 chunks from vector search

        for config in todo:
            # runs each configuration still left for this question (by default just Cohere)

            try:
                start = time.perf_counter()
                # starts the stopwatch

                ranked = chunks if config == "vector" else rerankers[config](case["query"], chunks)
                # Stage 2: rerank the 20 chunks ("vector" keeps vector search's order)

                rerank_seconds = time.perf_counter() - start
                # stops the stopwatch: how long the reranking took

                retrieval_scores = evaluate_retrieval(ranked, case["relevant_pages"], k=TOP_N)
                # the six retrieval scores (Hit Rate, Precision, Recall, MRR, MAP, NDCG)

                top_chunks = ranked[:TOP_N]
                # keeps only the Top 5, the chunks the LLM will see

                answer = generate_answer(case["query"], top_chunks)
                # Stage 3: the LLM writes the answer from those 5 chunks

                generation_scores, judgement = evaluate_generation(case["query"], top_chunks, answer, case["key_facts"])
                # the judge marks the answer: the five generation scores, plus its full reply

            except Exception as error:
                print(f"  {config:7} FAILED: {error}  (not saved; it will be retried on the next run)")
                continue
                # if anything above goes wrong, report it and move on; rerunning later will retry it

            results.append({
                "question": number,                                   # question number, e.g. 3
                "config": config,                                     # which configuration, e.g. "cohere"
                "query": case["query"],                               # the question text
                "top_pages": [chunk["page"] for chunk in top_chunks], # pages the LLM saw, e.g. [6, 6, 22, 152, 23]
                "rerank_seconds": round(rerank_seconds, 3),           # reranking time, e.g. 1.042
                "retrieval": retrieval_scores,                        # the six retrieval scores
                "generation": generation_scores,                      # the five generation scores
                "answer": answer,                                     # the LLM's answer
                "judgement": judgement,                               # the judge's full reply
            })
            # adds this result to the list

            save_results(results)
            # saves to results/results.json right away, so it isn't lost if the run stops later

            print(f"  {config:7} recall@{TOP_N} {retrieval_scores[f'recall@{TOP_N}']:.2f}  "
                  f"ndcg@{TOP_N} {retrieval_scores[f'ndcg@{TOP_N}']:.2f}  "
                  f"faithfulness {generation_scores['faithfulness']:.2f}  "
                  f"correctness {generation_scores['answer_correctness']:.2f}")
            # one short progress line, e.g. "cohere  recall@5 1.00  ndcg@5 0.92  faithfulness 1.00  correctness 0.83"

    print(f"\nDone: {len(results)} results saved in {RESULTS_FILE}")
    # final message; with all 33 questions and Cohere only, that's 33 results