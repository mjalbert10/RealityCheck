function Result({
  title,
  year,
  rating,
  similarity,
  description,
  tags,
  dimensions,
  aiExplanation,
}: {
  title: string;
  year: number;
  rating: number;
  similarity: number;
  description: string;
  tags: string[];
  dimensions?: { dimension: number; matched_words: string[]; positive_words: string[]; contribution: number }[];
  aiExplanation?: string;
}) {
  const pct = Math.round(similarity * 100);
  const tier = similarity >= 0.75 ? 'high' : similarity >= 0.5 ? 'mid' : 'low';
  const maxContribution = Math.max(...dimensions!.map(d => d.contribution));

  return (
    <div className="result-card">
      <div className="result-top">
        <h3 className="result-title">{title}</h3>
        <span className={`score-pill score-pill--${tier}`}>
          <span className={`score-dot score-dot--${tier}`} />
          {pct}% match
        </span>
      </div>

      <div className="result-meta">
        {year > 0 && <span>{year}</span>}
        {rating > 0 && (
          <>
            <span className="result-meta-sep" />
            <span className="result-meta-rating">
              <svg width="12" height="12" viewBox="0 0 12 12">
                <polygon
                  points="6,1 7.5,4.5 11,5 8.5,7.5 9,11 6,9.5 3,11 3.5,7.5 1,5 4.5,4.5"
                  fill="#d4922a"
                />
              </svg>
              {rating.toFixed(1)}
            </span>
          </>
        )}
      </div>

      <p className="result-desc">{description}</p>

      {aiExplanation && aiExplanation.length > 0 && (
        <div className="result-match">
          <div className="result-match-label">Why it matched</div>
          {aiExplanation}
        </div>
      )}

      {(dimensions?.length ?? 0) > 0 && (
        <div className="result-dims">
          {dimensions!.slice(0, 3).map((dim, i) => (
            <div key={dim.dimension} className="dim-row">
              <span className="dim-label">Dim {dim.dimension} · {Math.round(dim.contribution * 100)}%</span>
              <div className="dim-bar-bg">
                <div className="dim-bar-fill" style={{ width: `${Math.round((dim.contribution / maxContribution) * 100)}%` }} />
              </div>
              <span className="dim-words">
                {dim.positive_words?.slice(0, 3).join(', ') || 'general theme'}
              </span>
            </div>
          ))}
        </div>
      )}

      {tags.length > 0 && (
        <div className="result-tags">
          {tags.map((tag, i) => (
            <span key={i} className="tag">{tag}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export default Result;