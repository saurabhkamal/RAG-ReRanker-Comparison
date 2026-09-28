# eval/test_queries.py
# 10 labelled test queries, each paired with source PDF + page that answers it.
# eval/compare.py runs each query through all four rerankers and scores them against this ground truth.
# Copied from ReRankEval; page numbers were verified against the same Qdrant collection this repo reads.

TEST_QUERIES = [
    {
        "query": "How many 'building blocks' did the CPMI identify to enhance cross-border payments?",
        "relevant_sources": [
            ("enhancing-cross-border-payments-building-blocks-global-roadmap.pdf", 3),
        ],
    },
    {
        "query": "How many focus areas are the cross-border payments building blocks arranged into?",
        "relevant_sources": [
            ("enhancing-cross-border-payments-building-blocks-global-roadmap.pdf", 5),
        ],
    },
    {
        "query": "Which payment methods does Stripe recommend for SaaS and subscription businesses?",
        "relevant_sources": [
            ("Payment-methods-guide.pdf", 6),
        ],
    },
    {
        "query": "How quickly is a payment confirmed when a customer pays with Alipay?",
        "relevant_sources": [
            ("Payment-methods-guide.pdf", 12),
        ],
    },
    {
        "query": "What do the Electronic Money Regulations (EMRs) govern?",
        "relevant_sources": [
            ("payment-services-electronic-money-approach.pdf", 6),
        ],
    },
    {
        "query": "What is the temporary permissions regime (TPR) for EEA payment firms?",
        "relevant_sources": [
            ("payment-services-electronic-money-approach.pdf", 7),
        ],
    },
    {
        "query": "What are the 12 requirements of the PCI Data Security Standard?",
        "relevant_sources": [
            ("PCIDSS_QRGv3.pdf", 9),
        ],
    },
    {
        "query": "What does PCI DSS Requirement 3 say about protecting cardholder data?",
        "relevant_sources": [
            ("PCIDSS_QRGv3.pdf", 14),
        ],
    },
    {
        "query": "How does this report define a financial market infrastructure (FMI)?",
        "relevant_sources": [
            ("principles-financial-market-infrastructures.pdf", 13),
        ],
    },
    {
        "query": "Besides systemic risk, what other types of risk do financial market infrastructures face?",
        "relevant_sources": [
            ("principles-financial-market-infrastructures.pdf", 24),
        ],
    },
]