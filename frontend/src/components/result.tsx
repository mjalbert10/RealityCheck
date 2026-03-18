function Result({ title,year,rating,similarity,description,tags }: { title: string; year: number; rating: number; similarity: number; description: string; tags: string[] }) {
  return (
    <div className="result-item">
      <h3>{title}</h3>
      <p>Year: {year} | Rating: {rating} | Similarity: {similarity}</p>
      <p>{description}</p>
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