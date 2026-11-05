import { useState, useEffect } from "react";
import "./MemoryGame.css";

const SYMBOLS = ["🎮", "🚀", "⚡", "👾", "🏆", "🎯", "🔥", "💎"];

function createCards() {
  return [...SYMBOLS, ...SYMBOLS]
    .map((symbol, index) => ({
      id: index,
      symbol,
      matched: false,
    }))
    .sort(() => Math.random() - 0.5);
}

function MemoryGame() {
  const [cards, setCards] = useState(createCards);
  const [flipped, setFlipped] = useState([]);
  const [moves, setMoves] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [started, setStarted] = useState(false);
  const [locked, setLocked] = useState(false);

  const gameWon = cards.every((card) => card.matched);
  const [pointsAwarded, setPointsAwarded] = useState(false);

  useEffect(() => {
    if (!started || gameWon) return;

    const timer = setInterval(() => {
      setSeconds((previous) => previous + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [started, gameWon]);
  useEffect(() => {
    if (!gameWon || pointsAwarded) return;

    setPointsAwarded(true);

    fetch("http://127.0.0.1:8000/api/profile/mini-game-points", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        points: 100,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Memory Match points:", data);
      })
      .catch((error) => {
        console.error("Points update failed:", error);
      });
  }, [gameWon, pointsAwarded]);

  function flipCard(card) {
    if (locked || card.matched || flipped.includes(card.id)) {
      return;
    }

    setStarted(true);

    if (flipped.length === 1) {
      setMoves((previous) => previous + 1);
      setLocked(true);

      const firstCard = cards.find((item) => item.id === flipped[0]);

      if (firstCard.symbol === card.symbol) {
        setCards((previous) =>
          previous.map((item) =>
            item.id === card.id || item.id === firstCard.id
              ? { ...item, matched: true }
              : item,
          ),
        );

        setFlipped([]);
        setLocked(false);
      } else {
        setFlipped((previous) => [...previous, card.id]);

        setTimeout(() => {
          setFlipped([]);
          setLocked(false);
        }, 800);
      }
    } else {
      setFlipped([card.id]);
    }
  }

  function restartGame() {
    setCards(createCards());
    setFlipped([]);
    setMoves(0);
    setSeconds(0);
    setStarted(false);
    setLocked(false);
    setPointsAwarded(false);
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return (
    <section className="memory-section">
      <div className="memory-heading">
        <p className="eyebrow">GAMEVERSE ARCADE</p>
        <h2>Memory Match</h2>
        <p>Flip the cards and find all 8 matching pairs. Test your memory!</p>
      </div>

      <div className="memory-stats">
        <div className="memory-stat">
          <span>🎯</span>
          <strong>{moves}</strong>
          <small>Moves</small>
        </div>

        <div className="memory-stat">
          <span>⏱️</span>
          <strong>
            {minutes}:{String(remainingSeconds).padStart(2, "0")}
          </strong>
          <small>Time</small>
        </div>

        <div className="memory-stat">
          <span>🏆</span>
          <strong>{cards.filter((card) => card.matched).length / 2}</strong>
          <small>Pairs Found</small>
        </div>
      </div>

      <div className="memory-grid">
        {cards.map((card) => {
          const isVisible = flipped.includes(card.id) || card.matched;

          return (
            <button
              key={card.id}
              className={`memory-card ${
                isVisible ? "flipped" : ""
              } ${card.matched ? "matched" : ""}`}
              onClick={() => flipCard(card)}
              disabled={card.matched || locked}
              aria-label={isVisible ? card.symbol : "Hidden card"}
            >
              {isVisible ? card.symbol : "?"}
            </button>
          );
        })}
      </div>

      {gameWon && (
        <div className="memory-win">
          <h3>🎉 YOU WON!</h3>
          <p>
            You found all pairs in {moves} moves and {minutes}:
            {String(remainingSeconds).padStart(2, "0")}.
          </p>
        </div>
      )}

      <button className="memory-restart" onClick={restartGame}>
        ↻ RESTART GAME
      </button>
    </section>
  );
}

export default MemoryGame;
