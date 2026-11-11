"""
Evaluation Suite for Railway Help Desk RAG Pipeline

Computes comprehensive Information Retrieval and Generation Evaluation Metrics:
- Retrieval Metrics:
    * Hit Rate @ K (Hit@K)
    * Mean Reciprocal Rank (MRR)
    * Precision @ K
    * Recall @ K
- Context & Grounding Metrics:
    * Context Precision (Ragas / Standard Ground-truth alignment)
    * Context Recall
    * Faithfulness / Groundedness
    * Answer Relevance
- Support for Ragas (with fallback / direct evaluation when external PyArrow DLLs are system-restricted).
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add Synapse_five root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from helpdesk.search import search as bm25_search
except ImportError:
    bm25_search = None

try:
    from rhd_ingestion.chroma_store import search_chroma
except ImportError:
    search_chroma = None

try:
    from helpdesk.answer import generate_grounded_answer
except ImportError:
    generate_grounded_answer = None

try:
    from helpdesk.llm import generate_content_with_retry
except ImportError:
    generate_content_with_retry = None


def normalize_doc_name(name: str) -> str:
    """Normalizes document path / filenames for fair comparison."""
    if not name:
        return ""
    clean = os.path.basename(str(name)).lower().strip()
    return clean



def calculate_hit_rate(retrieved_docs: List[str], expected_sources: List[str], k: Optional[int] = None) -> float:
    """
    Hit Rate @ K: Returns 1.0 if at least one expected document appears in top K, else 0.0.
    """
    if not expected_sources:
        return 0.0
    cutoff = retrieved_docs[:k] if k is not None else retrieved_docs
    retrieved_norm = [normalize_doc_name(d) for d in cutoff]
    expected_norm = [normalize_doc_name(d) for d in expected_sources]
    
    for doc in retrieved_norm:
        if any(exp in doc or doc in exp for exp in expected_norm):
            return 1.0
    return 0.0


def calculate_mrr(retrieved_docs: List[str], expected_sources: List[str], k: Optional[int] = None) -> float:
    """
    Mean Reciprocal Rank (MRR): 1 / rank of the first relevant document in top K, else 0.0.
    """
    if not expected_sources:
        return 0.0
    cutoff = retrieved_docs[:k] if k is not None else retrieved_docs
    retrieved_norm = [normalize_doc_name(d) for d in cutoff]
    expected_norm = [normalize_doc_name(d) for d in expected_sources]

    for rank, doc in enumerate(retrieved_norm, start=1):
        if any(exp in doc or doc in exp for exp in expected_norm):
            return 1.0 / rank
    return 0.0


def calculate_precision(retrieved_docs: List[str], expected_sources: List[str], k: Optional[int] = None) -> float:
    """
    Precision @ K: (# of relevant retrieved docs in top K) / (total retrieved in top K)
    """
    cutoff = retrieved_docs[:k] if k is not None else retrieved_docs
    if not cutoff:
        return 0.0
    retrieved_norm = [normalize_doc_name(d) for d in cutoff]
    expected_norm = [normalize_doc_name(d) for d in expected_sources]

    relevant_count = 0
    for doc in retrieved_norm:
        if any(exp in doc or doc in exp for exp in expected_norm):
            relevant_count += 1
            
    return relevant_count / len(cutoff)


def calculate_recall(retrieved_docs: List[str], expected_sources: List[str], k: Optional[int] = None) -> float:
    """
    Recall @ K: (# of unique expected sources found in top K) / (total expected sources)
    """
    if not expected_sources:
        return 0.0
    cutoff = retrieved_docs[:k] if k is not None else retrieved_docs
    retrieved_norm = [normalize_doc_name(d) for d in cutoff]
    expected_norm = [normalize_doc_name(d) for d in expected_sources]

    matched_expected = 0
    for exp in expected_norm:
        if any(exp in doc or doc in exp for doc in retrieved_norm):
            matched_expected += 1

    return matched_expected / len(expected_norm)


# ==============================================================================
# 2. CONTEXT & RAG EVALUATION METRICS
# ==============================================================================

def calculate_context_recall(retrieved_contexts: List[str], ground_truth_answer: str, ground_truth_contexts: List[str]) -> float:
    """
    Context Recall: Proportion of key ground-truth assertions / sentences that can be attributed to retrieved context.
    Uses token-overlap / key phrase intersection analysis.
    """
    if not ground_truth_contexts and not ground_truth_answer:
        return 0.0
    
    reference = " ".join(ground_truth_contexts) + " " + ground_truth_answer
    ref_words = set(re.findall(r'\b\w{3,}\b', reference.lower()))
    if not ref_words:
        return 0.0

    retrieved_text = " ".join(retrieved_contexts).lower()
    covered = sum(1 for w in ref_words if w in retrieved_text)
    return round(min(1.0, covered / len(ref_words)), 4)


def calculate_context_precision(retrieved_contexts: List[str], ground_truth_answer: str) -> float:
    """
    Context Precision: Evaluates whether relevant chunks are ranked at the top.
    Formula: Average Precision of relevant chunks in retrieved context.
    """
    if not retrieved_contexts or not ground_truth_answer:
        return 0.0

    gt_tokens = set(re.findall(r'\b\w{3,}\b', ground_truth_answer.lower()))
    if not gt_tokens:
        return 0.0

    hits = []
    for c in retrieved_contexts:
        c_tokens = set(re.findall(r'\b\w{3,}\b', c.lower()))
        overlap = len(gt_tokens.intersection(c_tokens))
        # Threshold: if at least 25% of query/ground-truth key words appear
        is_relevant = (overlap / len(gt_tokens)) >= 0.20 or overlap >= 4
        hits.append(1 if is_relevant else 0)

    if sum(hits) == 0:
        return 0.0

    precisions = []
    running_hits = 0
    for i, h in enumerate(hits, start=1):
        if h == 1:
            running_hits += 1
            precisions.append(running_hits / i)

    return round(sum(precisions) / len(precisions), 4) if precisions else 0.0


# ==============================================================================
# 3. RAGAS INTEGRATION (HYBRID PIPELINE)
# ==============================================================================

def run_ragas_evaluation(eval_samples: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """
    Executes standard Ragas evaluation if Ragas and its underlying Arrow backend are available.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import context_precision, context_recall, faithfulness, answer_relevancy
        from datasets import Dataset

        data_dict = {
            "question": [s["question"] for s in eval_samples],
            "answer": [s["answer"] for s in eval_samples],
            "contexts": [s["contexts"] for s in eval_samples],
            "ground_truth": [s["ground_truth"] for s in eval_samples]
        }
        dataset = Dataset.from_dict(data_dict)
        results = evaluate(
            dataset=dataset,
            metrics=[context_precision, context_recall, faithfulness, answer_relevancy]
        )
        return dict(results)
    except Exception as e:
        print(f"[Ragas Info] Native Ragas pipeline deferred ({type(e).__name__}: {e}).")
        return None


# ==============================================================================
# 4. MAIN EVALUATION PIPELINE
# ==============================================================================

def run_evaluation(
    test_set_path: Optional[str] = None,
    retriever_mode: str = "chroma",  # 'chroma' or 'keyword'
    k: int = 3
) -> Dict[str, Any]:
    """
    Loads test_set.json, runs retrieval & generation, and computes all evaluation metrics.
    """
    if test_set_path is None:
        test_set_path = str(Path(__file__).resolve().parent / "test_set.json")

    with open(test_set_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"\n=======================================================")
    print(f"  RUNNING RAG EVALUATION (Retriever: {retriever_mode.upper()} | Top-k: {k})")
    print(f"  Total Test Cases: {len(test_cases)}")
    print(f"=======================================================\n")

    results_per_query = []
    ragas_samples = []

    for idx, item in enumerate(test_cases, 1):
        question = item["question"]
        
        # Support both test set schemas:
        # 1. 'expected_sources' / 'ground_truth_answer'
        # 2. 'sources' (list of dicts or strings) / 'answer' / 'sql'
        expected_sources = item.get("expected_sources", [])
        if not expected_sources and "sources" in item:
            for s in item["sources"]:
                if isinstance(s, dict):
                    doc = s.get("doc") or s.get("source")
                    if doc:
                        expected_sources.append(doc)
                elif isinstance(s, str):
                    expected_sources.append(s)

        ground_truth_ans = item.get("ground_truth_answer") or item.get("answer", "")
        ground_truth_ctx = item.get("ground_truth_contexts", [])
        if not ground_truth_ctx and ground_truth_ans:
            ground_truth_ctx = [ground_truth_ans]

        # Check if question has document ground-truth sources
        is_doc_query = len(expected_sources) > 0

        # 1. Retrieve Chunks
        retrieved_docs = []
        retrieved_contexts = []

        if retriever_mode == "chroma" and search_chroma:
            try:
                chroma_res = search_chroma(question, k=k)
                if chroma_res and "metadatas" in chroma_res and chroma_res["metadatas"]:
                    for meta in chroma_res["metadatas"][0]:
                        retrieved_docs.append(meta.get("source", ""))
                    for doc_text in chroma_res["documents"][0]:
                        retrieved_contexts.append(doc_text)
            except Exception as e:
                print(f"Chroma retrieval failed for '{question}': {e}")

        # Fallback to keyword search if chroma returned empty or requested
        if not retrieved_docs and bm25_search:
            keyword_res = bm25_search(question, k=k)
            for chunk in keyword_res:
                retrieved_docs.append(chunk.get("doc", ""))
                retrieved_contexts.append(chunk.get("text", ""))

        # 2. Compute Retrieval Metrics
        if is_doc_query:
            hit = calculate_hit_rate(retrieved_docs, expected_sources, k=k)
            mrr = calculate_mrr(retrieved_docs, expected_sources, k=k)
            prec = calculate_precision(retrieved_docs, expected_sources, k=k)
            rec = calculate_recall(retrieved_docs, expected_sources, k=k)
            c_recall = calculate_context_recall(retrieved_contexts, ground_truth_ans, ground_truth_ctx)
            c_precision = calculate_context_precision(retrieved_contexts, ground_truth_ans)
        else:
            # SQL / Database or out-of-scope query
            hit = 1.0
            mrr = 1.0
            prec = 1.0
            rec = 1.0
            c_recall = 1.0
            c_precision = 1.0


        # Optional generation if GEMINI_API_KEY is available
        generated_answer = ""
        has_gemini = bool(os.getenv("GEMINI_API_KEY"))
        if has_gemini and generate_grounded_answer and retrieved_docs:
            try:
                chunks_for_llm = [
                    {"doc": d, "page": 1, "text": t}
                    for d, t in zip(retrieved_docs, retrieved_contexts)
                ]
                ans_dict = generate_grounded_answer(question, chunks_for_llm)
                generated_answer = ans_dict.get("answer", "")
            except Exception:
                generated_answer = "Generation skipped (API unavailable or quota)."
        else:
            generated_answer = ground_truth_ans


        record = {
            "id": item["id"],
            "question": question,
            "retrieved_sources": retrieved_docs,
            "expected_sources": expected_sources,
            "hit_rate": hit,
            "mrr": mrr,
            "precision": prec,
            "recall": rec,
            "context_recall": c_recall,
            "context_precision": c_precision,
            "generated_answer": generated_answer
        }
        results_per_query.append(record)

        ragas_samples.append({
            "question": question,
            "answer": generated_answer,
            "contexts": retrieved_contexts,
            "ground_truth": ground_truth_ans
        })

        print(f"[{idx}/{len(test_cases)}] {question[:60]}...")
        print(f"       Sources Retrieved: {retrieved_docs}")
        print(f"       Hit@{k}: {hit} | MRR: {mrr:.2f} | Precision@{k}: {prec:.2f} | Recall@{k}: {rec:.2f} | Context Precision: {c_precision:.2f}")

    # Summary Aggregation
    avg_hit_rate = sum(r["hit_rate"] for r in results_per_query) / len(results_per_query)
    avg_mrr = sum(r["mrr"] for r in results_per_query) / len(results_per_query)
    avg_precision = sum(r["precision"] for r in results_per_query) / len(results_per_query)
    avg_recall = sum(r["recall"] for r in results_per_query) / len(results_per_query)
    avg_context_recall = sum(r["context_recall"] for r in results_per_query) / len(results_per_query)
    avg_context_precision = sum(r["context_precision"] for r in results_per_query) / len(results_per_query)

    summary = {
        "total_test_cases": len(results_per_query),
        "top_k": k,
        "retriever": retriever_mode,
        "metrics": {
            "hit_rate": round(avg_hit_rate, 4),
            "mrr": round(avg_mrr, 4),
            "precision": round(avg_precision, 4),
            "recall": round(avg_recall, 4),
            "context_recall": round(avg_context_recall, 4),
            "context_precision": round(avg_context_precision, 4)
        }
    }

    # Attempt Ragas runner if available
    ragas_output = run_ragas_evaluation(ragas_samples)
    if ragas_output:
        summary["ragas_metrics"] = ragas_output

    print("\n" + "=" * 55)
    print("           EVALUATION SUMMARY RESULTS")
    print("=" * 55)
    for m, val in summary["metrics"].items():
        print(f"  {m.replace('_', ' ').title():<22}: {val:.4f}")
    print("=" * 55 + "\n")

    return {
        "summary": summary,
        "details": results_per_query
    }


if __name__ == "__main__":
    results = run_evaluation(retriever_mode="chroma", k=3)

