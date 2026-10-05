# eval/report.py
# Step 5 of the evaluation: turns results/results.json into a readable report.
# it only reads the saved results and does arithmetic
#
#     reads   results/results.json            (written by run_evaluation.py)
#     writes  reports/evaluation_report.md    (the final evaluation report)

import json
from pathlib import Path
from collections import defaultdict

from eval.eval_dataset import EVAL_DATASET

RESULTS_FILE = Path("results/results.json")
REPORT_FILE = Path("reports/evaluation_report.md")

RETRIEVAL_METRICS = {
    "hit_rate@5":  "Did at least one relevant page reach the Top 5?",
    "precision@5": "How much of the Top 5 was relevant?",
    "recall@5":    "How many of all relevant pages reached the Top 5?",
    "mrr":         "How high was the first relevant page? (1st = 1.0, 2nd = 0.5 ...)",
    "map":         "How high were ALL the relevant pages?",
    "ndcg@5":      "Were the best pages (grade 2) at the very top?",
}

GENERATION_METRICS = {
    "faithfulness":       "Share of the answer's claims backed by the Top 5 chunks",
    "hallucination":      "Share of answers with at least one unsupported claim (lower is better)",
    "answer_relevance":   "Did the answer address the question? (1.0 / 0.5 / 0.0)",
    "context_relevance":  "Share of the Top 5 chunks that actually helped answer the question",
    "answer_correctness": "Share of the key facts the answer contained",
}

SHORT_NAMES = {
    "enhancing-cross-border-payments-building-blocks-global-roadmap.pdf": "Cross-border roadmap (CPMI)",
    "Payment-methods-guide.pdf": "Payment methods guide (Stripe)",
    "payment-services-electronic-money-approach.pdf": "Payment services & e-money (FCA)",
    "PCIDSS_QRGv3.pdf": "PCI DSS quick reference",
    "principles-financial-market-infrastructures.pdf": "Principles for FMIs (CPMI-IOSCO)",
}
# readable names for the five PDFs, used in the per-document table

def average(rows: list[dict], section: str, metric: str) -> float | None:
    # the average of one metric over a list of results, skipping results without that section
    # (unanswerable questions have no retrieval scores); None if there's nothing to average
    values = [row[section][metric] for row in rows if row[section] is not None]
    return sum(values) / len(values) if values else None


def show(value: float | None, decimals: int = 2) -> str:
    # formats a score for the report: 0.949 -> "0.95", or "-" when there's no score
    return "-" if value is None else f"{value:.{decimals}f}"

def document_of(question_numbers: int) -> str:
    # which pdf the question is about
    source = EVAL_DATASET[question_numbers - 1]["relevant_pages"][0][0]
    return SHORT_NAMES.get(source, source)


def metrics_table(rows_by_config: dict, section: str, metrics: dict) -> list[str]:
    # a Markdown table: one row per metric, one column per configuration, plus the metric's meaning
    configs = list(rows_by_config)
    lines = ["| Metric | " + " | ".join(configs) + " | What it measures |",
             "|---|" + "---|" * len(configs) + "---|"]
    for metric, meaning in metrics.items():
        values = " | ".join(show(average(rows_by_config[c], section, metric), 3) for c in configs)
        lines.append(f"| **{metric}** | {values} | {meaning} |")
    return lines


if __name__ == "__main__":
    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    # reads results.json into a python list: one entry per question per configuration

    rows_by_config = defaultdict(list)   # an empty dictionary that will hold one list of results per configuration

    for row in results:
        rows_by_config[row["config"]].append(row)  # puts each result into its configuration list e.g. {"cohere": [33 results]}

    retrieval_table = metrics_table(rows_by_config, "retrieval", RETRIEVAL_METRICS)
    # builds the table of Hit Rate, Precision, Recall, MRR, MAP, NDCG

    generation_table = metrics_table(rows_by_config, "generation", GENERATION_METRICS)
    # Builds the table of the  faithfulness, hallucination, relevance, correctness

    lines = ["# RAG Evaluation Report", "",
             
             f"{len(results)} results, configurations: {', '.join(rows_by_config)}. "
             "Pipeline: vector search Top 20 -> rerank -> Top 5 -> LLM answer.", "",
             # one summary line

             "## Retrieval metrics (averages)", "", *retrieval_table, "",
             # a heading, then the retrieval table; * puts the table's lines in one by one

             "## Generation metrics (averages)", "", *generation_table, "",
             # a heading, then the generation table
             
    ]

    for config, rows in rows_by_config.items():
        # one set of tables per configuration; with Cohere only, this runs once

        lines += [f"## Results by question type ({config})", "",
                  "| Type | Questions | Recall@5 | NDCG@5 | Faithful | Halluc. rate | Correct |", "|---|---|---|---|---|---|---|"]
        for question_type in ["direct", "multi-page", "vague", "cross-document", "unanswerable"]:
            type_rows = [r for r in rows if EVAL_DATASET[r["question"] - 1]["type"] == question_type]
            if type_rows:
                lines.append(f"| {question_type} | {len(type_rows)} "
                             f"| {show(average(type_rows, 'retrieval', 'recall@5'))} "
                             f"| {show(average(type_rows, 'retrieval', 'ndcg@5'))} "
                             f"| {show(average(type_rows, 'generation', 'faithfulness'))} "
                             f"| {show(average(type_rows, 'generation', 'hallucination'))} "
                             f"| {show(average(type_rows, 'generation', 'answer_correctness'))} |")
        lines.append("")
        # the averages for each question type, to show where the system struggles

        lines += [f"## Every question ({config})", "",
                  "| Q | Type | Question | Recall@5 | MRR | NDCG@5 | Faithful | Correct |", "|---|---|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: r["question"]):
            ret, gen = r["retrieval"] or {}, r["generation"]
            # "or {}" gives an empty dictionary for unanswerable questions, so .get() below returns None -> "-"
            lines.append(f"| {r['question']} | {EVAL_DATASET[r['question'] - 1]['type']} | {r['query'][:55]} "
                         f"| {show(ret.get('recall@5'))} | {show(ret.get('mrr'))} | {show(ret.get('ndcg@5'))} "
                         f"| {show(gen['faithfulness'])} | {show(gen['answer_correctness'])} |")
        lines.append("")
        # one row per question, so every average above can be traced back

    lines += ["## Notes", "",
              "- The LLM judge is the same model that writes the answers, so generation scores may be lenient.",
              "- Precision@5 cannot reach 1.0 for questions with fewer than 5 relevant pages.",
              "- The average of `hallucination` is the hallucination rate (share of answers with any unsupported claim)."]
    # three honest caveats at the end of the report

    REPORT_FILE.parent.mkdir(exist_ok=True)   # creates the reports/ folder if it doesn't exist yet

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # joins all the lines with line breaks and saves them as reports/evaluation_report.md

    print("\n".join(retrieval_table + [""] + generation_table))
    # shows the two tables of averages in the terminal too

    print(f"\nFull report written to {REPORT_FILE}")


             

        



