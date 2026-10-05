# RAG Evaluation Report

43 results, configurations: cohere. Pipeline: vector search Top 20 -> rerank -> Top 5 -> LLM answer.

## Retrieval metrics (averages)

| Metric | cohere | What it measures |
|---|---|---|
| **hit_rate@5** | 1.000 | Did at least one relevant page reach the Top 5? |
| **precision@5** | 0.337 | How much of the Top 5 was relevant? |
| **recall@5** | 0.935 | How many of all relevant pages reached the Top 5? |
| **mrr** | 0.947 | How high was the first relevant page? (1st = 1.0, 2nd = 0.5 ...) |
| **map** | 0.867 | How high were ALL the relevant pages? |
| **ndcg@5** | 0.913 | Were the best pages (grade 2) at the very top? |

## Generation metrics (averages)

| Metric | cohere | What it measures |
|---|---|---|
| **faithfulness** | 1.000 | Share of the answer's claims backed by the Top 5 chunks |
| **hallucination** | 0.000 | Share of answers with at least one unsupported claim (lower is better) |
| **answer_relevance** | 1.000 | Did the answer address the question? (1.0 / 0.5 / 0.0) |
| **context_relevance** | 0.521 | Share of the Top 5 chunks that actually helped answer the question |
| **answer_correctness** | 0.974 | Share of the key facts the answer contained |

## Results by question type (cohere)

| Type | Questions | Recall@5 | NDCG@5 | Faithful | Halluc. rate | Correct |
|---|---|---|---|---|---|---|
| direct | 27 | 0.98 | 0.97 | 1.00 | 0.00 | 0.99 |
| multi-page | 8 | 0.83 | 0.77 | 1.00 | 0.00 | 0.94 |
| vague | 3 | 1.00 | 0.99 | 1.00 | 0.00 | 1.00 |
| cross-document | 3 | 0.78 | 0.72 | 1.00 | 0.00 | 0.89 |
| unanswerable | 2 | - | - | 1.00 | 0.00 | 1.00 |

## Every question (cohere)

| Q | Type | Question | Recall@5 | MRR | NDCG@5 | Faithful | Correct |
|---|---|---|---|---|---|---|---|
| 1 | direct | How many 'building blocks' did the CPMI identify to enh | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2 | direct | How many focus areas are the cross-border payments buil | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 3 | direct | Which payment methods does Stripe recommend for SaaS an | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 4 | direct | How quickly is a payment confirmed when a customer pays | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 5 | multi-page | What do the Electronic Money Regulations (EMRs) govern? | 0.67 | 1.00 | 0.85 | 1.00 | 1.00 |
| 6 | multi-page | What is the temporary permissions regime (TPR) for EEA  | 1.00 | 1.00 | 0.98 | 1.00 | 0.80 |
| 7 | direct | What are the 12 requirements of the PCI Data Security S | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 8 | multi-page | What does PCI DSS Requirement 3 say about protecting ca | 1.00 | 1.00 | 0.95 | 1.00 | 1.00 |
| 9 | direct | How does this report define a financial market infrastr | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 10 | direct | Besides systemic risk, what other types of risk do fina | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 11 | direct | How many underlying frictions in cross-border payments  | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 12 | multi-page | What does focus area E of the cross-border payments roa | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 13 | direct | Who chairs the CPMI Cross-border Payments Task Force? | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 14 | direct | What does building block 14 propose for cross-border pa | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 15 | direct | Which payment methods does Stripe recommend for e-comme | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 16 | direct | What share of online payments globally do credit and de | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 17 | direct | What market share does Bacs Direct Debit have in the Un | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 18 | direct | How popular is iDEAL for online payments in the Netherl | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 19 | direct | According to a Stripe study, what percentage of online  | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 20 | direct | How long do payment service providers have to send a fi | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 21 | multi-page | What conditions must a business meet to register as a s | 1.00 | 1.00 | 0.81 | 1.00 | 1.00 |
| 22 | direct | What are the two methods an institution can use to safe | 1.00 | 1.00 | 0.93 | 1.00 | 0.67 |
| 23 | direct | What is strong customer authentication based on? | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 24 | direct | How often must the safeguarding return be submitted, an | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 25 | direct | How long must audit trail history be retained under PCI | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 26 | direct | How often does PCI DSS require penetration testing? | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 27 | direct | What does PCI DSS require for remote network access fro | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 28 | direct | How can network segmentation reduce PCI DSS scope? | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 29 | direct | What is the PCI DSS Self-Assessment Questionnaire (SAQ) | 1.00 | 1.00 | 0.93 | 1.00 | 1.00 |
| 30 | direct | How quickly should an FMI be able to resume operations  | 0.67 | 1.00 | 0.80 | 1.00 | 1.00 |
| 31 | multi-page | What default scenario should a systemically important C | 0.33 | 0.33 | 0.12 | 1.00 | 0.75 |
| 32 | direct | By when should an FMI provide final settlement? | 0.67 | 1.00 | 0.83 | 1.00 | 1.00 |
| 33 | direct | What is a central counterparty (CCP)? | 1.00 | 0.50 | 0.66 | 1.00 | 1.00 |
| 34 | vague | How long does a company have to get back to an unhappy  | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 35 | vague | If hackers stole our customer database, how do we make  | 1.00 | 1.00 | 0.96 | 1.00 | 1.00 |
| 36 | vague | How do most people in China pay online? | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 37 | multi-page | How must a payment institution safeguard customers' mon | 0.67 | 0.50 | 0.53 | 1.00 | 1.00 |
| 38 | multi-page | What does PCI DSS Requirement 8 require for identifying | 1.00 | 1.00 | 0.92 | 1.00 | 1.00 |
| 39 | cross-document | What share of online payments are made by card, and how | 1.00 | 0.50 | 0.69 | 1.00 | 1.00 |
| 40 | cross-document | What do PCI DSS and the FCA each require for authentica | 0.33 | 1.00 | 0.56 | 1.00 | 0.67 |
| 41 | cross-document | What do the FCA guidance and the PFMI expect when opera | 1.00 | 1.00 | 0.91 | 1.00 | 1.00 |
| 42 | unanswerable | How much does Stripe charge per transaction to process  | - | - | - | 1.00 | 1.00 |
| 43 | unanswerable | What is the maximum fine a merchant can receive for fai | - | - | - | 1.00 | 1.00 |

## Notes

- The LLM judge is the same model that writes the answers, so generation scores may be lenient.
- Precision@5 cannot reach 1.0 for questions with fewer than 5 relevant pages.
- The average of `hallucination` is the hallucination rate (share of answers with any unsupported claim).
