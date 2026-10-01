# rag/generate.py
# the LLM writes the answer using ONLY the Top 5 reranked chunks.
# Running this file runs the WHOLE pipeline for one question:
# question -> Top 20 (retriever.py) -> rerank (rerankers.py) -> Top 5 -> answer (here)
# Run with:  python -m rag.generate cohere 6      (reranker name, question number 1-10)

import sys    # reads the words typed after the command, e.g. "cohere" and "6"
from rag.chat_model import EuriChatModel
from rag.retriever import retrieve    # Top 20 chunks from Qdrant
from rag.rerankers import CrossEncoderReRanker, LLMReRanker, CohereReRanker, JinaReRanker, TOP_N 
# the four rerankers, and TOP_N = 5

from eval.test_queries import TEST_QUERIES   # the test questions, so can be picked one by number

_SYSTEM_PROMPT = "You answer questions about payment regulations and standards using only the context you are given."
# tells the LLM its role: answer from the given chunks, not from its own general knowledge

_PROMPT = """Answer the question using ONLY the context below.
After each fact, cite where it came from, like this: [PCIDSS_QRGv3.pdf p.14]
If the context does not contain the answer, say: "The provided documents don't answer this."

Question: {query}

Context:
{context}"""
# the instruction; {query} and {context} are filled in for every question
# the last rule matters: if the right chunk didn't reach the Top 5, the LLM should say so, not guess

_chat_model = EuriChatModel()    # creates the chat model client once

def generate_answer(query: str, top_chunks: list[dict]) -> str:
    # takes the question and the Top 5 chunks, returns the LLM's answer as text

    context = "\n\n".join(f"[{c['source']} p.{c['page']}]\n{c['text']}" for c in top_chunks)
    # joins the 5 chunks into one block, each labelled with where it came from:
    #     [PCIDSS_QRGv3.pdf p.14]
    #     14 Protect Cardholder Data Cardholder data refers to...
    #
    #     [PCIDSS_QRGv3.pdf p.15]
    #     ...
    #
    # the labels let the LLM cite its sources in the answer

    prompt = _PROMPT.format(query=query, context=context)   # fills the question and the 5 labelled chunks into the instruction
    return _chat_model(_SYSTEM_PROMPT, prompt)   # ONE call to the LLM; returns the answer text

if __name__ == "__main__":     # python -m rag.generate <reranker> <question>

    reranker_name = sys.argv[1] if len(sys.argv) > 1 else "cohere"
    # which reranker to use; if you don't type one, it uses Cohere

    question_number = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    # which test question, 1 to 10, matching the "q" column in compare.py; default is 8

    rerankers = {"cross": CrossEncoderReRanker, "llm": LLMReRanker, "cohere": CohereReRanker, "jina": JinaReRanker}
    reranker = rerankers[reranker_name]()
    # creates ONLY the chosen reranker, so the cross-encoder model isn't loaded unless you ask for it

    case = TEST_QUERIES[question_number - 1]
    # question numbers start at 1, but list positions start at 0, so question 6 is TEST_QUERIES[5]

    chunks = retrieve(case["query"])   # Stage 1: the Top 20 from vector search

    top_chunks = reranker(case["query"], chunks)[:TOP_N]
    # Part 1: reranker(case["query"], chunks) reranks the 20 chunks, using the question to judge them. 
    # It returns all 20, in the new order.
    # Part 2: [:TOP_N] keeps only the first 5. [:5] means "from the start, up to position 5."
    # So after this line, top_chunks holds the 5 best chunks.
    # 20 chunks  →  rerank  →  keep Top 5  →  question + Top 5 go to LLM  →  answer
    # └────────── top_chunks = ... ─────────┘  └──── generate_answer(...) ────┘

    print(f"Question {question_number}: {case['query']}")
    print(f"Answer is on: {case['relevant_sources']}")
    print(f"Reranker: {reranker.name}\n")

    print(f"Top {TOP_N} chunks sent to the LLM:")
    for c in top_chunks:
        marker = "  <- answer page" if (c["source"], c["page"]) in case["relevant_sources"] else ""
        print(f"  {c['rerank_rank']}. {c['source']} p.{c['page']}  (was {c['vector_rank']} in vector search){marker}")
    # shows which 5 chunks the LLM receives, where each one was before reranking, and flags the answer page

    print("\nAnswer:\n")
    print(generate_answer(case["query"], top_chunks))   # the LLM writes the answer from those 5 chunks only

    

