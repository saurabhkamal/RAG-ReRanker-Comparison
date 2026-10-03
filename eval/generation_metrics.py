# eval/generation_metrics.py
# The five generation metrics, scored by an LLM judge
# The judge reads the question, the Top 5 chunks, the generated answer, and the expected answer,
# and returns COUNTS (claims, supported claims, useful chunks, key facts covered)
# This file can turn those counts into scores with simple division, so every score can be checked by hand.
#
#       faithfulness        =  supported claims / total claims                     (answer vs chunks)
#       hallucination       = 1 if ANY claim is unsupported, else 0                (answer vs chunks)
#       answer_relevance    = 1.0 / 0.5 / 0.0: does the answer address the question? (answer vs question)
#       context_relevance   = useful chunks ÷ chunks given to the LLM              (chunks vs question)
#       answer_correctness  = key facts covered ÷ key facts in the expected answer (answer vs expected answer) 
#
# run_evaluation.py calls evaluate_generation() once per question per configuration.

import json
from rag.chat_model import EuriChatModel

_JUDGE_SYSTEM_PROMPT = "You are a strict evaluator of answers produced by a retrieval-augmented system. Reply only with JSON."
# tells the judge its role, and that the reply must be JSON so code can read it
 
_JUDGE_PROMPT = """Evaluate the ANSWER below.

QUESTION:
{query}

CONTEXT (the only chunks the answering system was given):
{context}

ANSWER (written by the system):
{answer}

KEY FACTS (what a complete answer should contain):
{key_facts}

Do these four tasks:
1. Split the ANSWER into separate factual claims. For each claim, decide if the CONTEXT supports it.
   A claim that is true in real life but not stated in the CONTEXT is NOT supported.
   Citations like [file p.7] are not claims; ignore them.
   If the ANSWER only says the documents don't answer the question, it has 0 claims.
2. Decide if the ANSWER addresses the QUESTION: 1.0 = fully, 0.5 = partly or drifts off topic, 0.0 = not at all.
3. List the numbers of the CONTEXT chunks that directly help answer the QUESTION.
   Count a chunk only if it contains information that answers part of the QUESTION.
   A chunk that only mentions the same topic, without answering any part of the QUESTION, does not count.
4. For each KEY FACT, decide if the ANSWER contains it (same meaning, any wording).

Reply with ONLY this JSON:
{{
  "claims_total": <number of claims in the ANSWER>,
  "claims_supported": <how many of them the CONTEXT supports>,
  "unsupported_claims": [<each unsupported claim, as short text>],
  "answer_relevance": <1.0, 0.5 or 0.0>,
  "useful_chunks": [<chunk numbers, e.g. 1, 3>],
  "facts_covered": [<numbers of the KEY FACTS the ANSWER contains, e.g. 1, 3>]
}}"""
# the instruction; {query}, {context}, {answer} and {expected_answer} are filled in for every answer
# {{ and }} are written double so Python's .format() leaves them as real { } in the JSON example
# CONTEXT: the same 5 chunks the LLM received
# Top 20 (vector search)  →  rerank  →  Top 5  →  LLM writes the answer
#                                         ↓
#                                  the judge gets these same 5 as CONTEXT

_judge = EuriChatModel()

# Asks the LLM judge to mark one answer: sends the following, and
# returns the judge's counts as a Python dictionary.
def _ask_judge(query: str, chunks: list[dict], answer: str, key_facts: list[str]) -> dict:
    # sends everything to the judge in one call, and returns its reply in the python dictionary.

    context = "\n\n".join(
        f"[{i}] ({c['source']} p.{c['page']})\n{c['text']}" for i, c in enumerate(chunks, start=1)
    )
    # the chunks numbered [1] to [5], so the judge can see which ones were useful
    # e.g. "[1] (payment-services-electronic-money-approach.pdf p.6)\nThe EMRs govern..."

    facts_text = "\n".join(f"{i}. {fact}" for i, fact in enumerate(key_facts, start=1))
    # the key facts numbered 1, 2, 3 ..., so the judge can say which ones the answer covers
    # e.g. "1. Victoria Cleland\n2. Of the Bank of England"

    prompt = _JUDGE_PROMPT.format(query=query, context=context, answer=answer, key_facts=facts_text)
    reply = _judge(_JUDGE_SYSTEM_PROMPT, prompt)
    # one call to the judge; the reply should be JSON text.

    json_text = reply[reply.find("{"): reply.rfind("}") + 1]
    # cuts reply down to just the JSON, and throws away anything around it.

    return json.loads(json_text)  # turns the JSON text into a dictionary e.g. {"claims_total": 5, "claims_supported": 5, ...}


def scores_from_judgement(judgement: dict, n_chunks: int, n_facts: int) -> dict:
    # turns the judge's counts into scores, so they can be averaged across questions.
    # 
    # EXAMPLE judgement:
    #     claims_total 4, claims_supported 3, answer_relevance 1.0,
    #     useful_chunks [1, 3, 5], key_facts_total 6, key_facts_covered 2
    # gives:
    #     faithfulness 3/4 = 0.75, hallucination 1, answer_relevance 1.0,
    #     context_relevance 3/5 = 0.60, answer_correctness 2/6 = 0.33

    claims_total = int(judgement["claims_total"]) 
    claims_supported = min(int(judgement["claims_supported"]), claims_total)
    # min(...) guards against the judge saying more claims are supported than exist
    # the judge can miscount, e.g. "6 supported out of 5 claims"

    useful = {int(n) for n in judgement["useful_chunks"] if 1 <= int(n) <= n_chunks}
    # keeps only real chunk numbers (1 to 5), and each number once

    covered = {int(n) for n in judgement["facts_covered"] if 1 <= int(n) <= n_facts}
    # the key facts the answer contains, keeping only real fact numbers and each number once
    # e.g. [2, 5] -> {2, 5}; a repeated or impossible number like 9 is ignored, so the score can't go above 1.0

    return {
        "faithfulness": claims_supported / claims_total if claims_total > 0 else 1.0,
        # an answer like "the documents don't answer this" has 0 claims, and 0 ÷ 0 would crash, so 1.0

        "hallucination": 1.0 if claims_supported < claims_total else 0.0,
        # 1 if at least one claim isn't backed by the chunks; this becomes hallucination rate after averaging.

        "answer_relevance": float(judgement["answer_relevance"]),
        # 1.0, 0.5 or 0.0, as decided by the judge

        "context_relevance": len(useful) / n_chunks,
        # useful_chunks ÷ chunks given to the LLM, e.g. 3 ÷ 5 = 0.6

        "answer_correctness": len(covered) / n_facts if n_facts > 0 else 0.0,
        # key facts covered ÷ key facts in the fixed list, e.g. 2 ÷ 6 = 0.33

    }

def evaluate_generation(query: str, chunks: list[dict], answer: str, key_facts: list[str]) -> tuple[dict, dict]:
    # the function run_evaluation.py calls: one judge call, then the five scores
    # returns (scores, judgements): the scores for the report, and the judge's full reply.
    # which shows which claims were unsupported and which facts were missing
    judgement = _ask_judge(query, chunks, answer, key_facts)
    return scores_from_judgement(judgement, len(chunks), len(key_facts)), judgement


if __name__ == "__main__":
    # python -m eval.generation_metrics cohere 5    (reranker name, question number 1-33)

    import sys
    from rag.retriever import retrieve
    from rag.rerankers import CrossEncoderReRanker, LLMReRanker, CohereReRanker, JinaReRanker, TOP_N
    from rag.generate import generate_answer
    from eval.eval_dataset import EVAL_DATASET

    # ---------- check 1: the worked example from the comments, no API calls ----------
    example = {"claims_total": 4, "claims_supported": 3, "answer_relevance": 1.0,
               "useful_chunks": [1, 3, 5], "facts_covered": [2, 5]}
    print("Worked Example:")
    for name, value in scores_from_judgement(example, 5, 6).items():
        print(f"   {name:19}: {value:.3f}")
    # expected: faithfulness, hallucination, answer_relevance,
    #           context_relevance, answer_correctness

    # ---------- check 2: one real question through the whole pipeline, then the judge ----------
    reranker_name = sys.argv[1] if len(sys.argv) > 1 else "cohere"
    question_number = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rerankers = {"cross": CrossEncoderReRanker, "llm": LLMReRanker, "cohere": CohereReRanker, "jina": JinaReRanker}
    reranker = rerankers[reranker_name]()

    case = EVAL_DATASET[question_number - 1]
    top_chunks = reranker(case["query"], retrieve(case["query"]))[:TOP_N]
    # 1: Run retrieve(case["query"]) - Top 20 from Qdrant
    # 2: reranker(case["query"]...) - Rerank all 20
    # 3: [:TOP_N] - Keep the Top 5

    answer = generate_answer(case["query"], top_chunks)
    # answer to be judged

    scores, judgement = evaluate_generation(case["query"], top_chunks, answer, case["key_facts"])

    print(f"\nQuestion {question_number}: {case['query']}")
    print(f"Reranker: {reranker_name}   Top {TOP_N} pages: {[c['page'] for c in top_chunks]}")
    print(f"\nAnswer:\n{answer}\n")
    
    covered = {int(n) for n in judgement["facts_covered"]}
    # the fact numbers the judge says are covered, as real numbers (the judge sometimes sends "2" as text)

    missing = [fact for i, fact in enumerate(case["key_facts"], start=1) if i not in covered]
    # the facts from the fixed list that the answer did NOT cover

    print(f"Judge: {judgement['claims_supported']}/{judgement['claims_total']} claims supported, "
          f"useful chunks {judgement['useful_chunks']}, "
          f"{len(covered)}/{len(case['key_facts'])} key facts covered")
    print(f"Unsupported claims: {judgement.get('unsupported_claims', [])}")
    print(f"Missing facts: {missing}\n")
    for name, value in scores.items():
        print(f"  {name:19}: {value:.3f}")


# other questions tested:
# python -m eval.generation_metrics cross 5
# python -m eval.generation_metrics llm 5
# python -m eval.generation_metrics cohere 5
# python -m eval.generation_metrics jina 5


    


    