import React, { useState } from "react";
import "./App.css";
import { parseWebsite } from "./api";

function App() {
  const [ingredients, setIngredients] = useState([]);
  const [steps, setSteps] = useState([]);
  const [author, setAuthor] = useState("");
  const [loading, setLoading] = useState(false);
  const [url, setUrl] = useState("");

  const handleParse = async () => {
    if (!url.trim()) return alert("Please enter a URL");
    setLoading(true);
    try {
      const data = await parseWebsite(url);
      setIngredients(data.ingredients || []);
      setSteps(data.steps || []);
      setAuthor(data.author || "");
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Recipe Reformat</h1>
      </header>

      <div className="input-section">
        <input
          className="url-input"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="Paste recipe URL here..."
        />
        <button
          className="parse-button"
          onClick={handleParse}
          disabled={loading}
        >
          {loading ? "Parsing..." : "Parse Recipe"}
        </button>
      </div>

      <div className="panels">
        <Panel title="Ingredients">
          {ingredients.length ? (
            <ul className="checklist">
              {ingredients.map((item, i) => (
                <li key={i}>
                  <label>
                    <input type="checkbox" />
                    <span>{item}</span>
                  </label>
                </li>
              ))}
            </ul>
          ) : (
            <p className="placeholder">No ingredients loaded</p>
          )}
        </Panel>

        <Panel title="Steps">
          {steps.length ? (
            <ol>
              {steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          ) : (
            <p className="placeholder">No steps loaded</p>
          )}
        </Panel>

        <Panel title="Author">
          <p>{author || <span className="placeholder">Unknown</span>}</p>
        </Panel>
      </div>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      <div className="panel-content">{children}</div>
    </div>
  );
}

export default App;
