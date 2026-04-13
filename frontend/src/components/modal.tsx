import { useEffect } from 'react'

interface ModalProps {
    show: {
      title: string
      description: string
      language: string
      popularity: number
      rating: number
      first_air_date: string
      score: number
      genre_ids: number[]
      poster_path: string | null
      origin_country: string[]
      vote_count: number
      reddit_posts: unknown[]
      reddit_comments: unknown[]
      keywords: string[]
    } | null
  onClose: () => void
}

export const genres: Record<number, string> = {
  10764: "Reality",
  10765: "Sci-Fi & Fantasy",
  10766: "Soap",
  10767: "Talk",
  10768: "War & Politics",
  10759: "Action & Adventure",
  10762: "Kids",
  10763: "News",
  16: "Animation",
  18: "Drama",
  35: "Comedy",
  99: "Documentary",
  80: "Crime",
  37: "Western",
  10751: "Family",
  9648: "Mystery",
  10749: "Foreign",
}

export default function Modal({ show, onClose }: ModalProps) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  if (!show) return null

  const year = show.first_air_date?.split('-')[0] ?? 'Unknown'
  const posterUrl = `https://image.tmdb.org/t/p/original${show.poster_path}`

  console.log("poster_path value:", show.poster_path)
  console.log("full URL:", posterUrl)
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>

        <div className="modal-header">
            {show.poster_path ? (
            <img
                src={posterUrl}
                alt={show.title}
                className="modal-poster"
                referrerPolicy="no-referrer"
                onError={(e) => {
                    console.error("Poster failed to load:", (e.target as HTMLImageElement).src)
                }}
            />
            ) : (
            <div className="modal-poster placeholder-poster">
                🎬
            </div>
            )}
          <div className="modal-header-text">
            <div className="modal-badges">
              {(show.origin_country ?? []).map((c) => (
                <span key={c} className="badge">{c}</span>
            ))}
              <span className="modal-meta">{year}</span>
            </div>
            <h2 className="modal-title">{show.title}</h2>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="modal-stats">
            <div className="stat-card">
              <p className="stat-label">Rating</p>
              <p className="stat-value">{show.rating.toFixed(1)}</p>
              <p className="stat-sub">{show.vote_count} votes</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Language</p>
              <p className="stat-value">{show.language.toUpperCase()}</p>
            </div>
          </div>

          <p className="modal-description">{show.description}</p>

          {(show.keywords ?? []).length > 0 && (
            <p className="modal-keywords">
              Why this matched: <span>{show.keywords.join(', ')}</span>
            </p>
          )}
          
          {(show.genre_ids ?? []).length > 0 && (
            <div className="modal-tags">
                {(show.genre_ids ?? []).map((id) => (
                <span key={id} className="tag">{genres[id]}</span>
                ))}
            </div>
            )}

          {((show.reddit_posts ?? []).length > 0 || (show.reddit_comments ?? []).length > 0) && (
            <div className="modal-reddit">
                <p className="stat-label">Community</p>
                <p>{(show.reddit_posts ?? []).length} posts · {(show.reddit_comments ?? []).length} comments</p>
            </div>
            )}
        </div>

        <div className="modal-footer">
          <button className="modal-close-btn" onClick={onClose}>Close</button>
        </div>

      </div>
    </div>
  )
}