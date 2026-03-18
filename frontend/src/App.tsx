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
          <h2>First the basics...</h2>

          {/* Subgenre */}
          <label>Type of Reality:</label>
          <select>
            <option value="">Select a subgenre</option>
            <option value="dating">Dating</option>
            <option value="survival">Survival</option>
            <option value="performance">Performance</option>
          </select>

          {/* Year Range */}
          <label>Year Range:</label>
          <div className="range-selection">
            <input type="number" placeholder="Start Year" />
            <span>to</span>
            <input type="number" placeholder="End Year" />
          </div>

          {/* Language */}
          <label>Language:</label>
          <div className="checkbox-group">
            <label><input type="checkbox" value="en" /> English</label>
            <label><input type="checkbox" value="sp" /> Spanish</label>
            <label><input type="checkbox" value="ko" /> Korean</label>
            <label><input type="checkbox" value="hi" /> Hindi</label>
          </div>

          <h2>Now some fun...</h2>

          {/* Ratings */}
          <label>Ratings:</label>
          <div className="range-selection">
            <input type="number" placeholder="Min" />
            <input type="number" placeholder="Max" />
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
            />
          </div>

          <h2>Search Results</h2>

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