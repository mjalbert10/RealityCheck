import './App.css'
import { useState, useEffect } from 'react'
import Modal from './components/modal'
import Result from './components/result'
import SearchIcon from './assets/mag.png'
import ReactMarkdown from 'react-markdown'

const MD = ReactMarkdown as React.ElementType;

const GENRE_MAP: Record<number, string> = {
  10764: "Reality", 10765: "Sci-Fi & Fantasy", 10766: "Soap",
  10767: "Talk", 10768: "War & Politics", 10759: "Action & Adventure",
  10762: "Kids", 10763: "News", 16: "Animation", 18: "Drama",
  35: "Comedy", 99: "Documentary", 80: "Crime", 37: "Western",
  10751: "Family", 9648: "Mystery", 10749: "Foreign",
};

interface ShowResult {
  title: string; description: string; language: string;
  popularity: number; rating: number; first_air_date: string;
  score: number; genre_ids: number[]; poster_path: string | null;
  origin_country: string[]; vote_count: number;
  reddit_posts: unknown[]; reddit_comments: unknown[];
  match_dimensions: { dimension: number; matched_words: string[]; positive_words: string[] }[];
  dimensions: number[];
  llm_explanation?: string;
}

interface FilterOptions {
  languages: string[];
  years: { min: string; max: string };
  ratings: { min: number; max: number };
  popularity: { min: number; max: number };
  genre_ids: number[];
}

export default function App() {
  const [filtersOn, setFiltersOn] = useState(true);
  const [results, setResults] = useState<ShowResult[]>([]);
  const [ragOverview, setRagOverview] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [searchType, setSearchType] = useState('tfidf');
  const [subgenre, setSubgenre] = useState('');
  const [yearRange, setYearRange] = useState({ start: '', end: '' });
  const [language, setLanguage] = useState<string[]>([]);
  const [ratings, setRatings] = useState({ min: '', max: '' });
  const [popularity, setPopularity] = useState('');
  const [selectedShow, setSelectedShow] = useState<ShowResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/filters')
      .then(r => r.json())
      .then(setFilterOptions)
      .catch(err => console.error('Failed to load filters:', err));
  }, []);

  const performSearch = () => {
    if (!searchQuery.trim()) { setResults([]); return; }
    const params = new URLSearchParams({ q: searchQuery });
    params.append('type', searchType);
    if (subgenre)            params.append('subgenre', subgenre);
    if (yearRange.start)     params.append('year_start', yearRange.start);
    if (yearRange.end)       params.append('year_end', yearRange.end);
    if (language.length > 0) params.append('language', language.join(','));
    if (ratings.min !== '')  params.append('rating_min', ratings.min);
    if (ratings.max !== '')  params.append('rating_max', ratings.max);
    if (popularity)          params.append('popularity', popularity);

    setLoading(true);
    fetch(`/api/search?${params}`)
      .then(r => r.json())
      .then(data => {
        setResults(data.results ?? []);
        setRagOverview(data.answer ?? '');
      })
      .catch(err => console.error('Search failed:', err))
      .finally(() => setLoading(false));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') performSearch();
  };


  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">RealityCheck</h1>
        <p className="app-subtitle">
          Keeping the TV show search <span className="app-emphasis">REAL</span>
        </p>
      </header>

      <div className="app-body">
        {filtersOn && (
          <aside
            className="filter-panel"
            id="filter-panel"
            aria-label="Search filters"
          >
            <p className="filter-section-label">The basics</p>

            <div className="filter-group">
              <label className="filter-label" htmlFor="genre-select">Genre</label>
              <select
                id="genre-select"
                className="filter-select"
                value={subgenre}
                onChange={e => setSubgenre(e.target.value)}
              >
                <option value="">All genres</option>
                {filterOptions?.genre_ids.map(id => (
                  <option key={id} value={String(id)}>{GENRE_MAP[id] ?? `Genre ${id}`}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              {/* fieldset/legend instead of bare label for a range pair */}
              <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="filter-label">Release year</legend>
                <div className="range-row">
                  <input
                    className="filter-input"
                    id="year-from"
                    type="number"
                    aria-label="From year"
                    placeholder={filterOptions?.years.min ?? 'From'}
                    min={filterOptions?.years.min ?? '1900'}
                    max={filterOptions?.years.max ?? '2026'}
                    value={yearRange.start}
                    onChange={e => setYearRange({ ...yearRange, start: e.target.value })}
                  />
                  <span className="range-sep" aria-hidden="true">–</span>
                  <input
                    className="filter-input"
                    id="year-to"
                    type="number"
                    aria-label="To year"
                    placeholder={filterOptions?.years.max ?? 'To'}
                    min={filterOptions?.years.min ?? '1900'}
                    max={filterOptions?.years.max ?? '2026'}
                    value={yearRange.end}
                    onChange={e => setYearRange({ ...yearRange, end: e.target.value })}
                  />
                </div>
              </fieldset>
            </div>

            <div className="filter-group">
              <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="filter-label">Language</legend>
                <div className="checkbox-list">
                  {filterOptions?.languages.map(lang => (
                    <label key={lang} className="checkbox-item">
                      <input
                        type="checkbox"
                        value={lang}
                        checked={language.includes(lang)}
                        onChange={e => setLanguage(
                          e.target.checked ? [...language, lang] : language.filter(v => v !== lang)
                        )}
                      />
                      {lang.toUpperCase()}
                    </label>
                  ))}
                </div>
              </fieldset>
            </div>

            <p className="filter-section-label" style={{ marginTop: '1.5rem' }}>Refine</p>

            <div className="filter-group">
              <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="filter-label">Rating</legend>
                <div className="range-row">
                  <input
                    className="filter-input"
                    type="number" step="0.1"
                    aria-label="Minimum rating"
                    placeholder={filterOptions ? String(Math.floor(filterOptions.ratings.min)) : 'Min'}
                    min={filterOptions?.ratings.min ?? 0}
                    max={filterOptions?.ratings.max ?? 10}
                    value={ratings.min}
                    onChange={e => setRatings({ ...ratings, min: e.target.value })}
                  />
                  <span className="range-sep" aria-hidden="true">–</span>
                  <input
                    className="filter-input"
                    type="number" step="0.1"
                    aria-label="Maximum rating"
                    placeholder={filterOptions ? String(Math.ceil(filterOptions.ratings.max)) : 'Max'}
                    min={filterOptions?.ratings.min ?? 0}
                    max={filterOptions?.ratings.max ?? 10}
                    value={ratings.max}
                    onChange={e => setRatings({ ...ratings, max: e.target.value })}
                  />
                </div>
              </fieldset>
            </div>

            <div className="filter-group">
              <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
                <legend className="filter-label">Popularity</legend>
                <div className="pop-toggle" role="group">
                  {(['low', 'medium', 'high'] as const).map(val => (
                    <button
                      key={val}
                      className={`pop-btn${popularity === val ? ' pop-btn--active' : ''}`}
                      aria-pressed={popularity === val}
                      onClick={() => setPopularity(popularity === val ? '' : val)}
                    >
                      {val.charAt(0).toUpperCase() + val.slice(1)}
                    </button>
                  ))}
                </div>
              </fieldset>
            </div>

            <button className="find-btn" onClick={performSearch}>
              Find results
            </button>
          </aside>
        )}

        <main className="results-panel">
          <div className="search-row">
            <div className="search-box">
              {/* Wrap the icon in a button so it's keyboard-accessible */}
              <label htmlFor="search-input">Search for a TV show</label>
              <button
                className="search-icon-btn"
                aria-label="Search"
                onClick={performSearch}
                type="button"
              >
                <img
                  src={SearchIcon}
                  alt=""
                  aria-hidden="true"
                  className="search-icon"
                />
              </button>
              <input
                id="search-input"
                className="search-input"
                type="search"
                placeholder="e.g. dramatic survival show"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
              />
            </div>

            <button className="toggle-filters-btn" onClick={() => setFiltersOn(!filtersOn)}>
              {filtersOn ? 'Hide filters' : 'Show filters'}
            </button>

            <div className="search-type-toggle">
              {(['tfidf', 'svd'] as const).map(val => (
                <button
                  key={val}
                  className={`search-type-btn${searchType === val ? ' search-type-btn--active' : ''}`}
                  onClick={() => setSearchType(val)}
                >
                  {val.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {ragOverview && (
            <div className="ai-overview" role="region" aria-label="AI overview">
              <span className="ai-overview-label">AI overview</span>
              <div className="ai-overview-body">
                <MD>{ragOverview}</MD>
              </div>
            </div>
          )}

          {/* aria-live so screen readers announce result updates */}
          <div
            className="results-list"
            role="region"
            aria-label="Search results"
            aria-live="polite"
            aria-busy={loading}
          >
            {loading ? (
              <div className="loading-state" role="status" aria-label="Loading results">
                <div className="loading-dots" aria-hidden="true">
                  <span /><span /><span />
                </div>
                <p className="loading-text">Finding shows...</p>
              </div>
            ) : results.length === 0 ? (
              <div className="empty-state">
                <p className="empty-tagline">Find your next binge.</p>
                <p className="empty-hint">
                  Try searching something like{' '}
                  <span className="empty-example">"dramatic survival competition"</span>{' '}
                  or <span className="empty-example">"feel-good cooking show"</span>
                </p>
              </div>
            ) : (
              results.map((show, index) => (
                <div
                  key={`${show.title}-${index}`}
                  onClick={() => setSelectedShow(show)}
                  // Make the card keyboard-accessible if Result doesn't already handle this
                  role="button"
                  tabIndex={0}
                  aria-label={`View details for ${show.title}`}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setSelectedShow(show);
                    }
                  }}
                >
                  <Result
                    title={show.title}
                    year={parseInt(show.first_air_date?.split('-')[0]) || 0}
                    rating={show.rating}
                    similarity={parseFloat(show.score.toFixed(2))}
                    description={show.description}
                    tags={show.genre_ids?.map(id => GENRE_MAP[id] ?? `Genre ${id}`).filter(Boolean) ?? [show.language?.toUpperCase()]}
                    aiExplanation={show.llm_explanation}
                    dimensions={show.match_dimensions}
                  />
                </div>
              ))
            )}
          </div>
        </main>
      </div>

      <Modal show={selectedShow} onClose={() => setSelectedShow(null)} />
    </div>
  );
}