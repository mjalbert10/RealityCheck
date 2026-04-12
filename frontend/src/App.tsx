import './App.css'
import { useState, useEffect } from 'react'
import Result from './components/result'
import SearchIcon from './assets/mag.png'

const GENRE_MAP: Record<number, string> = {
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
};

interface ShowResult {
  title: string;
  description: string;
  language: string;
  popularity: number;
  rating: number;
  first_air_date: string;
  score: number;
  genre_ids: number[];
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
  const [searchQuery, setSearchQuery] = useState('');
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);

  // Filter states
  const [subgenre, setSubgenre] = useState('');
  const [yearRange, setYearRange] = useState({ start: '', end: '' });
  const [language, setLanguage] = useState<string[]>([]);
  const [ratings, setRatings] = useState({ min: '', max: '' });
  const [popularity, setPopularity] = useState('');

  // Fetch available filter options on mount
  useEffect(() => {
    fetch('/api/filters')
      .then((res) => res.json())
      .then((data) => setFilterOptions(data))
      .catch((err) => console.error('Failed to load filters:', err));
  }, []);

  const toggleFilters = () => setFiltersOn(!filtersOn);

  // Set search on keystroke or button click
  const performSearch = () => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }
  
    const params = new URLSearchParams({
      q: searchQuery,
      ...(subgenre && { subgenre }),
      ...(yearRange.start && { year_start: yearRange.start }),
      ...(yearRange.end && { year_end: yearRange.end }),
      ...(language.length > 0 && { language: language.join(',') }),
      ...(ratings.min && { rating_min: ratings.min }),
      ...(ratings.max && { rating_max: ratings.max }),
      ...(popularity && { popularity }),
    });

    fetch(`/api/search?${params}`)
      .then((res) => res.json())
      .then((data) => {
        console.log('Results:', data.map((s: ShowResult) => s.title));
        setResults(data);
      })
      .catch((err) => console.error('Search failed:', err));
    };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      performSearch();
    }
  };

  return (
    <div className="App">
      <header>
        <div>
          <h1>RealityCheck</h1>
        </div>
        <p>
          Keeping the TV show search <span className="emphasis">REAL</span>
        </p>
      </header>

      <div className="main-content">
        {filtersOn && (
          <div className="filter-area">
            <div className="selection-area">
              <h2 className="titles">First the basics...</h2>

              {/* Subgenre — dynamic from API */}
              <label>Type of Reality:</label>
              <select onChange={(e) => setSubgenre(e.target.value)}>
                <option value="">All Genres</option>
                {filterOptions?.genre_ids.map((id) => (
                  <option key={id} value={String(id)}>
                    {GENRE_MAP[id] ?? `Genre ${id}`}
                  </option>
                ))}
              </select>

              {/* Year Range — min/max from API */}
              <label>Release Year:</label>
              <div className="range-selection">
                <input
                  type="number"
                  placeholder={filterOptions?.years.min ?? 'Start'}
                  min={filterOptions?.years.min ?? '1900'}
                  max={filterOptions?.years.max ?? '2026'}
                  onChange={(e) => setYearRange({ ...yearRange, start: e.target.value })}
                />
                <span>to</span>
                <input
                  type="number"
                  placeholder={filterOptions?.years.max ?? 'End'}
                  min={filterOptions?.years.min ?? '1900'}
                  max={filterOptions?.years.max ?? '2026'}
                  onChange={(e) => setYearRange({ ...yearRange, end: e.target.value })}
                />
              </div>

              {/* Language — dynamic from API */}
              <label>Language:</label>
              <div className="checkbox-group">
                {filterOptions?.languages.map((lang) => (
                  <label key={lang} className="options">
                    <input
                      type="checkbox"
                      value={lang}
                      onChange={(e) => {
                        setLanguage(e.target.checked
                          ? [...language, lang]
                          : language.filter((v) => v !== lang)
                        );
                      }}
                    />
                    {' '}{lang.toUpperCase()}
                  </label>
                ))}
              </div>

              <h2 className="titles">Now some fun...</h2>

              {/* Ratings — min/max from API */}
              <label>Ratings:</label>
              <div className="range-selection">
                <input
                  type="number"
                  placeholder={filterOptions ? String(Math.floor(filterOptions.ratings.min)) : 'Min'}
                  min={filterOptions?.ratings.min ?? 0}
                  max={filterOptions?.ratings.max ?? 10}
                  step="0.1"
                  onChange={(e) => setRatings({ ...ratings, min: e.target.value })}
                />
                <p>to</p>
                <input
                  type="number"
                  placeholder={filterOptions ? String(Math.ceil(filterOptions.ratings.max)) : 'Max'}
                  min={filterOptions?.ratings.min ?? 0}
                  max={filterOptions?.ratings.max ?? 10}
                  step="0.1"
                  onChange={(e) => setRatings({ ...ratings, max: e.target.value })}
                />
              </div>

              {/* Popularity */}
              <label>People Traffic:</label>
              <div className="radio-group">
                {['low', 'medium', 'high'].map((val) => (
                  <label key={val} className="options">
                    <input
                      type="radio"
                      name="traffic"
                      value={val}
                      onChange={(e) => setPopularity(e.target.value)}
                    />
                    {' '}{val.charAt(0).toUpperCase() + val.slice(1)}
                  </label>
                ))}
              </div>

              <button className="search-button" onClick={performSearch}>Find Results</button>
            </div>
          </div>
        )}

        <div className="results-area">
          <h1>Search For a Show</h1>
          <div className="search-input">
            <img 
              src={SearchIcon} 
              alt="Search Icon" 
              className="search-icon" 
              onClick={performSearch}
              style={{ cursor: 'pointer' }} 
            />
            <input
              type="text"
              placeholder="e.g. dramatic survival show"
              className="search-bar"
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyPress}
            />
          </div>

          <div className="similarity-toggle">
            <button className="filter-button" onClick={toggleFilters}>
              {filtersOn ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>

          <h2 className="titles">Search Results</h2>

          <div className="results-list">
            {results.length === 0 ? (
              <p>No results yet — try searching above!</p>
            ) : (
              results.map((show, index) => (
                <Result
                  key={`${show.title}-${index}`}
                  title={show.title}
                  year={parseInt(show.first_air_date?.split('-')[0]) || 0}
                  rating={show.rating}
                  similarity={parseFloat(show.score.toFixed(2))}
                  description={show.description}
                  tags={show.genre_ids?.map((id) => GENRE_MAP[id] ?? `Genre ${id}`).filter(Boolean) ?? [show.language?.toUpperCase()]}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}