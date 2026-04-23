from infosci_spark_client import LLMClient
from svd import (
  build_svd,
  hybrid_search,
  explain_why_result_matched,
  get_user_facing_keywords,
)
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Build once at startup, not on every query
SVD_INDEX = build_svd(k=50)
SHOW_DF = SVD_INDEX["df"]


def row_to_context(row) -> str:
  """
  Convert one retrieved show row into text for the LLM.
  Adjust fields here to match your dataset.
  """
  title = row.get("title", "") or row.get("name", "") or "Untitled"
  overview = row.get("overview", "") or ""

  reddit_posts = row.get("reddit_posts", []) or []
  reddit_comments = row.get("reddit_comments", []) or []

  post_snippets = []
  for p in reddit_posts[:2]:
      if isinstance(p, dict):
          text = f"{p.get('title', '')} {p.get('text', '')}".strip()
          if text:
              post_snippets.append(text[:300])

  comment_snippets = []
  for c in reddit_comments[:3]:
      if isinstance(c, dict):
          text = c.get("text", "")
          if text:
              comment_snippets.append(text[:200])

  parts = [f"Title: {title}"]

  if overview:
      parts.append(f"Overview: {overview}")

  if post_snippets:
      parts.append("Reddit posts: " + " | ".join(post_snippets))

  if comment_snippets:
      parts.append("Reddit comments: " + " | ".join(comment_snippets))

  return "\n".join(parts)


def rewrite_query(user_query: str, client: LLMClient) -> str:
  """
  Use LLM to rewrite the user's query into a short retrieval query.
  """
  prompt = [
        {
            "role": "system",
            "content": (
                "Rewrite the user's query into a concise search query of up to 10 keywords. "
                "Convert vague or descriptive language into specific concepts used in TV show descriptions. "
                "Do not reuse vague adjectives unless necessary. "
                "Do not use full sentences. Return only the query."
            ),
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]
  response = client.chat(prompt, stream=False, show_thinking=False)
  return response["content"].strip()

def build_context_from_hits(retrieval_query: str, hits, svd_index) -> str:
  """
    Build the exact context that will be passed to the LLM from the same hits shown to the user.
  """
  blocks = []

  for rank, hit in enumerate(hits, start=1):
      title = hit.get("title", "Untitled")
      score = hit.get("score", 0.0)
      method = hit.get("search_method", "unknown")

      block_lines = [
          f"### Result {rank}: {title}",
          f"Score: {score:.4f}",
          f"Search method: {method}",
      ]

      doc_idx = hit.get("doc_idx")
      if doc_idx is not None:
          row = svd_index["df"].iloc[doc_idx]

          try:
              explanation = explain_why_result_matched(retrieval_query, hit, svd_index)
              keywords = get_user_facing_keywords(explanation)
              if keywords:
                  block_lines.append("Why it matched: " + ", ".join(keywords))
          except Exception:
              pass

          block_lines.append("")
          block_lines.append(row_to_context(row))
      else:
          overview = hit.get("overview", "") or hit.get("text", "") or ""
          if overview:
              block_lines.append("")
              block_lines.append(overview)

      blocks.append("\n".join(block_lines))

  return "\n\n---\n\n".join(blocks)

def retrieve_hits(retrieval_query: str, top_k: int = 5):
  """
    Retrieve hits that
    1. display in the app
    2. are used for the LLM context
    """
  return hybrid_search(query=retrieval_query, svd=SVD_INDEX, df=SHOW_DF, top_k=top_k)

def generate_answer(user_query: str, retrieval_query: str, hits, client: LLMClient) -> str:
  """
  Generate an answer using only the retrieved hits.
  """
  context = build_context_from_hits(retrieval_query, hits, SVD_INDEX)

  prompt = [
      {
          "role": "system",
          "content": (
              "You are a helpful assistant for a TV recommendation system. "
              "Answer using only the retrieved results below. "
              "Recommend shows only if they are supported by the retrieved context. "
              "When useful, mention which retrieved shows best match the user's request and why. "
              "If the retrieved context is weak or insufficient, say that clearly."
          ),
      },
      {
          "role": "user",
          "content": (
              f"Original user question:\n{user_query}\n\n"
              f"Retrieval query used by the IR system:\n{retrieval_query}\n\n"
              f"Retrieved results:\n\n{context}"
          ),
      },
  ]
  response = client.chat(prompt, stream=False, show_thinking=False)
  return response["content"].strip()

def run_rag(user_query: str, client: LLMClient, top_k: int = 5):
  """ 
  Full RAG pipeline: user query -> rewritten query -> retrieval -> displayed hits + LLM answer
  """

  retrieval_query = rewrite_query(user_query, client)
  hits = retrieve_hits(retrieval_query, top_k=top_k)
  answer = generate_answer(user_query, retrieval_query, hits, client)

  return {
      "original_query": user_query,
      "retrieval_query": retrieval_query,
      "hits": hits,
      "answer": answer,
  }

if __name__ == "__main__":
    query = input("Ask about reality shows: ").strip()

    client = LLMClient(api_key=os.getenv("SPARK_API_KEY"))

    result = run_rag(query, client, top_k=5)

    print("\nOriginal query:")
    print(result["original_query"])

    print("\nRewritten retrieval query:")
    print(result["retrieval_query"])

    print("\nRetrieved results:")
    for i, h in enumerate(result["hits"], start=1):
        print(f"{i}. score={h['score']:.4f} | {h.get('title', 'Untitled')[:80]}")
        if "doc_idx" in h:
            row = SVD_INDEX["df"].iloc[h["doc_idx"]]
            print("   overview:", (row.get("overview", "") or "")[:150])

    print("\nLLM answer:")
    print(result["answer"])