from database import get_db_connection

try:
    connection = get_db_connection()
    print("GameVerse AI database connection successful!")
    connection.close()

except Exception as error:
    print("Connection failed:", error)