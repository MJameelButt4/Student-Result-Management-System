from database import get_db_connection
from werkzeug.security import generate_password_hash

connection = get_db_connection()

hashed_password = generate_password_hash("admin123")

connection.execute(
    """
    UPDATE users
    SET password = ?
    WHERE username = ?
    """,
    (hashed_password, "admin")
)

connection.commit()
connection.close()

print("Admin password migrated successfully!")