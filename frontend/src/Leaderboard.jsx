import { useEffect, useState } from "react";
import "./Leaderboard.css";

function Leaderboard() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadLeaderboard() {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/leaderboard");

        if (!response.ok) {
          throw new Error("Unable to load leaderboard");
        }

        const data = await response.json();
        setPlayers(data);
      } catch {
        setError("Could not connect to the leaderboard.");
      } finally {
        setLoading(false);
      }
    }

    loadLeaderboard();
    const interval = setInterval(loadLeaderboard, 5000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <section className="leaderboard-section">Loading leaderboard...</section>
    );
  }

  if (error) {
    return <section className="leaderboard-section">{error}</section>;
  }

  return (
    <section className="leaderboard-section">
      <div className="leaderboard-heading">
        <p className="eyebrow">GLOBAL RANKINGS</p>
        <h2>🏆 Leaderboard</h2>
        <p>Compete with the best players in GameVerse AI.</p>
      </div>

      <div className="leaderboard-table">
        <div className="leaderboard-row leaderboard-header">
          <span>RANK</span>
          <span>PLAYER</span>
          <span>POINTS</span>
        </div>

        {players.map((player, index) => (
          <div
            className={`leaderboard-row ${
              player.username === "CyberGamer" ? "current-player" : ""
            }`}
            key={player.username}
          >
            <span className="player-rank">
              {index === 0
                ? "🥇"
                : index === 1
                  ? "🥈"
                  : index === 2
                    ? "🥉"
                    : `#${index + 1}`}
            </span>

            <span className="player-name">
              {player.username}

              {player.username === "CyberGamer" && (
                <span className="you-badge">YOU</span>
              )}
            </span>

            <span className="player-points">
              {player.points.toLocaleString()} ⭐
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Leaderboard;
