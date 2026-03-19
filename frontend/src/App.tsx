import './App.css'
import { useState, useEffect } from 'react'
import Result from './components/result'
import SearchIcon from './assets/mag.png'

export default function App() {
  // Filter menu visibility
  const [filtersOn, setFiltersOn] = useState(false);

  // Search and results states
  const [simModel, setSimModel] = useState('');
  const [results, setResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Additional filters states
  const [subgenre, setSubgenre] = useState('');
  const [yearRange, setYearRange] = useState({ start: '', end: '' });
  const [language, setLanguage] = useState<string[]>([]);
  const [ratings, setRatings] = useState({ min: '', max: '' });
  const [popularity, setPopularity] = useState('');

  useEffect(() => {
    // Placeholder for fetching results based on searchQuery and filters
    // This is where you would make an API call to your backend with the search parameters
    console.log('Search Query:', searchQuery);
    console.log('Selected Similarity Model:', simModel);
    console.log('Subgenre:', subgenre);
    console.log('Year Range:', yearRange);
    console.log('Language:', language);
    console.log('Ratings:', ratings);
    console.log('Popularity:', popularity);
    
  }, [searchQuery, simModel, subgenre, yearRange, language, ratings, popularity]);


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
            <select onChange={(e) => setSubgenre(e.target.value)}>
              <option className="placeholder" value="" disabled selected>Select a subgenre</option>
              <option value="dating">Dating</option>
              <option value="survival">Survival</option>
              <option value="performance">Performance</option>
            </select>

            {/* Year Range */}
            <label>Release Year:</label>
            <div className="range-selection">
              <input type="number" placeholder="Start"  min="1900" max="2026" onChange={(e) => setYearRange({...yearRange, start: e.target.value})}/>
              <span>to</span>
              <input type="number" placeholder="End" min="1900" max="2026" onChange={(e) => setYearRange({...yearRange, end: e.target.value})}/>
            </div>

            {/* Language */}
            <label>Language:</label>
            <div className="checkbox-group">
              <label className="options" ><input type="checkbox" value="en" onChange={(e) => {
                if (e.target.checked) {
                  setLanguage([...language, e.target.value]);
                } else {
                  setLanguage(language.filter((v) => v !== e.target.value));
                }
              }} /> English</label>
              <label className="options"><input type="checkbox" value="sp" onChange={(e) => {
                if (e.target.checked) {
                  setLanguage([...language, e.target.value]);
                } else {
                  setLanguage(language.filter((v) => v !== e.target.value));
                }
              }} /> Spanish</label>
              <label className="options"><input type="checkbox" value="ko" onChange={(e) => {
                if (e.target.checked) {
                  setLanguage([...language, e.target.value]);
                } else {
                  setLanguage(language.filter((v) => v !== e.target.value));
                }
              }} /> Korean</label>
              <label className="options"><input type="checkbox" value="hi" onChange={(e) => {
                if (e.target.checked) {
                  setLanguage([...language, e.target.value]);
                } else {
                  setLanguage(language.filter((v) => v !== e.target.value));
                }
              }} /> Hindi</label>
            </div>

            <h2 className="titles">Now some fun...</h2>

            {/* Ratings */}
            <label>Ratings:</label>
            <div className="range-selection">
              <input type="number" placeholder="Min" min="0" max="10" onChange={(e) => setRatings({...ratings, min: e.target.value})}/>
              <p>to</p>
              <input type="number" placeholder="Max" min="0" max="10" onChange={(e) => setRatings({...ratings, max: e.target.value})}/>
            </div>

            {/* Popularity */}
            <label>People Traffic:</label>
            <div className="radio-group">
              <label className="options"><input type="radio" name="traffic" value="low" onChange={(e) => setPopularity(e.target.value)} /> Low</label>
              <label className="options"><input type="radio" name="traffic" value="medium" onChange={(e) => setPopularity(e.target.value)} /> Medium</label>
              <label className="options"><input type="radio" name="traffic" value="high" onChange={(e) => setPopularity(e.target.value)} /> High</label>
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
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="similarity-toggle">
            <button className="filter-button" onClick={toggleFilters}>
              {filtersOn ? 'Hide Filters' : 'Show Filters'}
            </button>
            <h3> Similarity Function: </h3>
            <div className="radio-group">
              <label className="options"><input type="radio" name="sim-function" value="cosine" onChange={(e) => setSimModel(e.target.value)} /> Cosine</label>
              <label className="options"><input type="radio" name="sim-function" value="tfidf" onChange={(e) => setSimModel(e.target.value)} /> TF-IDF</label>
              <label className="options"><input type="radio" name="sim-function" value="svd" onChange={(e) => setSimModel(e.target.value)} /> SVD</label>
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
