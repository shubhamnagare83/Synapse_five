# Evaluation Experiments & Benchmark Log

This document records the evaluation benchmark experiments conducted for the Indian Railway Passenger Help Desk RAG pipeline.

---

## 1. Evaluation Methodology

The evaluation benchmarks both **Information Retrieval (IR)** and **Context Grounding / Generation**:

| Metric Category | Metrics Evaluated | Purpose |
| :--- | :--- | :--- |
| **Retrieval Quality** | **Hit Rate @ K** (`Hit@3`) | Checks whether at least one relevant official circular is retrieved in the top $K$. |
| | **Mean Reciprocal Rank (MRR)** | Measures how early the first relevant source appears in the ranked results. |
| | **Precision @ K** (`Precision@3`) | Measures the ratio of retrieved sources that are relevant. |
| | **Recall @ K** (`Recall@3`) | Measures the coverage of all expected ground-truth sources. |
| **Context Quality** | **Context Precision** | Measures whether relevant chunks are ranked higher than irrelevant ones. |
| | **Context Recall** | Measures whether the retrieved passages contain all the required ground-truth information. |
| **Ragas Integration** | `context_precision`, `context_recall`, `faithfulness`, `answer_relevancy` | Native Ragas workflow with graceful fallback when system DLL policies restrict PyArrow C-extensions. |

---

## 2. Test Set Design (`eval/test_set.json`)

10 high-value multi-lingual queries covering key Indian Railways circulars and policies:
1. **Advance Reservation Period (ARP)** — CC 10/2024 (60 days rule).
2. **Confirmed AC 1st Class Cancellation (>48 hrs)** — Rs. 240 + GST flat charge.
3. **Cancellation 48h to 12h** — 25% minimum rule.
4. **RAC / Waitlist Cancellation** — Rs. 60 clerkage charge.
5. **Confirmed Tatkal Ticket Refund** — Non-refundable policy (CC 08/2025).
6. **Train Late > 3 Hours** — Full refund rule via TDR.
7. **Vande Bharat Sleeper Express (72h to 8h)** — 50% cancellation fee.
8. **वंदे भारत स्लीपर एक्सप्रेस (Hindi query > 72h)** — 25% fee (Gazette notification).
9. **AC Failure enroute** — TDR filing window (20 hours).
10. **Tatkal Aadhaar Authentication** — Anti-fraud bot prevention rules.

---

## 3. Benchmark Experiment Results

**Configuration:**
- **Vector Retriever:** ChromaDB with ONNX `all-MiniLM-L6-v2` embeddings
- **Top-$K$ retrieved:** 3
- **Collection:** `railway_passenger_rules` (Indexed from `final_chunks.json`)

### Summary Results:

```text
=======================================================
           EVALUATION SUMMARY RESULTS
=======================================================
  Hit Rate @ 3          : 1.0000 (100.0%)
  MRR                   : 0.9500
  Precision @ 3         : 0.8333 (83.33%)
  Recall @ 3            : 0.9000 (90.00%)
  Context Recall        : 0.7576 (75.76%)
  Context Precision     : 1.0000 (100.0%)
=======================================================
```

---

## 4. Observations & Recommendations

1. **High Retrieval Precision & Hit Rate**: With ChromaDB semantic search, the pipeline achieved a **100% Hit Rate** and **0.95 MRR**, retrieving the authoritative circulars on rank 1 for 9 out of 10 queries.
2. **Multi-lingual Capability**: The Hindi Vande Bharat query successfully retrieved the Hindi Gazette circular chunks (`rb_cc08_2026_vande_bharat_sleeper_refund.pdf`) with perfect precision.
3. **System Environment Note**: On Windows systems where Windows Defender Application Control (WDAC) restricts `pyarrow` DLL loading, the evaluation script executes all standard mathematical formulas natively while providing seamless hooks for `ragas`.

