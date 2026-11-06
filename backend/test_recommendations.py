import pytest
from fastapi.testclient import TestClient

import main


def test_explicit_genre_filtering(monkeypatch):
    monkeypatch.setattr(
        main, "fetch_player_profile", lambda: {"favorite_genre": "Action"}
    )

    selected_genre, recommendations = main.generate_hybrid_recommendations(
        "Adventure", "Easy", "Any"
    )

    assert selected_genre == "Adventure"
    assert len(recommendations) == 2
    assert all(game["genre"] == "Adventure" for game in recommendations)


def test_difficulty_preference_score(monkeypatch):
    monkeypatch.setattr(
        main, "fetch_player_profile", lambda: {"favorite_genre": "Action"}
    )

    _, recommendations = main.generate_hybrid_recommendations(
        "Action", "Hard", "Competitive"
    )

    battle_zone = next(
        game for game in recommendations if game["name"] == "Battle Zone"
    )

    shadow_strike = next(
        game for game in recommendations if game["name"] == "Shadow Strike"
    )

    assert battle_zone["preference_score"] == 100
    assert shadow_strike["preference_score"] == 70


def test_recommendation_explanations(monkeypatch):
    monkeypatch.setattr(
        main, "fetch_player_profile", lambda: {"favorite_genre": "Action"}
    )

    _, recommendations = main.generate_hybrid_recommendations(
        "Action", "Hard", "Competitive"
    )

    battle_zone = recommendations[0]

    assert "Action genre" in battle_zone["recommendation_reason"]
    assert "Hard difficulty" in battle_zone["recommendation_reason"]
    assert "Competitive play style" in battle_zone["recommendation_reason"]


def test_recommendations_are_sorted(monkeypatch):
    monkeypatch.setattr(
        main, "fetch_player_profile", lambda: {"favorite_genre": "Action"}
    )

    _, recommendations = main.generate_hybrid_recommendations("Any", "Any", "Any")

    scores = [game["match_percentage"] for game in recommendations]

    assert scores == sorted(scores, reverse=True)


client = TestClient(main.app, raise_server_exceptions=True)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to GameVerse AI!",
        "status": "running",
    }


def test_get_games_endpoint():
    response = client.get("/api/games")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "games" in data

    games = data["games"]

    assert isinstance(games, list)
    assert len(games) > 0

    assert any(game["name"] == "Battle Zone" for game in games)


def test_get_player_profile_endpoint():
    response = client.get("/api/profile")

    assert response.status_code == 200

    profile = response.json()

    assert isinstance(profile, dict)
    assert "username" in profile
    assert "favorite_genre" in profile
    assert "achievements" in profile
    assert "points" in profile


def test_recommendation_history_endpoint():
    response = client.get("/api/recommendation-history")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "total_requests" in data
    assert "history" in data

    history = data["history"]

    assert isinstance(history, list)
    assert data["total_requests"] >= 0


def test_chat_history_endpoint():
    response = client.get("/api/chat-history")

    assert response.status_code == 200

    history = response.json()

    assert isinstance(history, list)


def test_invalid_mini_game_points():
    response = client.post(
        "/api/profile/mini-game-points",
        json={"points": -10},
    )

    assert response.status_code == 422


def test_empty_chat_message():
    response = client.post(
        "/api/chat",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_oversized_username():
    response = client.put(
        "/api/profile",
        json={
            "username": "A" * 31,
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    assert response.status_code == 422


def test_oversized_chat_message():
    response = client.post(
        "/api/chat",
        json={"message": "A" * 2001},
    )

    assert response.status_code == 422


def test_mini_game_points_validation():
    response = client.post(
        "/api/profile/mini-game-points",
        json={"points": 1001},
    )

    assert response.status_code == 422


def test_rule_based_recommendations():
    response = client.post(
        "/api/recommendations",
        json={
            "genre": "Action",
            "difficulty": "Hard",
            "play_style": "Competitive",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 5

    assert data[0]["name"] == "Battle Zone"
    assert data[0]["match_percentage"] == 100

    assert all("match_percentage" in game and "reasons" in game for game in data)

    assert data == sorted(
        data,
        key=lambda game: game["match_percentage"],
        reverse=True,
    )


def test_ml_recommendations(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    response = client.post(
        "/api/ml-recommendations",
        json={
            "genre": "Action",
            "difficulty": "Hard",
            "play_style": "Competitive",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    assert data[0]["name"] == "Battle Zone"
    assert data[0]["match_percentage"] == 100

    assert all(
        "similarity_score" in game
        and "preference_score" in game
        and "recommendation_reason" in game
        for game in data
    )


def test_ml_recommendations_are_sorted(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    response = client.post(
        "/api/ml-recommendations",
        json={
            "genre": "Action",
            "difficulty": "Hard",
            "play_style": "Competitive",
        },
    )

    assert response.status_code == 200

    data = response.json()

    percentages = [game["match_percentage"] for game in data]

    assert percentages == sorted(percentages, reverse=True)


def test_profile_update_validation(monkeypatch):
    profile = {
        "username": "OldGamer",
        "favorite_genre": "Adventure",
        "preferred_difficulty": "Any",
        "preferred_play_style": "Any",
    }

    monkeypatch.setattr(main, "fetch_player_profile", lambda: profile)

    monkeypatch.setattr(
        main,
        "update_player_profile",
        lambda **kwargs: profile.update(kwargs),
    )

    response = client.put(
        "/api/profile",
        json={
            "username": "TestGamer",
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Profile updated successfully!"
    assert data["profile"]["username"] == "TestGamer"
    assert data["profile"]["favorite_genre"] == "Action"


def test_unlock_achievement(monkeypatch):
    monkeypatch.setattr(
        main,
        "unlock_player_achievement",
        lambda **kwargs: (
            ["Gaming Champion"],
            True,
        ),
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "achievements": ["Gaming Champion"],
            "points": 500,
        },
    )

    response = client.post("/api/profile/achievement")

    assert response.status_code == 200

    data = response.json()

    assert "Achievement unlocked" in data["message"]
    assert "Gaming Champion" in data["profile"]["achievements"]
    assert data["profile"]["points"] == 500


def test_leaderboard_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "points": 500,
        },
    )

    monkeypatch.setattr(
        main,
        "save_leaderboard_score",
        lambda username, points: None,
    )

    monkeypatch.setattr(
        main,
        "fetch_leaderboard",
        lambda: [
            {"username": "TestGamer", "points": 500},
            {"username": "CyberGamer", "points": 400},
        ],
    )

    response = client.get("/api/leaderboard")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["username"] == "TestGamer"
    assert data[0]["points"] == 500


def test_chat_assistant_greeting(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "achievements": [],
            "points": 0,
            "preferred_difficulty": "Any",
            "preferred_play_style": "Any",
        },
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args, **kwargs: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "reply" in data
    assert len(data["reply"]) > 0


def test_chat_assistant_recommendations(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "achievements": [],
            "points": 0,
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args, **kwargs: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Recommend some games"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "reply" in data
    assert len(data["reply"]) > 0
    assert "Battle Zone" in data["reply"]


def test_chat_intent_detection():
    test_cases = [
        ("Why did you recommend this game?", "explain"),
        ("Give me gaming tips", "tips"),
        ("I like racing games", "genre"),
        ("Suggest a hard game", "difficulty"),
        ("Recommend some games", "recommend"),
        ("I enjoy competitive games", "competitive"),
        ("Hello there", "greeting"),
        ("Tell me something interesting", "general"),
    ]

    for message, expected_intent in test_cases:
        assert main.detect_chat_intent(message) == expected_intent


def test_extract_game_preferences():
    test_cases = [
        (
            "I want an action game on hard difficulty",
            {"genre": "Action", "difficulty": "Hard"},
        ),
        (
            "Suggest an easy racing game",
            {"genre": "Racing", "difficulty": "Easy"},
        ),
        (
            "I like adventure games with medium difficulty",
            {"genre": "Adventure", "difficulty": "Medium"},
        ),
        (
            "Recommend something",
            {"genre": "Any", "difficulty": "Any"},
        ),
    ]

    for message, expected in test_cases:
        assert main.extract_game_preferences(message) == expected


def test_chat_assistant_competitive(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "I enjoy competitive games"})

    assert response.status_code == 200
    assert "Neon Racer" in response.json()["reply"]
    assert "Battle Zone" in response.json()["reply"]


def test_chat_assistant_tips(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "Give me some gaming tips"})

    assert response.status_code == 200
    assert "Gaming tips" in response.json()["reply"]
    assert "Practice regularly" in response.json()["reply"]


def test_chat_assistant_easy_games(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "Show me easy games"})

    assert response.status_code == 200
    assert "Cyber Chess" in response.json()["reply"]
    assert "Speed Legends" in response.json()["reply"]


def test_chat_assistant_medium_games(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "Show me medium games"})

    assert response.status_code == 200
    assert "Neon Racer" in response.json()["reply"]
    assert "Galaxy Explorer" in response.json()["reply"]
    assert "Kingdom Tactics" in response.json()["reply"]


def test_chat_assistant_hard_games(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "Show me hard games"})

    assert response.status_code == 200
    assert "Shadow Quest" in response.json()["reply"]
    assert "Battle Zone" in response.json()["reply"]


def test_chat_assistant_racing_games(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "Tell me about racing games"})

    assert response.status_code == 200
    assert "Neon Racer" in response.json()["reply"]
    assert "Speed Legends" in response.json()["reply"]


def test_chat_assistant_adventure_games(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post(
        "/api/chat", json={"message": "Tell me about adventure games"}
    )

    assert response.status_code == 200
    assert "Shadow Quest" in response.json()["reply"]
    assert "Galaxy Explorer" in response.json()["reply"]


def test_chat_assistant_strategy_games(monkeypatch):
    monkeypatch.setattr(main, "fetch_player_profile", lambda: {"username": "TestGamer"})
    monkeypatch.setattr(main, "save_chat_message", lambda *args: None)

    response = client.post("/api/chat", json={"message": "strategy"})

    assert response.status_code == 200
    assert "Cyber Chess" in response.json()["reply"]
    assert "Kingdom Tactics" in response.json()["reply"]


def test_chat_assistant_action_games(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {"username": "TestGamer"},
    )
    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "action"},
    )

    assert response.status_code == 200
    assert "Battle Zone" in response.json()["reply"]
    assert "Shadow Strike" in response.json()["reply"]


def test_chat_assistant_exploration_games(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {"username": "TestGamer"},
    )
    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "exploration"},
    )

    assert response.status_code == 200
    assert "Shadow Quest" in response.json()["reply"]
    assert "Galaxy Explorer" in response.json()["reply"]


def test_chat_assistant_combined_preferences(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    monkeypatch.setattr(
        main,
        "generate_hybrid_recommendations",
        lambda *args: (
            "Action",
            [
                {
                    "name": "Battle Zone",
                    "match_percentage": 100,
                    "recommendation_reason": "Matches Action and Hard difficulty.",
                }
            ],
        ),
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "I want an action game on hard difficulty"},
    )

    assert response.status_code == 200
    assert "Battle Zone" in response.json()["reply"]
    assert "Hard Action games" in response.json()["reply"]


def test_chat_explanation_without_profile(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Why did you recommend Battle Zone?"},
    )

    assert response.status_code == 200
    assert response.json()["reply"] == "Player profile not found."


def test_chat_explanation_without_recommendations(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    monkeypatch.setattr(
        main,
        "generate_hybrid_recommendations",
        lambda *args: ("Action", []),
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Why did you recommend Battle Zone?"},
    )

    assert response.status_code == 200
    assert response.json()["reply"] == ("I couldn't find a recommendation to explain.")


def test_chat_explanation_for_specific_game(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        },
    )

    monkeypatch.setattr(
        main,
        "generate_hybrid_recommendations",
        lambda *args: (
            "Action",
            [
                {
                    "name": "Battle Zone",
                    "match_percentage": 100,
                    "recommendation_reason": "Matches Action and Hard difficulty.",
                },
                {
                    "name": "Shadow Strike",
                    "match_percentage": 68,
                    "recommendation_reason": "Matches Competitive play style.",
                },
            ],
        ),
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda *args: None,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Why did you recommend Shadow Strike?"},
    )

    assert response.status_code == 200
    assert "Shadow Strike" in response.json()["reply"]
    assert "68%" in response.json()["reply"]


def test_rule_recommendations_endpoint(monkeypatch):
    saved_data = {}

    monkeypatch.setattr(
        main,
        "GAMES",
        [
            {
                "name": "Game A",
                "genre": "Action",
                "difficulty": "Hard",
                "play_style": "Competitive",
            },
            {
                "name": "Game B",
                "genre": "Racing",
                "difficulty": "Easy",
                "play_style": "Casual",
            },
        ],
    )

    def mock_save_recommendation_history(**kwargs):
        saved_data.update(kwargs)

    monkeypatch.setattr(
        main,
        "save_recommendation_history",
        mock_save_recommendation_history,
    )

    response = client.post(
        "/api/recommendations",
        json={
            "genre": "Action",
            "difficulty": "Hard",
            "play_style": "Competitive",
        },
    )

    assert response.status_code == 200

    recommendations = response.json()

    assert len(recommendations) == 2
    assert recommendations[0]["name"] == "Game A"
    assert recommendations[0]["match_percentage"] == 100
    assert recommendations[1]["name"] == "Game B"
    assert recommendations[1]["match_percentage"] == 0

    assert saved_data["genre"] == "Action"
    assert saved_data["difficulty"] == "Hard"
    assert saved_data["play_style"] == "Competitive"
    assert len(saved_data["recommendations"]) == 2


def test_rule_recommendations_with_any_preferences(monkeypatch):
    monkeypatch.setattr(
        main,
        "save_recommendation_history",
        lambda **kwargs: None,
    )

    response = client.post(
        "/api/recommendations",
        json={
            "genre": "Any",
            "difficulty": "Any",
            "play_style": "Any",
        },
    )

    assert response.status_code == 200

    recommendations = response.json()

    assert len(recommendations) <= 5
    assert all(game["match_percentage"] == 0 for game in recommendations)


def test_rule_recommendations_save_only_top_five(monkeypatch):
    saved_data = {}

    monkeypatch.setattr(
        main,
        "save_recommendation_history",
        lambda **kwargs: saved_data.update(kwargs),
    )

    response = client.post(
        "/api/recommendations",
        json={
            "genre": "Any",
            "difficulty": "Any",
            "play_style": "Any",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) <= 5
    assert len(saved_data["recommendations"]) <= 5


def test_get_profile_creates_profile_when_missing(monkeypatch):
    calls = {"count": 0}
    saved_data = {}

    def mock_fetch_player_profile():
        calls["count"] += 1

        if calls["count"] == 1:
            return None

        return {
            "username": "TestGamer",
            "favorite_genre": "Action",
            "achievements": [],
            "points": 0,
        }

    def mock_save_player_profile(**kwargs):
        saved_data.update(kwargs)

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        mock_fetch_player_profile,
    )

    monkeypatch.setattr(
        main,
        "save_player_profile",
        mock_save_player_profile,
    )

    response = client.get("/api/profile")

    assert response.status_code == 200
    assert response.json()["username"] == "TestGamer"
    assert calls["count"] == 2
    assert saved_data["username"] == main.PLAYER_PROFILE["username"]


def test_get_profile_fails_when_creation_unsuccessful(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "save_player_profile",
        lambda **kwargs: None,
    )

    response = client.get("/api/profile")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to create or retrieve player profile.")


def test_get_profile_handles_database_error(monkeypatch):
    def mock_fetch_player_profile():
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        mock_fetch_player_profile,
    )

    response = client.get("/api/profile")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Database error while retrieving player profile."
    )


def test_update_profile_creates_profile_when_missing(monkeypatch):
    calls = {"count": 0}
    saved_data = {}

    test_profile = {
        "username": "NewGamer",
        "favorite_genre": "Racing",
        "achievements": [],
        "points": 0,
        "preferred_difficulty": "Easy",
        "preferred_play_style": "Casual",
    }

    monkeypatch.setattr(
        main,
        "PLAYER_PROFILE",
        test_profile.copy(),
    )

    def mock_fetch_player_profile():
        calls["count"] += 1

        if calls["count"] == 1:
            return None

        return test_profile.copy()

    def mock_save_player_profile(**kwargs):
        saved_data.update(kwargs)

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        mock_fetch_player_profile,
    )

    monkeypatch.setattr(
        main,
        "save_player_profile",
        mock_save_player_profile,
    )

    response = client.put(
        "/api/profile",
        json={
            "username": "NewGamer",
            "favorite_genre": "Racing",
            "preferred_difficulty": "Easy",
            "preferred_play_style": "Casual",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully!"
    assert response.json()["profile"]["username"] == "NewGamer"

    assert calls["count"] == 2

    assert saved_data["username"] == "NewGamer"
    assert saved_data["favorite_genre"] == "Racing"
    assert saved_data["achievements"] == []
    assert saved_data["points"] == 0


def test_update_existing_player_profile(monkeypatch):
    calls = {"count": 0}
    updated_data = {}

    def mock_fetch_player_profile():
        calls["count"] += 1

        return {
            "username": "OldGamer",
            "favorite_genre": "Action",
            "achievements": [],
            "points": 100,
            "preferred_difficulty": "Hard",
            "preferred_play_style": "Competitive",
        }

    def mock_update_player_profile(**kwargs):
        updated_data.update(kwargs)

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        mock_fetch_player_profile,
    )

    monkeypatch.setattr(
        main,
        "update_player_profile",
        mock_update_player_profile,
    )

    response = client.put(
        "/api/profile",
        json={
            "username": "NewGamer",
            "favorite_genre": "Racing",
            "preferred_difficulty": "Easy",
            "preferred_play_style": "Casual",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully!"
    assert response.json()["profile"]["username"] == "OldGamer"

    assert calls["count"] == 2
    assert updated_data["username"] == "NewGamer"
    assert updated_data["favorite_genre"] == "Racing"
    assert updated_data["preferred_difficulty"] == "Easy"
    assert updated_data["preferred_play_style"] == "Casual"


def test_update_profile_fails_when_updated_profile_missing(monkeypatch):
    calls = {"count": 0}

    def mock_fetch_player_profile():
        calls["count"] += 1

        if calls["count"] == 1:
            return {
                "username": "OldGamer",
                "favorite_genre": "Action",
                "achievements": [],
                "points": 100,
                "preferred_difficulty": "Hard",
                "preferred_play_style": "Competitive",
            }

        return None

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        mock_fetch_player_profile,
    )

    monkeypatch.setattr(
        main,
        "update_player_profile",
        lambda **kwargs: None,
    )

    response = client.put(
        "/api/profile",
        json={
            "username": "NewGamer",
            "favorite_genre": "Racing",
            "preferred_difficulty": "Easy",
            "preferred_play_style": "Casual",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to retrieve updated player profile.")
    assert calls["count"] == 2


def test_update_profile_handles_database_error(monkeypatch):
    def mock_fetch_player_profile():
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        mock_fetch_player_profile,
    )

    response = client.put(
        "/api/profile",
        json={
            "username": "NewGamer",
            "favorite_genre": "Racing",
            "preferred_difficulty": "Easy",
            "preferred_play_style": "Casual",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Database error while updating player profile."
    )


def test_unlock_achievement_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        main,
        "unlock_player_achievement",
        lambda **kwargs: (None, False),
    )

    response = client.post("/api/profile/achievement")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Player profile not found.",
        "profile": None,
    }


def test_unlock_achievement_already_unlocked(monkeypatch):
    test_profile = {
        "username": "TestGamer",
        "favorite_genre": "Action",
        "achievements": ["Gaming Champion"],
        "points": 500,
    }

    monkeypatch.setattr(
        main,
        "unlock_player_achievement",
        lambda **kwargs: (["Gaming Champion"], False),
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: test_profile,
    )

    response = client.post("/api/profile/achievement")

    assert response.status_code == 200
    assert response.json()["message"] == ("Achievement already unlocked!")
    assert response.json()["profile"]["username"] == "TestGamer"


def test_unlock_achievement_successfully(monkeypatch):
    test_profile = {
        "username": "TestGamer",
        "favorite_genre": "Action",
        "achievements": ["Gaming Champion"],
        "points": 500,
    }

    saved_data = {}

    def mock_unlock_player_achievement(**kwargs):
        saved_data.update(kwargs)
        return ["Gaming Champion"], True

    monkeypatch.setattr(
        main,
        "unlock_player_achievement",
        mock_unlock_player_achievement,
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: test_profile,
    )

    response = client.post("/api/profile/achievement")

    assert response.status_code == 200
    assert response.json()["message"] == ("Achievement unlocked! +500 points")
    assert response.json()["profile"]["username"] == "TestGamer"
    assert saved_data["achievement_name"] == "Gaming Champion"
    assert saved_data["points_to_add"] == 500


def test_unlock_achievement_updated_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        main,
        "unlock_player_achievement",
        lambda **kwargs: (["Gaming Champion"], True),
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    response = client.post("/api/profile/achievement")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to retrieve updated player profile.")


def test_unlock_achievement_database_error(monkeypatch):
    def mock_unlock_player_achievement(**kwargs):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "unlock_player_achievement",
        mock_unlock_player_achievement,
    )

    response = client.post("/api/profile/achievement")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Database error while unlocking achievement.")


def test_mini_game_points_player_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        main,
        "add_mini_game_points_to_database",
        lambda points: None,
    )

    response = client.post(
        "/api/profile/mini-game-points",
        json={"points": 100},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Player profile not found!"


def test_mini_game_points_updated_profile_not_found(monkeypatch):
    monkeypatch.setattr(
        main,
        "add_mini_game_points_to_database",
        lambda points: True,
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    response = client.post(
        "/api/profile/mini-game-points",
        json={"points": 100},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to retrieve updated player profile.")


def test_mini_game_points_successfully_updated(monkeypatch):
    test_profile = {
        "username": "TestGamer",
        "favorite_genre": "Action",
        "points": 600,
        "mini_game_points": 200,
    }

    monkeypatch.setattr(
        main,
        "add_mini_game_points_to_database",
        lambda points: True,
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: test_profile,
    )

    response = client.post(
        "/api/profile/mini-game-points",
        json={"points": 100},
    )

    assert response.status_code == 200
    assert response.json()["message"] == ("Mini-game points added successfully!")
    assert response.json()["profile"]["username"] == "TestGamer"
    assert response.json()["profile"]["mini_game_points"] == 200


def test_mini_game_points_database_error(monkeypatch):
    def mock_add_mini_game_points(points):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "add_mini_game_points_to_database",
        mock_add_mini_game_points,
    )

    response = client.post(
        "/api/profile/mini-game-points",
        json={"points": 100},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Database error while adding mini-game points."
    )


def test_leaderboard_not_found(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "points": 500,
        },
    )

    monkeypatch.setattr(
        main,
        "save_leaderboard_score",
        lambda username, points: None,
    )

    monkeypatch.setattr(
        main,
        "fetch_leaderboard",
        lambda: None,
    )

    response = client.get("/api/leaderboard")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to retrieve leaderboard.")


def test_leaderboard_database_error(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "TestGamer",
            "points": 500,
        },
    )

    monkeypatch.setattr(
        main,
        "save_leaderboard_score",
        lambda username, points: None,
    )

    def mock_fetch_leaderboard():
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "fetch_leaderboard",
        mock_fetch_leaderboard,
    )

    response = client.get("/api/leaderboard")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Database error while retrieving leaderboard.")


def test_mini_game_points_internal_validation():
    invalid_data = main.MiniGamePoints.model_construct(points=0)

    with pytest.raises(main.HTTPException) as exc_info:
        main.add_mini_game_points(invalid_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid points value!"


def test_chat_endpoint_preserves_http_exception(monkeypatch):
    def mock_generate_chat_reply(chat):
        raise main.HTTPException(
            status_code=418,
            detail="Test HTTP exception",
        )

    monkeypatch.setattr(
        main,
        "generate_chat_reply",
        mock_generate_chat_reply,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 418
    assert response.json()["detail"] == "Test HTTP exception"


def test_chat_endpoint_database_error(monkeypatch):
    def mock_generate_chat_reply(chat):
        raise RuntimeError("Unexpected server error")

    monkeypatch.setattr(
        main,
        "generate_chat_reply",
        mock_generate_chat_reply,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Database or server error while processing chat."
    )


def test_generate_chat_reply_whitespace_message():
    chat = main.ChatMessage(message="   ")

    response = main.generate_chat_reply(chat)

    assert response == {"reply": "Please enter a message!"}


def test_generate_chat_reply_combined_genre_difficulty(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {
            "username": "AmitGamer",
            "preferred_play_style": "Competitive",
        },
    )

    monkeypatch.setattr(
        main,
        "generate_hybrid_recommendations",
        lambda genre, difficulty, play_style: (
            genre,
            [
                {
                    "name": "Battle Zone",
                    "match_percentage": 100,
                    "recommendation_reason": "Matches your preferences.",
                }
            ],
        ),
    )

    response = main.generate_chat_reply(main.ChatMessage(message="Hard Action"))

    assert "Hard Action games" in response["reply"]
    assert "Battle Zone" in response["reply"]
    assert "100% match" in response["reply"]


def test_generate_chat_reply_combined_preferences_no_profile(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    response = main.generate_chat_reply(main.ChatMessage(message="Hard Action"))

    assert response == {"reply": "Player profile not found."}


def test_generate_chat_reply_recommendation_no_profile(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda username, message, reply: None,
    )

    response = main.generate_chat_reply(main.ChatMessage(message="Recommend a game"))

    assert response == {"reply": "Player profile not found."}


def test_generate_chat_reply_easy_games(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda username, message, reply: None,
    )

    response = main.generate_chat_reply(main.ChatMessage(message="Show me easy games"))

    assert "Cyber Chess" in response["reply"]
    assert "Speed Legends" in response["reply"]
    assert "Easy difficulty" in response["reply"]


def test_generate_chat_reply_easy_games_fallback(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda username, message, reply: None,
    )

    response = main.generate_chat_reply(main.ChatMessage(message="easy"))

    assert "Cyber Chess" in response["reply"]
    assert "Speed Legends" in response["reply"]


def test_generate_chat_reply_default_response(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "save_chat_message",
        lambda username, message, reply: None,
    )

    response = main.generate_chat_reply(
        main.ChatMessage(message="Tell me something interesting")
    )

    assert "GameVerse AI gaming assistant" in response["reply"]
    assert "gaming tips" in response["reply"]


def test_get_chat_history_returns_none(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {"username": "AmitGamer"},
    )

    monkeypatch.setattr(
        main,
        "fetch_chat_history",
        lambda username: None,
    )

    with pytest.raises(main.HTTPException) as exc_info:
        main.get_chat_history()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == ("Unable to retrieve chat history.")


def test_get_chat_history_database_exception(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: {"username": "AmitGamer"},
    )

    def mock_fetch_chat_history(username):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "fetch_chat_history",
        mock_fetch_chat_history,
    )

    with pytest.raises(main.HTTPException) as exc_info:
        main.get_chat_history()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == ("Database error while retrieving chat history.")


def test_hybrid_recommendations_no_matching_preferences(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "similarity_scores",
        [0] * len(main.GAMES),
        raising=False,
    )


def test_hybrid_recommendations_zero_similarity(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "cosine_similarity",
        lambda player_vector, game_vectors: [[0.0] * len(main.GAMES)],
    )

    _, recommendations = main.generate_hybrid_recommendations(
        "Any",
        "Any",
        "Any",
    )
    assert all(game["similarity_score"] == 0 for game in recommendations)

    assert len(recommendations) > 0

    assert all(
        game["recommendation_reason"]
        == "This game does not closely match your selected preferences."
        for game in recommendations
    )


def test_hybrid_recommendations_similarity_explanation(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "cosine_similarity",
        lambda player_vector, game_vectors: [[0.5] * len(main.GAMES)],
    )

    _, recommendations = main.generate_hybrid_recommendations(
        "Any",
        "Any",
        "Any",
    )

    assert len(recommendations) > 0

    assert all(game["similarity_score"] == 50 for game in recommendations)

    assert all(
        game["recommendation_reason"]
        == (
            "Recommended because its game features show similarity to your preferences."
        )
        for game in recommendations
    )


@pytest.mark.parametrize(
    "message, expected",
    [
        ("racing", "Neon Racer"),
        ("adventure", "Shadow Quest"),
        ("strategy", "Cyber Chess"),
        ("action", "Battle Zone"),
        ("exploration", "Galaxy Explorer"),
    ],
)
def test_chat_game_category_replies(monkeypatch, message, expected):
    monkeypatch.setattr(
        main,
        "detect_chat_intent",
        lambda message: "general",
    )

    monkeypatch.setattr(
        main,
        "fetch_player_profile",
        lambda: None,
    )

    chat = main.ChatMessage(message=message)
    result = main.generate_chat_reply(chat)

    assert expected in result["reply"]


def test_get_recommendation_history_none(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_recommendation_history",
        lambda: None,
    )

    response = client.get("/api/recommendation-history")

    assert response.status_code == 500
    assert response.json()["detail"] == ("Unable to retrieve recommendation history.")


def test_get_recommendation_history_database_error(monkeypatch):
    def raise_database_error():
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main,
        "fetch_recommendation_history",
        raise_database_error,
    )

    response = client.get("/api/recommendation-history")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Database error while retrieving recommendation history."
    )
