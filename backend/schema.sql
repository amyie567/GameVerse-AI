-- 1. Chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Leaderboard
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_leaderboard_username UNIQUE (username)
);

-- 3. Player profile
CREATE TABLE IF NOT EXISTS player_profile (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    favorite_genre VARCHAR(50) DEFAULT 'Any',
    achievements JSONB DEFAULT '[]'::jsonb,
    points INTEGER DEFAULT 0,
    mini_game_points INTEGER DEFAULT 0,
    preferred_difficulty VARCHAR(50) DEFAULT 'Any',
    preferred_play_style VARCHAR(50) DEFAULT 'Any'
);

-- 4. Recommendation history
CREATE TABLE IF NOT EXISTS recommendation_history (
    id SERIAL PRIMARY KEY,
    genre VARCHAR(50),
    difficulty VARCHAR(50),
    play_style VARCHAR(50),
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);