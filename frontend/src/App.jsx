import ChatAssistant from "./ChatAssistant";
import RecommendationHistory from "./RecommendationHistory";
import Leaderboard from "./Leaderboard";
import ReactionGame from "./ReactionGame";
import MemoryGame from "./MemoryGame";
import { useEffect, useState } from "react";
import "./App.css";
import PlayerProfile from "./PlayerProfile";
import API from "./api";

const gameDescriptions = {
  "Neon Racer":
    "Race through futuristic neon cities, master high-speed tracks, and compete to become the ultimate racing champion.",

  "Shadow Quest":
    "Enter a mysterious fantasy world, explore dangerous lands, and uncover secrets hidden in the shadows.",

  "Cyber Chess":
    "Challenge your strategic thinking in a futuristic chess battlefield where every move matters.",

  "Battle Zone":
    "Enter intense combat arenas, defeat your opponents, and prove your skills in the ultimate battle.",

  "Galaxy Explorer":
    "Explore distant planets, discover mysterious galaxies, and experience an adventure beyond the stars.",

  "Speed Legends":
    "Push your racing skills to the limit with incredible speed, challenging tracks, and competitive races.",

  "Shadow Strike":
    "Become a stealth warrior, master your combat skills, and strike enemies from the shadows.",

  "Kingdom Tactics":
    "Build your kingdom, command powerful armies, and use smart strategies to conquer new territories.",
};
const gameArtwork = {
  "Neon Racer": "/images/games/neon-racer.jpg",
  "Shadow Quest": "/images/games/shadow-quest.jpg",
  "Cyber Chess": "/images/games/cyber-chess.jpg",
  "Battle Zone": "/images/games/battle-zone.jpg",
  "Galaxy Explorer": "/images/games/galaxy-explorer.jpg",
  "Speed Legends": "/images/games/speed-legends.jpg",
  "Shadow Strike": "/images/games/shadow-strike.jpg",
  "Kingdom Tactics": "/images/games/kingdom-tactics.jpg",
};
function App() {
  const [games, setGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [error, setError] = useState("");

  // AI recommendation states
  const [genre, setGenre] = useState("Any");
  const [difficulty, setDifficulty] = useState("Any");
  const [playStyle, setPlayStyle] = useState("Any");
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationMode, setRecommendationMode] = useState("ml");
  const [loading, setLoading] = useState(false);
  const [recommendationError, setRecommendationError] = useState("");

  // Load games from backend
  useEffect(() => {
    fetch(`${API}/api/games`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("API error");
        }
        return response.json();
      })
      .then((data) => {
        setGames(data.games || []);
        setError("");
      })
      .catch((err) => {
        console.error("Games loading error:", err);
        setError("Unable to load games. Check the backend.");
      });
  }, []);

  const categories = ["All", "Action", "Adventure", "Racing", "Strategy"];

  // Search and category filtering
  const filteredGames = games.filter((game) => {
    const matchesSearch = `${game.name} ${game.genre}`
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCategory = category === "All" || game.genre === category;

    return matchesSearch && matchesCategory;
  });

  // Request recommendations from FastAPI
  async function getRecommendations() {
    setLoading(true);
    setRecommendationError("");
    setRecommendations([]);

    try {
      const endpoint =
        recommendationMode === "ml"
          ? "/api/ml-recommendations"
          : "/api/recommendations";

      const response = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          genre,
          difficulty,
          play_style: playStyle,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      setRecommendations(
        Array.isArray(data) ? data : data.recommendations || [],
      );
    } catch (err) {
      console.error("Recommendation error:", err);
      setRecommendationError(
        "Unable to get recommendations. Please check your backend.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <nav className="navbar">
        <a className="logo" href="#">
          GAMEVERSE<span>AI</span>
        </a>

        <span className="nav-label">YOUR NEXT ADVENTURE STARTS HERE</span>

        <span className="online">● SYSTEM ONLINE</span>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="hero">
          <p className="eyebrow">THE FUTURE OF GAMING</p>

          <h1>
            PLAY BEYOND
            <br />
            <span>LIMITS.</span>
          </h1>

          <p className="intro">
            Discover your next favorite game. Your gaming universe starts here.
          </p>

          <a className="primary-btn" href="#games">
            EXPLORE GAMES ↗
          </a>
        </section>

        {/* AI Recommendation Section */}
        <section className="ai-section" id="recommendations">
          <div className="section-heading">
            <div>
              <p className="eyebrow">POWERED BY GAMEVERSE AI</p>

              <h2>Find Your Perfect Game</h2>
            </div>

            <span className="ai-tag">✦ AI ENGINE</span>
          </div>

          <p className="ai-description">
            Tell us how you like to play. Our recommendation engine will find
            games that match your preferences.
          </p>

          <div className="mode-selector">
            <label htmlFor="recommendationMode">
              Choose Recommendation Engine
            </label>

            <select
              id="recommendationMode"
              value={recommendationMode}
              onChange={(e) => setRecommendationMode(e.target.value)}
            >
              <option value="ml">Machine Learning AI</option>

              <option value="rule">Rule-Based AI</option>
            </select>
          </div>

          <div className="preference-grid">
            <div className="preference-field">
              <label htmlFor="genre">Favorite Genre</label>

              <select
                id="genre"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
              >
                <option value="Any">Any Genre</option>
                <option value="Action">Action</option>
                <option value="Adventure">Adventure</option>
                <option value="Racing">Racing</option>
                <option value="Strategy">Strategy</option>
              </select>
            </div>

            <div className="preference-field">
              <label htmlFor="difficulty">Preferred Difficulty</label>

              <select
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="Any">Any Difficulty</option>
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>

            <div className="preference-field">
              <label htmlFor="playStyle">Your Play Style</label>

              <select
                id="playStyle"
                value={playStyle}
                onChange={(e) => setPlayStyle(e.target.value)}
              >
                <option value="Any">Any Play Style</option>
                <option value="Competitive">Competitive</option>
                <option value="Exploration">Exploration</option>
                <option value="Strategic">Strategic</option>
              </select>
            </div>
          </div>

          <button
            className="recommend-btn"
            onClick={getRecommendations}
            disabled={loading}
          >
            {loading ? "FINDING YOUR GAMES..." : "✦ GET AI RECOMMENDATIONS"}
          </button>

          {recommendationError && (
            <p className="error">{recommendationError}</p>
          )}

          {recommendations.length > 0 && (
            <div className="recommendation-results">
              <h3>Your Personalized Recommendations</h3>

              <div className="recommendation-grid">
                {recommendations.map((game) => (
                  <article className="recommendation-card" key={game.id}>
                    <div className="recommendation-top">
                      <span className="genre">{game.genre}</span>

                      <strong>{game.match_percentage}% MATCH</strong>
                    </div>

                    <h3>{game.name}</h3>

                    <div className="match-track">
                      <div
                        className="match-fill"
                        style={{
                          width: `${game.match_percentage}%`,
                        }}
                      />
                    </div>

                    <p className="difficulty">Difficulty: {game.difficulty}</p>

                    {recommendationMode === "ml" && (
                      <div className="score-breakdown">
                        <h4>AI Score Breakdown</h4>

                        <div className="score-item">
                          <span>TF-IDF Similarity</span>
                          <strong>{game.similarity_score}%</strong>
                        </div>

                        <div className="score-item">
                          <span>Preference Match</span>
                          <strong>{game.preference_score}%</strong>
                        </div>

                        <div className="score-item final-score">
                          <span>Final Hybrid Score</span>
                          <strong>{game.match_percentage}%</strong>
                        </div>
                      </div>
                    )}

                    <div className="match-reasons">
                      {recommendationMode === "ml" ? (
                        <p>✓ {game.recommendation_reason}</p>
                      ) : game.reasons?.length > 0 ? (
                        game.reasons.map((reason, index) => (
                          <p key={index}>✓ {reason}</p>
                        ))
                      ) : (
                        <p>Available for your gaming preferences.</p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Player Features */}
        <PlayerProfile />
        <Leaderboard />
        <ChatAssistant />
        <RecommendationHistory />
        <MemoryGame />
        <ReactionGame />

        {/* Game Library */}
        <section className="library" id="games">
          <div className="section-heading">
            <div>
              <p className="eyebrow">YOUR UNIVERSE</p>

              <h2>Explore Games</h2>
            </div>

            <span className="game-count">{filteredGames.length} GAMES</span>
          </div>

          <input
            className="search"
            type="search"
            placeholder="Search games or genres..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <div className="categories">
            {categories.map((item) => (
              <button
                key={item}
                className={
                  category === item ? "category-btn active" : "category-btn"
                }
                onClick={() => setCategory(item)}
              >
                {item}
              </button>
            ))}
          </div>

          {error && <p className="error">{error}</p>}

          <div className="game-grid">
            {filteredGames.map((game) => {
              const genre = game.genre || "Game";
              const difficulty = game.difficulty || "Unknown";

              const genreKey = genre.toLowerCase().replace(/\s+/g, "-");
              const gameKey = game.name
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, "-")
                .replace(/^-|-$/g, "");

              const gameIcons = {
                "Neon Racer": "🏎️",
                "Shadow Quest": "🗡️",
                "Cyber Chess": "♟️",
                "Battle Zone": "💥",
                "Galaxy Explorer": "🚀",
                "Speed Legends": "🏁",
                "Shadow Strike": "🥷",
                "Kingdom Tactics": "🏰",
              };

              const gameSymbol = gameIcons[game.name] || "🎮";

              return (
                <article
                  className="game-card game-card--enhanced"
                  key={game.id}
                  onClick={() => setSelectedGame(game)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      setSelectedGame(game);
                    }
                  }}
                >
                  <div
                    className={`game-card__art game-card__art--${genreKey} game-card__art--${gameKey}`}
                    style={{
                      backgroundImage: `linear-gradient(to top, rgba(5, 3, 15, 0.85), rgba(5, 3, 15, 0.05)), url("${gameArtwork[game.name]}")`,
                      backgroundSize: "cover",
                      backgroundPosition: "center",
                    }}
                  >
                    <span className="game-card__index">
                      {String(game.id).padStart(2, "0")}
                    </span>

                    <span className="game-card__symbol">{gameSymbol}</span>

                    <span className="game-card__art-label">
                      GAMEVERSE ORIGINAL
                    </span>
                  </div>

                  <div className="game-card__content">
                    <div className="game-card__meta">
                      <span className="game-card__genre">{genre}</span>

                      <span
                        className={`game-card__difficulty game-card__difficulty--${difficulty.toLowerCase()}`}
                      >
                        {difficulty}
                      </span>
                    </div>

                    <h3>{game.name}</h3>

                    <p className="game-card__playstyle">
                      {game.play_style || "Flexible"} play style
                    </p>
                  </div>
                </article>
              );
            })}
          </div>

          {filteredGames.length === 0 && !error && (
            <p className="empty">
              No games found. Try another category or search.
            </p>
          )}
        </section>
      </main>
      {/* GAME DETAILS POPUP */}
      {selectedGame && (
        <div
          className="game-modal-overlay"
          onClick={() => setSelectedGame(null)}
        >
          <section
            className="game-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="game-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="game-modal-close"
              onClick={() => setSelectedGame(null)}
              aria-label="Close game details"
            >
              ×
            </button>

            <div
              className="game-modal-art"
              style={{
                backgroundImage: `linear-gradient(to top, rgba(5, 3, 15, 0.75), rgba(5, 3, 15, 0.05)), url("${gameArtwork[selectedGame.name]}")`,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }}
            >
              <span className="game-modal-label">GAMEVERSE ORIGINAL</span>
            </div>

            <div className="game-modal-content">
              <p className="game-modal-eyebrow">✦ GAME DETAILS</p>

              <h2 id="game-modal-title">{selectedGame.name}</h2>

              <p className="game-modal-description">
                {gameDescriptions[selectedGame.name] ||
                  "Discover a new gaming experience in GameVerse AI."}
              </p>

              <div className="game-modal-stats">
                <div>
                  <span>GENRE</span>
                  <strong>{selectedGame.genre}</strong>
                </div>

                <div>
                  <span>DIFFICULTY</span>
                  <strong>{selectedGame.difficulty}</strong>
                </div>

                <div>
                  <span>PLAY STYLE</span>
                  <strong>{selectedGame.play_style}</strong>
                </div>
              </div>

              <button
                className="game-modal-button"
                onClick={() => setSelectedGame(null)}
              >
                CLOSE DETAILS
                <span>↗</span>
              </button>
            </div>
          </section>
        </div>
      )}
      <footer>
        GAMEVERSE AI <span>— LEVEL UP YOUR EXPERIENCE.</span>
      </footer>
    </div>
  );
}

export default App;
