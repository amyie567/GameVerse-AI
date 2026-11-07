import os

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

# Load environment variables from .env
load_dotenv()

# Local PostgreSQL configuration
DATABASE_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "5432")),
}


def get_db_connection():
    # Use Neon PostgreSQL when DATABASE_URL is available.
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(database_url, sslmode="require")

    # Otherwise, use local PostgreSQL.
    return psycopg.connect(**DATABASE_CONFIG)


def save_recommendation_history(genre, difficulty, play_style, recommendations):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO recommendation_history
                (genre, difficulty, play_style, recommendations)
                VALUES (%s, %s, %s, %s)
                """,
            (genre, difficulty, play_style, Jsonb(recommendations)),
        )


def fetch_recommendation_history():
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT id, genre, difficulty, play_style,
                       recommendations, created_at
                FROM recommendation_history
                ORDER BY created_at DESC, id DESC
                """
        )
        rows = cursor.fetchall()

    history = []

    for row in rows:
        history.append(
            {
                "id": row[0],
                "genre": row[1],
                "difficulty": row[2],
                "play_style": row[3],
                "recommendations": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
            }
        )

    return history


def save_player_profile(username, favorite_genre, achievements, points):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO player_profile
                (username, favorite_genre, achievements, points)
                VALUES (%s, %s, %s, %s)
                """,
            (username, favorite_genre, Jsonb(achievements), points),
        )


def fetch_player_profile():
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT id, username, favorite_genre,
                       achievements, points, mini_game_points,
                       preferred_difficulty, preferred_play_style
                FROM player_profile
                ORDER BY id ASC
                LIMIT 1
                """
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "username": row[1],
        "favorite_genre": row[2],
        "achievements": row[3],
        "points": row[4],
        "mini_game_points": row[5],
        "preferred_difficulty": row[6],
        "preferred_play_style": row[7],
    }


def update_player_profile(
    username, favorite_genre, preferred_difficulty, preferred_play_style
):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                UPDATE player_profile
                SET username = %s,
                    favorite_genre = %s,
                    preferred_difficulty = %s,
                    preferred_play_style = %s
                WHERE id = (
                    SELECT id
                    FROM player_profile
                    ORDER BY id ASC
                    LIMIT 1
                )
                """,
            (username, favorite_genre, preferred_difficulty, preferred_play_style),
        )


def unlock_player_achievement(achievement_name, description, icon, points_to_add):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT achievements
                FROM player_profile
                ORDER BY id ASC
                LIMIT 1
                """
        )

        row = cursor.fetchone()

        if row is None:
            return None, False

        achievements = row[0] or []

        already_unlocked = any(
            item["name"] == achievement_name for item in achievements
        )

        if already_unlocked:
            return achievements, False

        achievements.append(
            {"name": achievement_name, "description": description, "icon": icon}
        )

        cursor.execute(
            """
                UPDATE player_profile
                SET achievements = %s,
                    points = points + %s
                WHERE id = (
                    SELECT id
                    FROM player_profile
                    ORDER BY id ASC
                    LIMIT 1
                )
                """,
            (Jsonb(achievements), points_to_add),
        )

        return achievements, True


def add_mini_game_points(points_to_add):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                UPDATE player_profile
                SET mini_game_points = mini_game_points + %s,
                    points = points + %s
                WHERE id = (
                    SELECT id
                    FROM player_profile
                    ORDER BY id ASC
                    LIMIT 1
                )
                RETURNING id
                """,
            (points_to_add, points_to_add),
        )

        return cursor.fetchone()


def save_leaderboard_score(username, points):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO leaderboard (username, points)
                VALUES (%s, %s)
                ON CONFLICT (username)
                DO UPDATE SET
                    points = EXCLUDED.points
                """,
            (username, points),
        )


def fetch_leaderboard():
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT username, MAX(points) AS points
                FROM leaderboard
                GROUP BY username
                ORDER BY points DESC
                LIMIT 10
                """
        )

        rows = cursor.fetchall()

    return [{"username": row[0], "points": row[1]} for row in rows]


def save_chat_message(username, user_message, assistant_response):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO chat_history
                (username, user_message, assistant_response)
                VALUES (%s, %s, %s)
                """,
            (username, user_message, assistant_response),
        )


def fetch_chat_history(username):
    with get_db_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT id, user_message, assistant_response, created_at
                FROM chat_history
                WHERE username = %s
                ORDER BY created_at DESC, id DESC
                LIMIT 50
                """,
            (username,),
        )
        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_message": row[1],
            "assistant_response": row[2],
            "created_at": row[3].isoformat(),
        }
        for row in rows
    ]
