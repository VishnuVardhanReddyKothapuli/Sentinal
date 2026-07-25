"""One-time script to create the MySQL database and tables."""
import pymysql

from app.database import init_db

# Connect without specifying a database to create it
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Vishnu@123",
    port=3306,
)
cursor = conn.cursor()
cursor.execute(
    "CREATE DATABASE IF NOT EXISTS nsfw_copyright_db "
    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
)
conn.commit()
print("✅ Database 'nsfw_copyright_db' created successfully.")
cursor.close()
conn.close()

# Now let SQLAlchemy create the tables
init_db()
print("✅ Tables created successfully.")
