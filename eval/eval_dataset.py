# eval/eval_dataset.py
# The evaluation dataset: 33 questions, each with an expected answer and the pages that answer it.
# Every page number was checked against the PDFs with pdfplumber, the same tool and the same

# relevant_pages is a list of (pdf, page, grade):
#     grade 2 = the page contains the answer
#     grade 1 = the page is partly relevant (mentions it, or gives only part of the answer)
# The grades are what NDCG uses; the other retrieval metrics treat any listed page as relevant.

CBP = "enhancing-cross-border-payments-building-blocks-global-roadmap.pdf"   # CPMI cross-border roadmap
STRIPE = "Payment-methods-guide.pdf"                                         # Stripe guide to payment methods
FCA = "payment-services-electronic-money-approach.pdf"                       # FCA approach document
PCI = "PCIDSS_QRGv3.pdf"                                                     # PCI DSS quick reference guide
PFMI = "principles-financial-market-infrastructures.pdf"                     # CPMI-IOSCO principles for FMIs
# short names for the five PDFs, so each question below stays readable
 
EVAL_DATASET = [
    # ---------- questions 1-10: the original test questions ----------
    {
        "query": "How many 'building blocks' did the CPMI identify to enhance cross-border payments?",
        "expected_answer": "The CPMI identified 19 building blocks to enhance cross-border payments.",
        "relevant_pages": [(CBP, 3, 2), (CBP, 5, 1)],
    },
    {
        "query": "How many focus areas are the cross-border payments building blocks arranged into?",
        "expected_answer": "Five focus areas (A to E). Focus areas A to D aim to enhance the existing payments "
                           "ecosystem, while focus area E is more exploratory and covers emerging payment "
                           "infrastructures and arrangements.",
        "relevant_pages": [(CBP, 5, 2)],
    },
    {
        "query": "Which payment methods does Stripe recommend for SaaS and subscription businesses?",
        "expected_answer": "Cards, digital wallets and bank debits, because their payment details can be stored "
                           "and reused for recurring payments.",
        "relevant_pages": [(STRIPE, 6, 2), (STRIPE, 7, 1)],
    },
    {
        "query": "How quickly is a payment confirmed when a customer pays with Alipay?",
        "expected_answer": "Alipay payments are confirmed immediately. Because payments are authenticated with "
                           "the customer's login credentials, dispute rates are very low.",
        "relevant_pages": [(STRIPE, 12, 2)],
    },
    {
        "query": "What do the Electronic Money Regulations (EMRs) govern?",
        "expected_answer": "The EMRs govern the authorisation and associated requirements for electronic money "
                           "institutions (EMIs) and set the conduct of business rules for issuing e-money. They "
                           "also cover who must be authorised or registered, capital and safeguarding "
                           "requirements, and the issuing and redeeming of e-money. They apply, with certain "
                           "exceptions, to everyone who issues e-money in the UK.",
        "relevant_pages": [(FCA, 6, 2), (FCA, 7, 1), (FCA, 22, 1)],
    },
    {
        "query": "What is the temporary permissions regime (TPR) for EEA payment firms?",
        "expected_answer": "The TPR is a temporary scheme set up under the Exit SI after Brexit. It allowed EEA "
                           "payment and e-money firms that passported into the UK before the end of the "
                           "transition period (31 December 2020) to keep operating in the UK for a limited "
                           "period, within the scope of their previous passport permissions, while seeking full "
                           "UK authorisation or registration.",
        "relevant_pages": [(FCA, 7, 2), (FCA, 76, 2), (FCA, 77, 1)],
    },
    {
        "query": "What are the 12 requirements of the PCI Data Security Standard?",
        "expected_answer": "1. Install and maintain a firewall configuration. 2. Do not use vendor-supplied "
                           "defaults for passwords and security parameters. 3. Protect stored cardholder data. "
                           "4. Encrypt transmission of cardholder data across open, public networks. 5. Protect "
                           "all systems against malware and keep anti-virus updated. 6. Develop and maintain "
                           "secure systems and applications. 7. Restrict access to cardholder data by business "
                           "need to know. 8. Identify and authenticate access to system components. 9. Restrict "
                           "physical access to cardholder data. 10. Track and monitor all access to network "
                           "resources and cardholder data. 11. Regularly test security systems and processes. "
                           "12. Maintain a policy that addresses information security for all personnel.",
        "relevant_pages": [(PCI, 9, 2), (PCI, 40, 2)],
    },
    {
        "query": "What does PCI DSS Requirement 3 say about protecting cardholder data?",
        "expected_answer": "Requirement 3 is to protect stored cardholder data. Cardholder data should not be "
                           "stored unless the business needs it, and sensitive authentication data must never be "
                           "stored after authorisation. The PAN must be masked when displayed (first six and last "
                           "four digits at most) and rendered unreadable wherever it is stored, for example by "
                           "encryption. Encryption keys must be protected and managed with documented "
                           "procedures.",
        "relevant_pages": [(PCI, 14, 2), (PCI, 15, 2), (PCI, 9, 1)],
    },
    {
        "query": "How does this report define a financial market infrastructure (FMI)?",
        "expected_answer": "An FMI is a multilateral system among participating institutions, including the "
                           "operator of the system, used for clearing, settling or recording payments, "
                           "securities, derivatives or other financial transactions.",
        "relevant_pages": [(PFMI, 13, 2)],
    },
    {
        "query": "Besides systemic risk, what other types of risk do financial market infrastructures face?",
        "expected_answer": "Legal, credit, liquidity, general business, custody, investment and operational "
                           "risks.",
        "relevant_pages": [(PFMI, 24, 2)],
    },
 
    # ---------- questions 11-14: cross-border payments roadmap ----------
    {
        "query": "How many underlying frictions in cross-border payments did the Stage 1 assessment identify?",
        "expected_answer": "Seven underlying frictions, which together contribute to the challenges of cost, "
                           "speed, access and transparency in cross-border payments.",
        "relevant_pages": [(CBP, 3, 2), (CBP, 4, 1), (CBP, 5, 1)],
    },
    {
        "query": "What does focus area E of the cross-border payments roadmap explore?",
        "expected_answer": "Focus area E explores the potential role of new payment infrastructures and "
                           "arrangements. Its building blocks are: considering new multilateral platforms for "
                           "cross-border payments, fostering sound global stablecoin arrangements, and factoring "
                           "an international dimension into central bank digital currency (CBDC) designs.",
        "relevant_pages": [(CBP, 6, 2), (CBP, 9, 2), (CBP, 5, 1)],
    },
    {
        "query": "Who chairs the CPMI Cross-border Payments Task Force?",
        "expected_answer": "Victoria Cleland of the Bank of England.",
        "relevant_pages": [(CBP, 10, 2)],
    },
    {
        "query": "What does building block 14 propose for cross-border payment message formats?",
        "expected_answer": "Adopting a harmonised version of ISO 20022 for message formats, including common "
                           "rules for converting and mapping data between different formats.",
        "relevant_pages": [(CBP, 9, 2)],
    },
 
    # ---------- questions 15-19: Stripe guide to payment methods ----------
    {
        "query": "Which payment methods does Stripe recommend for e-commerce and marketplaces?",
        "expected_answer": "Cards, digital wallets, authenticated bank debits, and buy now, pay later.",
        "relevant_pages": [(STRIPE, 5, 2), (STRIPE, 7, 1)],
    },
    {
        "query": "What share of online payments globally do credit and debit cards account for?",
        "expected_answer": "Cards account for 41% of online payments globally.",
        "relevant_pages": [(STRIPE, 17, 2)],
    },
    {
        "query": "What market share does Bacs Direct Debit have in the United Kingdom?",
        "expected_answer": "About 14% market share in the UK. It is also the most popular method for sending and "
                           "receiving recurring payments in the UK.",
        "relevant_pages": [(STRIPE, 14, 2)],
    },
    {
        "query": "How popular is iDEAL for online payments in the Netherlands?",
        "expected_answer": "iDEAL is the most popular online payment method in the Netherlands, with a share of "
                           "online payments close to 55%.",
        "relevant_pages": [(STRIPE, 23, 2)],
    },
    {
        "query": "According to a Stripe study, what percentage of online businesses sell internationally?",
        "expected_answer": "70% of online businesses are selling internationally.",
        "relevant_pages": [(STRIPE, 2, 2)],
    },
 
    # ---------- questions 20-24: FCA approach to payment services and e-money ----------
    {
        "query": "How long do payment service providers have to send a final response to a payment services complaint?",
        "expected_answer": "By the end of 15 business days after receiving the complaint. In exceptional "
                           "circumstances beyond the provider's control, by the end of 35 business days.",
        "relevant_pages": [(FCA, 182, 2)],
    },
    {
        "query": "What conditions must a business meet to register as a small payment institution?",
        "expected_answer": "Its average monthly value of payment transactions must not exceed €3 million "
                           "(measured over 12 months, or projected if it is new), and it must not provide "
                           "account information services (AIS) or payment initiation services (PIS).",
        "relevant_pages": [(FCA, 25, 2), (FCA, 46, 2), (FCA, 47, 1)],
    },
    {
        "query": "What are the two methods an institution can use to safeguard relevant funds?",
        "expected_answer": "The segregation method, and the insurance or comparable guarantee method. An "
                           "institution can also use a combination of the two.",
        "relevant_pages": [(FCA, 174, 2), (FCA, 168, 1)],
    },
    {
        "query": "What is strong customer authentication based on?",
        "expected_answer": "Two or more independent elements from these categories: something only the customer "
                           "knows (knowledge), something only the customer has (possession), and something the "
                           "customer is (inherence).",
        "relevant_pages": [(FCA, 264, 2)],
    },
    {
        "query": "How often must the safeguarding return be submitted, and by when?",
        "expected_answer": "The safeguarding return (REP027) is submitted monthly, within 15 business days of the "
                           "end of each month, through RegData.",
        "relevant_pages": [(FCA, 203, 2)],
    },
 
    # ---------- questions 25-29: PCI DSS quick reference guide ----------
    {
        "query": "How long must audit trail history be retained under PCI DSS?",
        "expected_answer": "At least one year, with at least three months of history immediately available for "
                           "analysis.",
        "relevant_pages": [(PCI, 23, 2)],
    },
    {
        "query": "How often does PCI DSS require penetration testing?",
        "expected_answer": "External and internal penetration testing at least annually and after any upgrade or "
                           "modification. If segmentation is used to reduce scope, penetration tests should also "
                           "verify that segmentation is working.",
        "relevant_pages": [(PCI, 24, 2)],
    },
    {
        "query": "What does PCI DSS require for remote network access from outside the network?",
        "expected_answer": "Two-factor authentication for all remote network access from outside the network, by "
                           "employees, administrators and third parties, including vendors.",
        "relevant_pages": [(PCI, 20, 2)],
    },
    {
        "query": "How can network segmentation reduce PCI DSS scope?",
        "expected_answer": "Segmentation isolates the cardholder data environment from the rest of the network. "
                           "This reduces the scope of PCI DSS, which can lower the cost and difficulty of "
                           "assessment and compliance and reduce risk. A system is only out of scope if it is "
                           "properly isolated from the cardholder data environment.",
        "relevant_pages": [(PCI, 31, 2), (PCI, 30, 1)],
    },
    {
        "query": "What is the PCI DSS Self-Assessment Questionnaire (SAQ)?",
        "expected_answer": "A validation tool for merchants and service providers to report the results of their "
                           "PCI DSS self-assessment when they are not required to submit a Report on Compliance. "
                           "It contains yes-or-no questions for each applicable requirement, and different SAQs "
                           "exist for different merchant environments.",
        "relevant_pages": [(PCI, 33, 2), (PCI, 34, 1)],
    },
 
    # ---------- questions 30-33: principles for financial market infrastructures ----------
    {
        "query": "How quickly should an FMI be able to resume operations after a disruption?",
        "expected_answer": "Critical IT systems should be able to resume operations within two hours after a "
                           "disruptive event, and the FMI should be able to complete settlement by the end of "
                           "the day of the disruption.",
        "relevant_pages": [(PFMI, 100, 2), (PFMI, 104, 2), (PFMI, 173, 1)],
    },
    {
        "query": "What default scenario should a systemically important CCP be able to cover with its financial resources?",
        "expected_answer": "A CCP with a more complex risk profile, or that is systemically important in "
                           "multiple jurisdictions, should hold enough additional financial resources to cover "
                           "the default of the two participants and their affiliates that would cause the largest "
                           "aggregate credit exposure in extreme but plausible market conditions. Other CCPs "
                           "should cover at least the largest single participant and its affiliates.",
        "relevant_pages": [(PFMI, 42, 2), (PFMI, 7, 1), (PFMI, 43, 1)],
    },
    {
        "query": "By when should an FMI provide final settlement?",
        "expected_answer": "No later than the end of the value date, and preferably intraday or in real time, to "
                           "reduce settlement risk.",
        "relevant_pages": [(PFMI, 70, 2), (PFMI, 71, 2), (PFMI, 8, 1)],
    },
    {
        "query": "What is a central counterparty (CCP)?",
        "expected_answer": "A CCP interposes itself between counterparties to contracts in one or more financial "
                           "markets, becoming the buyer to every seller and the seller to every buyer, which "
                           "ensures the performance of open contracts.",
        "relevant_pages": [(PFMI, 15, 2), (PFMI, 149, 1)],
    },
]
 