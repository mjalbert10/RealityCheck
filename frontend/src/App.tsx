import './App.css'
import Result from './components/result'
import SearchIcon from './assets/mag.png'

function App() {
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
        <div className="selection-area">
          <h2 className="titles">First the basics...</h2>

          {/* Subgenre */}
          <label>Type of Reality:</label>
          <select>
            <option value="">Select a subgenre</option>
            <option value="dating">Dating</option>
            <option value="survival">Survival</option>
            <option value="performance">Performance</option>
          </select>

          {/* Year Range */}
          <label>Release Year:</label>
          <div className="range-selection">
            <input type="number" placeholder="Start Year"  min="1900" max="2026"/>
            <span>to</span>
            <input type="number" placeholder="End Year" min="1900" max="2026"/>
          </div>

          {/* Language */}
          <label>Language:</label>
          <div className="checkbox-group">
            <label><input type="checkbox" value="en" /> English</label>
            <label><input type="checkbox" value="sp" /> Spanish</label>
            <label><input type="checkbox" value="ko" /> Korean</label>
            <label><input type="checkbox" value="hi" /> Hindi</label>
          </div>

          <h2 className="titles">Now some fun...</h2>

          {/* Ratings */}
          <label>Ratings:</label>
          <div className="range-selection">
            <input type="number" placeholder="Min" min="0" max="10" />
            <input type="number" placeholder="Max" min="0" max="10" />
          </div>

          {/* Popularity */}
          <label>People Traffic:</label>
          <div className="radio-group">
            <label><input type="radio" name="traffic" value="low" /> Low</label>
            <label><input type="radio" name="traffic" value="medium" /> Medium</label>
            <label><input type="radio" name="traffic" value="high" /> High</label>
          </div>

          {/* Button */}
          <button className="search-button">Find Results</button>
        </div>

        {/* Search and Results Area */}
        <div className="results-area">
          <div className="search-input">
            <img src={SearchIcon} alt="Search Icon" className="search-icon" />
            <input
              type="text"
              placeholder="e.g. dramatic survival show"
              className="search-bar"
            />
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

export default App