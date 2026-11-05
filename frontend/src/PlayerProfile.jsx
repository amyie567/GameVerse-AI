import { useEffect, useState } from "react";
import "./PlayerProfile.css";

const API = "http://127.0.0.1:8000";

function PlayerProfile() {
  const [profile, setProfile] = useState(null);
  const [newUsername, setNewUsername] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Load saved profile from Python backend
  async function loadProfile() {
    try {
      setError("");
      const response = await fetch(`${API}/api/profile`);

      if (!response.ok) {
        throw new Error("Unable to load profile");
      }

      const data = await response.json();

      setProfile(data);
      setNewUsername(data.username);
    } catch (err) {
      setError("Could not connect to the profile server.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  // Update profile through backend
  async function updateProfile(event) {
    event.preventDefault();
    setMessage("");

    if (!newUsername.trim()) {
      setMessage("Please enter a username.");
      return;
    }

    try {
      const response = await fetch(`${API}/api/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: newUsername.trim(),
          favorite_genre: profile.favorite_genre,
        }),
      });

      if (!response.ok) {
        throw new Error("Update failed");
      }

      const data = await response.json();

      setProfile(data.profile);
      setNewUsername(data.profile.username);
      setMessage(data.message);
    } catch (err) {
      setMessage("Unable to update profile. Try again.");
    }
  }

  // Update favorite genre through backend
  async function updateGenre(value) {
    try {
      const response = await fetch(`${API}/api/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: profile.username,
          favorite_genre: value,
        }),
      });

      if (!response.ok) {
        throw new Error("Update failed");
      }

      const data = await response.json();
      setProfile(data.profile);
      setMessage(data.message);
    } catch (err) {
      setMessage("Unable to update genre.");
    }
  }

  // Unlock achievement through backend
  async function unlockAchievement() {
    try {
      const response = await fetch(`${API}/api/profile/achievement`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Achievement update failed");
      }

      const data = await response.json();

      setProfile(data.profile);
      setMessage(data.message);
    } catch (err) {
      setMessage("Unable to unlock achievement.");
    }
  }

  if (loading) {
    return <section className="profile-section">Loading profile...</section>;
  }

  if (error) {
    return <section className="profile-section error">{error}</section>;
  }

  if (!profile) return null;

  return (
    <section className="profile-section">
      <div className="profile-heading">
        <p className="eyebrow">PLAYER CENTER</p>
        <h2>Your Gaming Profile</h2>
      </div>

      <div className="profile-card">
        <div className="profile-avatar">🎮</div>

        <div className="profile-details">
          <p className="profile-label">PLAYER PROFILE</p>
          <h2>{profile.username}</h2>
          <span className="level-badge">LEVEL {profile.level}</span>
          <p className="favorite-genre">
            Favorite Genre: {profile.favorite_genre}
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>🎯</span>
          <h3>{profile.games_played}</h3>
          <p>Games Played</p>
        </div>

        <div className="stat-card">
          <span>⭐</span>
          <h3>
            {(profile.total_points ?? profile.points ?? 0).toLocaleString()}
          </h3>
          <p>Total Points</p>
        </div>

        <div className="profile-stat">
          <span>🎮</span>
          <strong>{profile.mini_game_points ?? 0}</strong>
          <small>Mini-Game Points</small>
        </div>

        <div className="stat-card">
          <span>🏆</span>
          <h3>{profile.achievements.length}</h3>
          <p>Achievements</p>
        </div>
      </div>

      <div className="profile-edit">
        <p className="eyebrow">CUSTOMIZE YOUR ACCOUNT</p>
        <h2>Edit Your Profile</h2>

        <form onSubmit={updateProfile}>
          <div className="profile-input-group">
            <label htmlFor="username">Player Username</label>
            <input
              id="username"
              value={newUsername}
              onChange={(event) => setNewUsername(event.target.value)}
              placeholder="Enter your username"
            />
          </div>

          <div className="profile-input-group">
            <label htmlFor="favoriteGenre">Favorite Genre</label>
            <select
              id="favoriteGenre"
              value={profile.favorite_genre}
              onChange={(event) => updateGenre(event.target.value)}
            >
              <option value="Action">Action</option>
              <option value="Adventure">Adventure</option>
              <option value="Racing">Racing</option>
              <option value="Strategy">Strategy</option>
            </select>
          </div>

          <button className="profile-save-btn" type="submit">
            SAVE PROFILE
          </button>
        </form>

        {message && <p className="profile-message">{message}</p>}
      </div>

      <div className="achievements-section">
        <p className="eyebrow">YOUR MILESTONES</p>
        <h2>Achievements</h2>

        <div className="achievements-grid">
          {profile.achievements.map((achievement) => (
            <div className="achievement-card" key={achievement.name}>
              <div className="achievement-icon">{achievement.icon}</div>

              <div>
                <h3>{achievement.name}</h3>
                <p>{achievement.description}</p>
              </div>
            </div>
          ))}
        </div>

        <button className="unlock-btn" onClick={unlockAchievement}>
          🏆 UNLOCK TEST ACHIEVEMENT (+500 POINTS)
        </button>
      </div>
    </section>
  );
}

export default PlayerProfile;
