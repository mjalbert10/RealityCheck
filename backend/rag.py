from infosci_spark_client import LLMClient
from svd import (
  build_svd,
  hybrid_search,
  explain_why_result_matched,
  get_user_facing_keywords,
)

# Build once at startup, not on every query
SVD_INDEX = build_svd(k=50)
DF = SVD_INDEX["df"]


def row_to_context(row) -> str:
  """
  Convert one retrieved show row into text for the LLM.
  Adjust fields here to match your dataset.
  """
  title = row.get("title", "") or row.get("name", "") or "Untitled"
  overview = row.get("overview", "") or ""
  tokens = " ".join(row.get("all_tokens", []))

  reddit_posts = row.get("reddit_posts", []) or []
  reddit_comments = row.get("reddit_comments", []) or []

  post_text = " ".join(
    f"{p.get('title', '')} {p.get('text', '')}".strip()
    for p in reddit_posts
    if isinstance(p, dict)
  )

  comment_text = " ".join(
    c.get("text", "")
    for c in reddit_comments
    if isinstance(c, dict)
  )

  parts = [
    f"Title: {title}",
    f"Overview: {overview}",
    f"Tokens: {tokens}",
  ]

  if post_text:
    parts.append(f"Reddit posts: {post_text}")
  if comment_text:
    parts.append(f"Reddit comments: {comment_text}")

  return "\n".join(parts)


def retrieve_for_rag(query: str, top_k: int = 5):
  """
  Retrieve documents using YOUR existing SVD pipeline
  and build one context string for the LLM.
  """
  hits = hybrid_search(query=query, svd=SVD_INDEX, df=DF, top_k=top_k)

  blocks = []
  for rank, hit in enumerate(hits, start=1):
    title = hit.get("title", "Untitled")
    score = hit.get("score", 0.0)
    method = hit.get("search_method", "unknown")

    block_lines = [
      f"### [{rank}] {title}",
      f"score: {score:.4f}",
      f"search_method: {method}",
    ]

    # SVD hits from your code include doc_idx
    doc_idx = hit.get("doc_idx")
    if doc_idx is not None:
      row = SVD_INDEX["df"].iloc[doc_idx]

      explanation = explain_why_result_matched(query, hit, SVD_INDEX)
      keywords = get_user_facing_keywords(explanation)

      if keywords:
        block_lines.append("matched_keywords: " + ", ".join(keywords))

      block_lines.append("")
      block_lines.append(row_to_context(row))
    else:
      # TF-IDF fallback path
      block_lines.append("")
      block_lines.append(hit.get("overview", "") or hit.get("text", ""))

    blocks.append("\n".join(block_lines))

  context = "\n\n---\n\n".join(blocks)
  return hits, context


def run_rag(user_query: str, client: LLMClient):
  hits, ctx = retrieve_for_rag(user_query, top_k=5)

  prompt = [
    {
      "role": "system",
      "content": (
        "You are answering questions using only the retrieved show data below. "
        "If the answer is not supported by the retrieved context, say so."
      ),
    },
    {
      "role": "user",
      "content": f"Question:\n{user_query}\n\nRetrieved context:\n\n{ctx}",
  },
]

  return client.chat(prompt, stream=False, show_thinking=False)

def rewrite_query(user_query: str, client: LLMClient) -> str:
  prompt = [
    {
      "role": "system",
      "content": (
        "Rewrite the user's query for retrieval. "
        "Keep it short, concrete, and focused on key entities and concepts. "
        "Return only the rewritten query."
        ),
    },
    {
      "role": "user",
      "content": user_query,
    },
  ]

  response = client.chat(prompt, stream=False, show_thinking=False)
  return response["content"].strip()


def run_rag_modified_query(user_query: str, client: LLMClient):
  modified_query = rewrite_query(user_query, client)
  hits, ctx = retrieve_for_rag(modified_query, top_k=5)

  prompt = [
    {
      "role": "system",
      "content": (
        "You are answering questions using only the retrieved show data below. "
        "If the answer is not supported by the retrieved context, say so."
      ),
  },
    {
      "role": "user",
      "content": (
        f"Original question:\n{user_query}\n\n"
        f"Retrieval query:\n{modified_query}\n\n"
        f"Retrieved context:\n\n{ctx}"
      ),
    },
  ]

  return client.chat(prompt, stream=False, show_thinking=False)

if __name__ == "__main__":
  query = input("ask abt reality shows: ").strip()
  client = LLMClient()
  answer = run_rag_modified_query(query, client)
  results = hybrid_search(query, SVD_INDEX, DF, top_k=5)

  for i, h in enumerate(results, start=1):
    print(f"{i}. score={h['score']:.4f} | {h['title'][:60]}")

    # if you want the underlying dataframe row
    if "doc_idx" in h:
      row = SVD_INDEX["df"].iloc[h["doc_idx"]]
      print("   overview:", row.get("overview", "")[:120])