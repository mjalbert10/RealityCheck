import { useEffect } from 'react'

interface Dimension {
  dimension: number
  matched_words: string[]
}

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
    match_dimensions?: Dimension[]
    llm_explanation?: string
  } | null
  onClose: () => void
}

export const genres: Record<number, string> = {
  10764: "Reality", 10765: "Sci-Fi & Fantasy", 10766: "Soap",
  10767: "Talk", 10768: "War & Politics", 10759: "Action & Adventure",
  10762: "Kids", 10763: "News", 16: "Animation", 18: "Drama",
  35: "Comedy", 99: "Documentary", 80: "Crime", 37: "Western",
  10751: "Family", 9648: "Mystery", 10749: "Foreign",
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
  const aiExplanation = show.llm_explanation
  const dimensions = show.match_dimensions

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>

        <div className="modal-header">
          {show.poster_path ? (
            <img
              src={posterUrl}
              alt={show.title}
              className="modal-poster"
              referrerPolicy="no-referrer"
              onError={e => (e.target as HTMLImageElement).style.display = 'none'}
            />
          ) : (
            <div className="modal-poster modal-poster--placeholder">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="2" y="3" width="20" height="18" rx="3" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M10 8l6 4-6 4V8z" fill="currentColor"/>
              </svg>
            </div>
          )}

          <div className="modal-header-text">
            <div className="modal-badges">
              {(show.origin_country ?? []).map(c => (
                <span key={c} className="modal-badge">{c}</span>
              ))}
              <span className="modal-year">{year}</span>
            </div>
            <h2 className="modal-title">{show.title}</h2>
          </div>

          <button className="modal-close" onClick={onClose}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <div className="modal-body">

          <div className="modal-stats">
            <div className="stat-card">
              <p className="stat-label">Rating</p>
              <p className="stat-value">{show.rating?.toFixed(1) ?? '—'}</p>
              <p className="stat-sub">{(show.vote_count ?? 0).toLocaleString()} votes</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Language</p>
              <p className="stat-value">{show.language?.toUpperCase() ?? '—'}</p>
            </div>
            {((show.reddit_posts ?? []).length > 0 || (show.reddit_comments ?? []).length > 0) && (
              <div className="stat-card">
                <p className="stat-label">Community</p>
                <p className="stat-value">{(show.reddit_posts ?? []).length + (show.reddit_comments ?? []).length}</p>
                <p className="stat-sub">posts &amp; comments</p>
              </div>
            )}
          </div>

          <p className="modal-description">{show.description}</p>

          {aiExplanation && aiExplanation.length > 0 && (
            <div className="modal-match">
              <p className="modal-match-label">Why it matched</p>
              <p className="modal-match-text">{aiExplanation}</p>
            </div>
          )}

          {(dimensions?.length ?? 0) > 0 && (
            <div className="modal-dims">
              <p className="modal-dims-label">Match dimensions</p>
              <div className="modal-dims-list">
                {dimensions!.slice(0, 3).map((dim, i) => (
                  <div key={i} className="modal-dim-row">
                    <span className="modal-dim-label">Dim {dim.dimension}</span>
                    <div className="modal-dim-bar-bg">
                      <div className="modal-dim-bar-fill" style={{ width: `${[88, 61, 40][i]}%` }} />
                    </div>
                    <span className="modal-dim-words">
                      {dim.matched_words?.slice(0, 3).join(', ') || 'general theme'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(show.genre_ids ?? []).length > 0 && (
            <div className="modal-tags">
              {(show.genre_ids ?? []).map(id => (
                <span key={id} className="tag">{genres[id]}</span>
              ))}
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