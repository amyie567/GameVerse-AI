import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import (
    add_mini_game_points as add_mini_game_points_to_database,
)
from database import (
    fetch_chat_history,
    fetch_leaderboard,
    fetch_player_profile,
    fetch_recommendation_history,
    save_chat_message,
    save_leaderboard_score,
    save_player_profile,
    save_recommendation_history,
    unlock_player_achievement,
    update_player_profile,
)

app = FastAPI(
    title="GameVerse AI API",
    description="AI-powered gaming recommendation platform",
    version="1.0.0",
)

# Allow our React frontend to communicate with Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Our game dataset
GAMES = [
    {
        "id": 1,
        "name": "Neon Racer",
        "genre": "Racing",
        "difficulty": "Medium",
        "play_style": "Competitive",
    },
    {
        "id": 2,
        "name": "Shadow Quest",
        "genre": "Adventure",
        "difficulty": "Hard",
        "play_style": "Exploration",
    },
    {
        "id": 3,
        "name": "Cyber Chess",
        "genre": "Strategy",
        "difficulty": "Easy",
        "play_style": "Strategic",
    },
    {
        "id": 4,
        "name": "Battle Zone",
        "genre": "Action",
        "difficulty": "Hard",
        "play_style": "Competitive",
    },
    {
        "id": 5,
        "name": "Galaxy Explorer",
        "genre": "Adventure",
        "difficulty": "Medium",
        "play_style": "Exploration",
    },
    {
        "id": 6,
        "name": "Speed Legends",
        "genre": "Racing",
        "difficulty": "Easy",
        "play_style": "Competitive",
    },
    {
        "id": 7,
        "name": "Kingdom Tactics",
        "genre": "Strategy",
        "difficulty": "Medium",
        "play_style": "Strategic",
    },
    {
        "id": 8,
        "name": "Shadow Strike",
        "genre": "Action",
        "difficulty": "Medium",
        "play_style": "Competitive",
    },
]
# Prepare game features for machine learning
game_features = []

for game in GAMES:
    features = game["genre"] + " " + game["difficulty"] + " " + game["play_style"]
    game_features.append(features)

# Convert game features into numerical vectors
vectorizer = TfidfVectorizer()
game_vectors = vectorizer.fit_transform(game_features)

# Calculate similarity between all games
similarity_matrix = cosine_similarity(game_vectors)

# Temporary player profile storage
PLAYER_PROFILE = {
    "username": "CyberGamer",
    "level": 12,
    "favorite_genre": "Action",
    "games_played": 24,
    "total_points": 2450,
    "mini_game_points": 0,
    "achievements": [
        {
            "name": "First Adventure",
            "description": "Started your gaming journey",
            "icon": "🎮",
        },
        {
            "name": "Speed Master",
            "description": "Racing enthusiast",
            "icon": "🏎️",
        },
        {
            "name": "Strategy Expert",
            "description": "Master of tactics",
            "icon": "♟️",
        },
    ],
}

# Store recommendation history
RECOMMENDATION_HISTORY = []


# Player preference model
class PlayerPreferences(BaseModel):
    genre: str = Field(default="Any", min_length=1, max_length=50)
    difficulty: str = Field(default="Any", min_length=1, max_length=50)
    play_style: str = Field(default="Any", min_length=1, max_length=50)


class PlayerProfileUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    favorite_genre: str = Field(min_length=1, max_length=50)
    preferred_difficulty: str = Field(default="Any", min_length=1, max_length=50)
    preferred_play_style: str = Field(default="Any", min_length=1, max_length=50)


@app.get("/")
def home():
    return {
        "message": "Welcome to GameVerse AI!",
        "status": "running",
    }


@app.get("/api/games")
def get_games():
    return {"games": GAMES}


# AI recommendation engine


@app.post("/api/recommendations")
def recommend_games(preferences: PlayerPreferences):

    recommendations = []

    for game in GAMES:
        score = 0
        possible_score = 0
        reasons = []

        # Genre matching: 50 points
        if preferences.genre != "Any":
            possible_score += 50

            if game["genre"] == preferences.genre:
                score += 50
                reasons.append("Matches your favorite genre")

        # Difficulty matching: 30 points
        if preferences.difficulty != "Any":
            possible_score += 30

            if game["difficulty"] == preferences.difficulty:
                score += 30
                reasons.append("Matches your preferred difficulty")

        # Play style matching: 20 points
        if preferences.play_style != "Any":
            possible_score += 20

            if game["play_style"] == preferences.play_style:
                score += 20
                reasons.append("Matches your play style")

        # Calculate percentage
        match_percentage = (
            round((score / possible_score) * 100) if possible_score > 0 else 0
        )

        recommendations.append(
            {
                **game,
                "match_percentage": match_percentage,
                "reasons": reasons,
            }
        )

    # Sort recommendations by match percentage
    recommendations.sort(key=lambda game: game["match_percentage"], reverse=True)

    # Save Rule-Based recommendation history to PostgreSQL
    save_recommendation_history(
        genre=preferences.genre,
        difficulty=preferences.difficulty,
        play_style=preferences.play_style,
        recommendations=[
            {
                "name": game["name"],
                "genre": game["genre"],
                "match_percentage": game["match_percentage"],
            }
            for game in recommendations[:5]
        ],
    )

    return recommendations[:5]


# Get player profile from PostgreSQL
@app.get("/api/profile")
def get_profile():
    try:
        profile = fetch_player_profile()

        if profile is None:
            save_player_profile(
                username=PLAYER_PROFILE["username"],
                favorite_genre=PLAYER_PROFILE["favorite_genre"],
                achievements=PLAYER_PROFILE["achievements"],
                points=PLAYER_PROFILE.get("points", 0),
            )

            profile = fetch_player_profile()

        if profile is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to create or retrieve player profile.",
            )

        return profile

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving player profile.",
        )


# Update player profile in PostgreSQL
@app.put("/api/profile")
def update_profile(profile: PlayerProfileUpdate):
    try:
        current_profile = fetch_player_profile()

        if current_profile is None:
            save_player_profile(
                username=profile.username,
                favorite_genre=profile.favorite_genre,
                achievements=PLAYER_PROFILE["achievements"],
                points=PLAYER_PROFILE["points"],
            )
        else:
            update_player_profile(
                username=profile.username,
                favorite_genre=profile.favorite_genre,
                preferred_difficulty=profile.preferred_difficulty,
                preferred_play_style=profile.preferred_play_style,
            )

        updated_profile = fetch_player_profile()

        if updated_profile is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve updated player profile.",
            )

        return {
            "message": "Profile updated successfully!",
            "profile": updated_profile,
        }

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while updating player profile.",
        )


# Unlock an achievement and save it in PostgreSQL
@app.post("/api/profile/achievement")
def unlock_achievement():
    try:
        achievement_name = "Gaming Champion"

        achievements, unlocked = unlock_player_achievement(
            achievement_name=achievement_name,
            description="Unlocked a new achievement",
            icon="🏆",
            points_to_add=500,
        )

        if achievements is None:
            return {
                "message": "Player profile not found.",
                "profile": None,
            }

        updated_profile = fetch_player_profile()

        if updated_profile is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve updated player profile.",
            )

        if not unlocked:
            return {
                "message": "Achievement already unlocked!",
                "profile": updated_profile,
            }

        return {
            "message": "Achievement unlocked! +500 points",
            "profile": updated_profile,
        }

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while unlocking achievement.",
        )


class MiniGamePoints(BaseModel):
    points: int = Field(gt=0, le=1000)


# Add mini-game points and save them in PostgreSQL
@app.post("/api/profile/mini-game-points")
def add_mini_game_points(data: MiniGamePoints):
    try:
        if data.points <= 0 or data.points > 1000:
            raise HTTPException(
                status_code=400,
                detail="Invalid points value!",
            )

        result = add_mini_game_points_to_database(data.points)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Player profile not found!",
            )

        updated_profile = fetch_player_profile()

        if updated_profile is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve updated player profile.",
            )

        return {
            "message": "Mini-game points added successfully!",
            "profile": updated_profile,
        }

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while adding mini-game points.",
        )


# Get leaderboard from PostgreSQL
@app.get("/api/leaderboard")
def get_leaderboard():
    try:
        profile = fetch_player_profile()

        if profile is not None:
            save_leaderboard_score(
                profile["username"],
                profile["points"],
            )

        leaderboard = fetch_leaderboard()

        if leaderboard is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve leaderboard.",
            )

        return leaderboard

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving leaderboard.",
        )


# api chat code start here
class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


def detect_chat_intent(message):
    message = message.lower().strip()

    # 1. Explanation intent
    if re.search(r"\b(why|explain|reason|because)\b", message):
        return "explain"

    # 2. Gaming tips intent
    if re.search(
        r"\b(tip|tips|advice|improve|"
        r"improvement|skill|guide|guidance)\b",
        message,
    ):
        return "tips"

    # 3. Specific game genre intent
    if re.search(
        r"\b(racing|adventure|strategy|action|exploration)\b",
        message,
    ):
        return "genre"

    # 4. Difficulty intent
    if re.search(
        r"\b(easy|medium|hard|challenging|difficult)\b",
        message,
    ):
        return "difficulty"

    # 5. Recommendation intent
    if re.search(
        r"\b(recommend|recommendation|suggest|suggestion|"
        r"which game|what game|game for me|find me a game|"
        r"what should i play|play tonight|something to play)\b",
        message,
    ):
        return "recommend"

    # 6. Competitive gaming intent
    if re.search(
        r"\b(competitive|competition|multiplayer|"
        r"ranked|tournament)\b",
        message,
    ):
        return "competitive"

    # 7. Greeting intent
    if re.search(
        r"^(hello|hi|hey|good morning|good evening)\b",
        message,
    ):
        return "greeting"

    return "general"


# extract game code start here
def extract_game_preferences(message):
    message = message.lower().strip()

    preferences = {"genre": "Any", "difficulty": "Any"}

    # Extract genre
    genres = {
        "racing": "Racing",
        "adventure": "Adventure",
        "strategy": "Strategy",
        "action": "Action",
        "exploration": "Adventure",
    }

    for keyword, genre in genres.items():
        if keyword in message:
            preferences["genre"] = genre
            break

    # Extract difficulty
    if re.search(r"\b(easy|beginner|simple)\b", message):
        preferences["difficulty"] = "Easy"

    elif re.search(r"\b(medium|moderate|normal)\b", message):
        preferences["difficulty"] = "Medium"

    elif re.search(r"\b(hard|challenging|difficult|tough)\b", message):
        preferences["difficulty"] = "Hard"

    return preferences


# API Chat
@app.post("/api/chat")
def gaming_assistant(chat: ChatMessage):
    try:
        return generate_chat_reply(chat)

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database or server error while processing chat.",
        )


# Generate the gaming assistant response
def generate_chat_reply(chat: ChatMessage):
    user_message = chat.message.strip()
    message_lower = user_message.lower()

    if not message_lower:
        return {"reply": "Please enter a message!"}

    # Detect user intent
    intent = detect_chat_intent(message_lower)

    # Extract genre and difficulty preferences
    extracted_preferences = extract_game_preferences(message_lower)

    requested_genre = extracted_preferences["genre"]
    requested_difficulty = extracted_preferences["difficulty"]

    # Get saved player profile
    profile = fetch_player_profile()
    username = profile["username"] if profile else "Guest"

    # Combined genre and difficulty recommendations
    if requested_genre != "Any" and requested_difficulty != "Any":
        if profile:
            selected_genre, recommendations = generate_hybrid_recommendations(
                requested_genre,
                requested_difficulty,
                profile["preferred_play_style"],
            )

            top_games = recommendations[:3]
            game_details = []

            for game in top_games:
                game_details.append(
                    f"\n\n🎯 {game['name']} "
                    f"({game['match_percentage']}% match)\n"
                    f"Why: {game['recommendation_reason']}"
                )

            reply = (
                f"🎮 Here are your recommendations for "
                f"{requested_difficulty} {selected_genre} games:"
                f"{''.join(game_details)}"
            )
        else:
            reply = "Player profile not found."

    # Greeting
    elif intent == "greeting":
        reply = (
            "Hello, gamer! 🎮 Welcome to GameVerse AI. "
            "Would you like personalized game recommendations, "
            "gaming tips, or help finding your next adventure?"
        )

    # Specific genre recommendations
    elif intent == "genre":
        if "racing" in message_lower:
            reply = (
                "🏎️ Racing recommendations: Neon Racer (Medium) "
                "and Speed Legends (Easy)."
            )
        elif "adventure" in message_lower:
            reply = (
                "🚀 Adventure recommendations: Shadow Quest (Hard) "
                "and Galaxy Explorer (Medium)."
            )
        elif "strategy" in message_lower:
            reply = (
                "♟️ Strategy recommendations: Cyber Chess (Easy) "
                "and Kingdom Tactics (Medium)."
            )
        elif "action" in message_lower:
            reply = (
                "⚔️ Action recommendations: Battle Zone (Hard) "
                "and Shadow Strike (Medium)."
            )
        else:
            reply = "For exploration, try Shadow Quest or Galaxy Explorer."

    # Personalized game recommendations
    elif intent == "recommend":
        if profile:
            selected_genre, recommendations = generate_hybrid_recommendations(
                profile["favorite_genre"],
                profile["preferred_difficulty"],
                profile["preferred_play_style"],
            )

            top_games = recommendations[:3]
            game_details = []

            for game in top_games:
                game_details.append(
                    f"\n\n🎯 {game['name']} "
                    f"({game['match_percentage']}% match)\n"
                    f"Why: {game['recommendation_reason']}"
                )

            reply = (
                f"🎮 Based on your preferences "
                f"({selected_genre}, "
                f"{profile['preferred_difficulty']}, "
                f"{profile['preferred_play_style']}), "
                f"here are my top recommendations:"
                f"{''.join(game_details)}"
            )
        else:
            reply = "Player profile not found."

    # Explain a recommendation
    elif intent == "explain":
        if profile:
            selected_genre, recommendations = generate_hybrid_recommendations(
                profile["favorite_genre"],
                profile["preferred_difficulty"],
                profile["preferred_play_style"],
            )

            selected_game = next(
                (
                    game
                    for game in recommendations
                    if game["name"].lower() in message_lower
                ),
                recommendations[0] if recommendations else None,
            )

            if selected_game:
                reply = (
                    f"🤖 Here's why I recommended "
                    f"{selected_game['name']}:\n\n"
                    f"🎯 Match: "
                    f"{selected_game['match_percentage']}%\n"
                    f"📝 Explanation: "
                    f"{selected_game['recommendation_reason']}"
                )
            else:
                reply = "I couldn't find a recommendation to explain."
        else:
            reply = "Player profile not found."

    # Competitive gaming
    elif intent == "competitive":
        reply = (
            "🏆 If you enjoy competitive games, try "
            "Neon Racer, Speed Legends, Battle Zone, "
            "or Shadow Strike!"
        )

    # Gaming tips
    elif intent == "tips":
        reply = (
            "🎮 Gaming tips:\n\n"
            "1. Practice regularly.\n"
            "2. Learn the game mechanics.\n"
            "3. Choose a difficulty that suits your skills.\n"
            "4. Analyze your mistakes.\n"
            "5. Keep improving and enjoy the challenge!"
        )

    # Easy games
    elif "easy" in message_lower:
        reply = (
            "Looking for easy games? Try Cyber Chess or "
            "Speed Legends. Both have Easy difficulty."
        )

    # Medium games
    elif "medium" in message_lower:
        reply = (
            "Try Neon Racer, Galaxy Explorer, Kingdom Tactics, "
            "or Shadow Strike. They all have Medium difficulty."
        )

    # Hard games
    elif "hard" in message_lower:
        reply = (
            "Ready for a challenge? Try Shadow Quest or Battle Zone. "
            "Both have Hard difficulty."
        )

    # Racing games
    elif "racing" in message_lower:
        reply = (
            "🏎️ Racing recommendations: Neon Racer (Medium) and Speed Legends (Easy)."
        )

    # Adventure games
    elif "adventure" in message_lower:
        reply = (
            "🚀 Adventure recommendations: Shadow Quest (Hard) "
            "and Galaxy Explorer (Medium)."
        )

    # Strategy games
    elif "strategy" in message_lower:
        reply = (
            "♟️ Strategy recommendations: Cyber Chess (Easy) "
            "and Kingdom Tactics (Medium)."
        )

    # Action games
    elif "action" in message_lower:
        reply = (
            "⚔️ Action recommendations: Battle Zone (Hard) and Shadow Strike (Medium)."
        )

    # Exploration games
    elif "exploration" in message_lower:
        reply = "For exploration, try Shadow Quest or Galaxy Explorer."

    # Default response
    else:
        reply = (
            "I'm your GameVerse AI gaming assistant! 🤖 "
            "Ask me about Action, Racing, Adventure, Strategy, "
            "game difficulty, competitive play, recommendations, "
            "or gaming tips."
        )

    # Save conversation in PostgreSQL
    save_chat_message(username, user_message, reply)

    return {"reply": reply}


# Get chat history from PostgreSQL
@app.get("/api/chat-history")
def get_chat_history():
    try:
        profile = fetch_player_profile()
        username = profile["username"] if profile else "Guest"

        history = fetch_chat_history(username)

        if history is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve chat history.",
            )

        return history

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving chat history.",
        )


# Machine Learning recommendation engine


def generate_hybrid_recommendations(genre, difficulty, play_style):
    # Read saved player profile
    profile = fetch_player_profile()

    # Remember whether the user explicitly selected a genre
    genre_was_selected = genre != "Any"

    # Use saved favorite genre when Any is selected
    selected_genre = genre

    if selected_genre == "Any" and profile:
        selected_genre = profile["favorite_genre"]

    # Create player feature description
    player_features = selected_genre + " " + difficulty + " " + play_style

    # Calculate TF-IDF similarity
    player_vector = vectorizer.transform([player_features])

    similarity_scores = cosine_similarity(player_vector, game_vectors)[0]

    recommendations = []

    for index, game in enumerate(GAMES):
        # Filter out unrelated genres when explicitly selected
        if genre_was_selected and game["genre"] != selected_genre:
            continue

        ml_score = float(similarity_scores[index]) * 100

        preference_score = 0
        max_score = 0

        matched_preferences = []

        # Genre matching
        if selected_genre != "Any":
            max_score += 50

            if game["genre"] == selected_genre:
                preference_score += 50
                matched_preferences.append(f"{selected_genre} genre")

        # Difficulty matching
        if difficulty != "Any":
            max_score += 30

            if game["difficulty"] == difficulty:
                preference_score += 30
                matched_preferences.append(f"{difficulty} difficulty")

        # Play-style matching
        if play_style != "Any":
            max_score += 20

            if game["play_style"] == play_style:
                preference_score += 20
                matched_preferences.append(f"{play_style} play style")

        if max_score > 0:
            preference_score = (preference_score / max_score) * 100

        # Hybrid score: 60% ML + 40% preferences
        hybrid_score = ml_score * 0.6 + preference_score * 0.4

        # Generate explanation
        if matched_preferences:
            recommendation_reason = (
                "Matches your preferences for " + ", ".join(matched_preferences) + "."
            )
        elif ml_score > 0:
            recommendation_reason = (
                "Recommended because its game features "
                "show similarity to your preferences."
            )
        else:
            recommendation_reason = (
                "This game does not closely match your selected preferences."
            )

        recommendations.append(
            {
                **game,
                "similarity_score": round(ml_score, 2),
                "preference_score": round(preference_score, 2),
                "match_percentage": round(hybrid_score),
                "recommendation_reason": recommendation_reason,
            }
        )

    recommendations.sort(key=lambda game: game["match_percentage"], reverse=True)

    return selected_genre, recommendations


# api ml recommendations start here
@app.post("/api/ml-recommendations")
def ml_recommend_games(preferences: PlayerPreferences):

    selected_genre, recommendations = generate_hybrid_recommendations(
        preferences.genre, preferences.difficulty, preferences.play_style
    )

    # Save the top five recommendations to PostgreSQL
    save_recommendation_history(
        genre=selected_genre,
        difficulty=preferences.difficulty,
        play_style=preferences.play_style,
        recommendations=[
            {
                "name": game["name"],
                "genre": game["genre"],
                "match_percentage": game["match_percentage"],
            }
            for game in recommendations[:5]
        ],
    )

    return recommendations


# Get recommendation history from PostgreSQL
@app.get("/api/recommendation-history")
def get_recommendation_history():
    try:
        history = fetch_recommendation_history()

        if history is None:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve recommendation history.",
            )

        return {
            "total_requests": len(history),
            "history": history,
        }

    except HTTPException:
        raise

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving recommendation history.",
        )
