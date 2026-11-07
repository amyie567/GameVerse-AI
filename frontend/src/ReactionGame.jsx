import { useState, useEffect, useRef } from "react";
import "./ReactionGame.css";
import API from "./api";

function ReactionGame() {
  const [status, setStatus] = useState("waiting");
  const [reactionTime, setReactionTime] = useState(null);
  const [bestTime, setBestTime] = useState(null);
  const [message, setMessage] = useState("Press Start to play!");

  const timerRef = useRef(null);
  const startTimeRef = useRef(null);

  useEffect(() => {
    return () => clearTimeout(timerRef.current);
  }, []);

  function startGame() {
    clearTimeout(timerRef.current);

    setStatus("ready");
    setReactionTime(null);
    setMessage("Wait for GREEN...");

    const delay = Math.floor(Math.random() * 3000) + 2000;

    timerRef.current = setTimeout(() => {
      setStatus("go");
      setMessage("CLICK NOW!");
      startTimeRef.current = performance.now();
    }, delay);
  }

  function handleClick() {
    if (status === "waiting" || status === "finished") {
      return;
    }

    if (status === "ready") {
      clearTimeout(timerRef.current);
      setStatus("finished");
      setMessage("Too early! Try again.");
      return;
    }

    if (status === "go") {
      const time = Math.round(performance.now() - startTimeRef.current);

      setReactionTime(time);
      setBestTime((previous) =>
        previous === null ? time : Math.min(previous, time),
      );

      const earnedPoints =
        time < 250 ? 100 : time < 400 ? 75 : time < 600 ? 50 : 25;

      fetch(`${API}/api/profile/mini-game-points`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          points: earnedPoints,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Reaction Game points:", data);
        })
        .catch((error) => {
          console.error("Points update failed:", error);
        });

      setStatus("finished");
      setMessage(`Great reaction! You earned ${earnedPoints} points!`);
    }
  }

  function resetGame() {
    clearTimeout(timerRef.current);
    setStatus("waiting");
    setReactionTime(null);
    setMessage("Press Start to play!");
  }

  return (
    <section className="reaction-section">
      <div className="reaction-heading">
        <p className="eyebrow">GAMEVERSE ARCADE</p>
        <h2>Reaction Time Challenge</h2>
        <p>Test your reflexes. Click as quickly as you can!</p>
      </div>

      <div className="reaction-stats">
        <div className="reaction-stat">
          <strong>{reactionTime === null ? "--" : `${reactionTime} ms`}</strong>
          <small>Last Reaction</small>
        </div>

        <div className="reaction-stat">
          <strong>{bestTime === null ? "--" : `${bestTime} ms`}</strong>
          <small>Best Reaction</small>
        </div>
      </div>

      <button className={`reaction-box ${status}`} onClick={handleClick}>
        {status === "waiting" && "READY?"}
        {status === "ready" && "WAIT..."}
        {status === "go" && "CLICK!"}
        {status === "finished" && "FINISHED"}
      </button>

      <p className="reaction-message">{message}</p>

      <div className="reaction-actions">
        <button onClick={startGame}>START GAME</button>
        <button onClick={resetGame}>RESET</button>
      </div>
    </section>
  );
}

export default ReactionGame;
