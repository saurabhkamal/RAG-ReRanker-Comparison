# eval/compare.py
# Step 4: runs all 10 test questions through vector search (BEFORE) and the four rerankers (AFTER),
# and show where the answer chunk landed each time.


import time                 # used to measure how many seconds each reranker takes
from rag.retriever import retrieve    # gets the top 20 chunks for a question from Qdrant
from rag.rerankers import CrossEncoderReRanker, LLMReRanker, CohereReRanker, JinaReRanker, TOP_N
# the four rerankers, and TOP_N = 5 (how many chunks go to the LLM)
from eval.test_queries import TEST_QUERIES   # the 10 test questions, each with the PDF page that holds its answer


def answer_position(chunks, answer_pages):
     # returns where the first answer chunk is in the list: 1, 2, 3 ... or None if it isn't there
    #
    # EXAMPLE INPUT:
    #     chunks = [
    #         {"source": "PCIDSS_QRGv3.pdf", "page": 5,  "text": "..."},    # 1st in the list
    #         {"source": "PCIDSS_QRGv3.pdf", "page": 9,  "text": "..."},    # 2nd
    #         {"source": "PCIDSS_QRGv3.pdf", "page": 22, "text": "..."},    # 3rd
    #     ]
    #     answer_pages = [("PCIDSS_QRGv3.pdf", 22)]
    #
    # EXAMPLE OUTPUT:  3   (the answer chunk is 3rd in the list)

    for position, chunk in enumerate(chunks, start=1):
        #     round 1:  position = 1,  chunk = the page 5 chunk
        #     round 2:  position = 2,  chunk = the page 9 chunk
        #     round 3:  position = 3,  chunk = the page 22 chunk

        if (chunk["source"], chunk["page"]) in answer_pages:
            # checks: does this chunk come from the answer's PDF AND page?
            #
            #     round 1:  ("PCIDSS_QRGv3.pdf", 5)   in [("PCIDSS_QRGv3.pdf", 22)]?  → No, keep going
            #     round 2:  ("PCIDSS_QRGv3.pdf", 9)   in [("PCIDSS_QRGv3.pdf", 22)]?  → No, keep going
            #     round 3:  ("PCIDSS_QRGv3.pdf", 22)  in [("PCIDSS_QRGv3.pdf", 22)]?  → YES

            return position
            # returns 3, and the loop stops

    return None   # found no answer chunk
    # EXAMPLE: if answer_pages were [("PCIDSS_QRGv3.pdf", 50)] instead,
    #     page 5 → No,  page 9 → No,  page 22 → No,  list finished  → returns None


def in_top_5(position):
    # True if the answer reached the Top 5, the chunks the LLM actually gets
    return position is not None and position <= TOP_N

def show(position):
    # turns a position into what we print:  3 -> "3",  8 -> "8*" (outside Top 5),  None -> "-"

    if position is None:
        return "-"
        # the answer wasn't in the Top 20 at all

    if position > TOP_N:
        return f"{position}*"
        # found, but below 5th place, so the LLM won't see it; the * flags this

    return str(position)  # found in the Top 5; just print the number

# ---------- set up the four rerankers ----------

rerankers = {
    "cross": CrossEncoderReRanker(),
    # reranker 1: the small local model; loads its model here, once

    "llm": LLMReRanker(),
    # reranker 2: the general LLM that puts all 20 chunks in order

    "cohere": CohereReRanker(),
    # reranker 3: Cohere's reranking API

    "jina":   JinaReRanker(),
    # reranker 4: Jina's reranking API
}

total_time = {"cross": 0.0, "llm": 0.0, "cohere": 0.0, "jina": 0.0}
# a running total of seconds for each reranker, starting at 0

results = [] 
# an empty list; it will hold one row per question, e.g.
# {"question": "What does...", "vector": 1, "cross": 8, "llm": 1, "cohere": 1, "jina": 1}

# ---------- run every question ----------

for number, case in enumerate(TEST_QUERIES, start=1):
    # goes through the 10 test questions one by one
    #     round 1:  number = 1,  case = test question 1
    #     round 2:  number = 2,  case = test question 2
    #     ...
    #     round 8:  number = 8,  case = test question 8   
    #     ...
    #     round 10: number = 10, case = test question 10
    # EXAMPLE, round 8:
    #     case = {
    #         "query": "What does PCI DSS Requirement 3 say about protecting cardholder data?",
    #         "relevant_sources": [("PCIDSS_QRGv3.pdf", 14)],
    #     }

    print(f"question {number}/{len(TEST_QUERIES)} ...")  # progress line
    answer_pages = case["relevant_sources"]

    chunks = retrieve(case["query"])  # vector search once; the SAME 20 chunks go to every reranker, so the comparison is fair
    
    row = {"question": case["query"], "vector": answer_position(chunks, answer_pages)}
    # starts this question's row with the question text and the BEFORE position

    for name, reranker in rerankers.items():
        # goes through the four rerankers one by one
        #
        #     round 1:  name = "cross",   reranker = the CrossEncoderReRanker
        #     round 2:  name = "llm",     reranker = the LLMReRanker
        #     round 3:  name = "cohere",  reranker = the CohereReRanker
        #     round 4:  name = "jina",    reranker = the JinaReRanker

        start = time.perf_counter()     # the time just before reranking,

        reranked = reranker(case["query"], chunks)

        total_time[name] += time.perf_counter() - start
        #  works out how long it took, and adds it to this reranker's running total

        row[name] = answer_position(reranked, answer_pages) # AFTER: where the answer is once this reranker has reordered the chunks

    results.append(row)



# ---------- Table 1: before vs after, per question ----------
print("\nPosition of the first answer chunk (lower is better)")

print("* = outside the Top 5, so the LLM never sees it     - = not in the Top 20 at all\n")

print(" q   vector   cross     llm  cohere    jina   question")
# the column headings

for number, row in enumerate(results, start=1):
    # goes through the 10 rows; number counts 1, 2, 3 ... for the "q" column

    print(
        f"{number:2}"
        # question number, 2 characters wide

        f"{show(row['vector']):>9}"
        # BEFORE: vector search position, right-aligned in 9 characters

        f"{show(row['cross']):>8}"
        f"{show(row['llm']):>8}"
        f"{show(row['cohere']):>8}"
        f"{show(row['jina']):>8}"
        # AFTER: each reranker's position, right-aligned in 8 characters so the columns line up

        f"   {row['question'][:45]}"
        # the first 45 characters of the question, so you know which row is which
    )
    # these pieces sit next to each other, so Python joins them into one line


# ---------- Table 2: Hit@5 and average time ----------

print("\nHit@5 = in how many questions the answer reached the Top 5\n")

print("method    Hit@5   avg time")
# the column headings

for name in ["vector", "cross", "llm", "cohere", "jina"]:
    # one line of the summary for each method

    hits = sum(in_top_5(row[name]) for row in results)
    # checks every question for this method: True (=1) if the answer reached the Top 5, False (=0) if not
    # sum adds them up, so hits = how many of the 10 questions were hits, e.g. 9

    if name == "vector":
        avg_time = "-"
        # vector search isn't a reranker, so there's no reranking time to show

    else:
        avg_time = f"{total_time[name] / len(results):.2f}s"
        # total seconds ÷ 10 questions = average per question, shown with 2 decimals, e.g. "1.24s"

    print(f"{name:8}{hits:>4}/{len(results)}{avg_time:>11}")
    # one summary line, e.g. "jina        9/10      1.24s"