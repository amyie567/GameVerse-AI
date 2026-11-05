import { useEffect, useState } from "react";
import "./RecommendationHistory.css";

function RecommendationHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadHistory() {
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/recommendation-history",
      );

      if (!response.ok) {
        throw new Error("Could not load history");
      }

      const data = await response.json();
      setHistory(data.history || []);
    } catch (error) {
      console.error("History error:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <section className="history-section">
      <div className="history-heading">
        <p className="eyebrow">YOUR GAMING JOURNEY</p>
        <h2>Recommendation History</h2>
        <p>Explore your previous AI game recommendations.</p>

        <button onClick={loadHistory} disabled={loading}>
          {loading ? "Loading..." : "Refresh History"}
        </button>
      </div>

      {loading ? (
        <p>Loading recommendation history...</p>
      ) : history.length === 0 ? (
        <p className="empty-history">
          No recommendation history yet. Try the AI recommender first!
        </p>
      ) : (
        <div className="history-list">
          {history.map((item, index) => (
            <article className="history-card" key={index}>
              <div className="history-preferences">
                <span>Genre: {item.genre}</span>
                <span>Difficulty: {item.difficulty}</span>
                <span>Play Style: {item.play_style}</span>
              </div>

              <h3>Recommended Games</h3>

              {item.recommendations.map((game, gameIndex) => (
                <div className="history-game" key={gameIndex}>
                  <span>{game.name}</span>
                  <strong>{game.match_percentage}% MATCH</strong>
                </div>
              ))}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default RecommendationHistory;
