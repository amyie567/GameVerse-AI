import { useEffect, useState } from "react";
import "./RecommendationHistory.css";

function RecommendationHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch recommendation history from the backend
  async function fetchHistory() {
    const response = await fetch(
      "http://127.0.0.1:8000/api/recommendation-history",
    );

    if (!response.ok) {
      throw new Error("Could not load history");
    }

    return response.json();
  }

  // Load history when the component first appears
  useEffect(() => {
    let cancelled = false;

    async function loadInitialHistory() {
      try {
        const data = await fetchHistory();

        if (!cancelled) {
          setHistory(data.history || []);
        }
      } catch (error) {
        console.error("History error:", error);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadInitialHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  // Refresh history when the button is clicked
  async function handleRefresh() {
    setLoading(true);

    try {
      const data = await fetchHistory();
      setHistory(data.history || []);
    } catch (error) {
      console.error("History error:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="history-section">
      <div className="history-heading">
        <p className="eyebrow">YOUR GAMING JOURNEY</p>
        <h2>Recommendation History</h2>
        <p>Explore your previous AI game recommendations.</p>

        <button onClick={handleRefresh} disabled={loading}>
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
