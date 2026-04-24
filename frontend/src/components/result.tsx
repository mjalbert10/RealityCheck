function Result({
  title,
  year,
  rating,
  similarity,
  description,
  tags,
  keywords,
  aiExplanation,
  dimensions
}: {
  title: string;
  year: number;
  rating: number;
  similarity: number;
  description: string;
  tags: string[];
  keywords: string[];
  aiExplanation?: string;
  dimensions?: any[];
}) {
  return (
    <div className="result-item">
      <h3 className="result-title">{title}</h3>

      <p className="result-subtitle">
        Year: {year} | Rating: {rating} | Similarity:{" "}
        {(similarity * 100).toFixed(1)}% (
        {similarity >= 0.75
          ? "High"
          : similarity >= 0.5
          ? "Medium"
          : "Low"}
        )
      </p>

      <p className="result-description">{description}</p>

      {/* WHY IT MATCHED */}
      {(keywords.length > 0 || aiExplanation) && (
        <div className="why-matched">
          <p>
            <strong>Why this matched:</strong>{" "}
            {aiExplanation ? (
              <span>{aiExplanation}</span>
            ) : (
              <span>{keywords.join(", ")}</span>
            )}
          </p>
        </div>
      )}

      {/* SVD DIMENSIONS */}
      {(dimensions?.length ?? 0) > 0 && (
        <div className="svd-dimensions">
          <p>
            <strong>Match dimensions:</strong>
          </p>
          <ul>
            {dimensions?.slice(0, 3).map((dim, i) => (
              <li key={i}>
                Dimension {dim.dimension}:{" "}
                {dim.matched_words?.slice(0, 3).join(", ") ||
                  "general theme"}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* TAGS */}
      <div className="tags">
        {tags.map((tag, index) => (
          <span key={index} className="tag">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}

export default Result;