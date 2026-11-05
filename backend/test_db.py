
import psycopg

try:
    connection = psycopg.connect(
        dbname="gameverse_ai",
        user="postgres",
        password="Am!?t@76",
        host="localhost",
        port="5432"
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_history (
            id SERIAL PRIMARY KEY,
            genre VARCHAR(50),
            difficulty VARCHAR(50),
            play_style VARCHAR(50),
            recommendations JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    connection.commit()

    print("Recommendation history table created successfully!")

    cursor.close()
    connection.close()

except Exception as error:
    print("Database error:", error)

