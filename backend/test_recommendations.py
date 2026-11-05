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

    selected_genre, recommendations = main.generate_hybrid_recommendations(
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

    from fastapi.testclient import TestClient


client = TestClient(main.app)


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
