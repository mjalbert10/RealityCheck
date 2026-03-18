import './App.css'
import { useState } from 'react'
import Result from './components/result'
import SearchIcon from './assets/mag.png'

export default function App() {
  const [filtersOn, setFiltersOn] = useState(false);

  const toggleFilters = () => {
    setFiltersOn(!filtersOn);
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
        {/* Filter area */}
        {filtersOn && (
        <div className="filter-area">
          <div className="selection-area">
            <h2 className="titles">First the basics...</h2>

            {/* Subgenre */}
            <label>Type of Reality:</label>
            <select>
              <option className="placeholder" value="" disabled hidden>Select a subgenre</option>
              <option value="dating">Dating</option>
              <option value="survival">Survival</option>
              <option value="performance">Performance</option>
            </select>

            {/* Year Range */}
            <label>Release Year:</label>
            <div className="range-selection">
              <input type="number" placeholder="Start"  min="1900" max="2026"/>
              <span>to</span>
              <input type="number" placeholder="End" min="1900" max="2026"/>
            </div>

            {/* Language */}
            <label>Language:</label>
            <div className="checkbox-group">
              <label className="options"><input type="checkbox" value="en" /> English</label>
              <label className="options"><input type="checkbox" value="sp" /> Spanish</label>
              <label className="options"><input type="checkbox" value="ko" /> Korean</label>
              <label className="options"><input type="checkbox" value="hi" /> Hindi</label>
            </div>

            <h2 className="titles">Now some fun...</h2>

            {/* Ratings */}
            <label>Ratings:</label>
            <div className="range-selection">
              <input type="number" placeholder="Min" min="0" max="10" />
              <p>to</p>
              <input type="number" placeholder="Max" min="0" max="10" />
            </div>

            {/* Popularity */}
            <label>People Traffic:</label>
            <div className="radio-group">
              <label className="options"><input type="radio" name="traffic" value="low" /> Low</label>
              <label className="options"><input type="radio" name="traffic" value="medium" /> Medium</label>
              <label className="options"><input type="radio" name="traffic" value="high" /> High</label>
            </div>

            {/* Button */}
            <button className="search-button">Find Results</button>
          </div>
        </div>
        )}

        {/* Search and Results Area */}
        <div className="results-area">
          <h1>Search For a Show</h1>
          <div className="search-input">
            <img src={SearchIcon} alt="Search Icon" className="search-icon" />
            <input
              type="text"
              placeholder="e.g. dramatic survival show"
              className="search-bar"
            />
          </div>

          <div className="similarity-toggle">
            <button className="filter-button" onClick={toggleFilters}>
              {filtersOn ? 'Hide Filters' : 'Show Filters'}
            </button>
            <h3> Similarity Function: </h3>
            <div className="radio-group">
              <label className="options"><input type="radio" name="sim-function" value="cosine" /> Cosine</label>
              <label className="options"><input type="radio" name="sim-function" value="tfidf" /> TF-IDF</label>
              <label className="options"><input type="radio" name="sim-function" value="svd" /> SVD</label>
            </div>
          </div>

          <h2 className="titles">Search Results</h2>

          <div className="results-list">
            <Result
              title="Survivor"
              year={2000}
              rating={8.0}
              similarity={0.95}
              description="A group of strangers are stranded in a remote location and must work together to survive while competing in challenges."
              tags={['Survival', 'Adventure', 'Competition']}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
