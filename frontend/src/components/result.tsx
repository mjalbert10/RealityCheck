function Result({ title,year,rating,similarity,description,tags }: { title: string; year: number; rating: number; similarity: number; description: string; tags: string[] }) {
  return (
    <div className="result-item">
      <h3 className="result-title">{title}</h3>
      <p className="result-subtitle">Year: {year} | Rating: {rating} | Similarity: {similarity} {similarity >= 0.75 ? "High Similarity" : similarity >= 0.5 ? "Medium Similarity" : "Low Similarity"}</p>
      <p className="result-description">{description}</p>
      <div className="tags">
        {tags.map((tag, index) => (
          <span key={index} className="tag">
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}

export default Result