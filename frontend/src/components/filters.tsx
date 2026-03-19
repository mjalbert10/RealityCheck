function Filters() {
    return (
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
    )
}

export default Filters