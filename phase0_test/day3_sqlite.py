import sqlite3

# Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect("app.db")

# Cursor lets us execute SQL commands
cursor = conn.cursor()

print("Database connected successfully")

# cursor.execute("""
# CREATE TABLE users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     email TEXT UNIQUE               
# )
# """)

conn.commit()
print("Users table created")

# cursor.execute("""
# INSERT INTO users (name, email)
# VALUES (?,?)
# """, ("Alice", "alice@gmail.com"))

conn.commit()
print("User inserted")

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.execute("""
UPDATE users
SET name = ?
WHERE id = ? 
""", ("Alice Smith", 1))

conn.commit()
print("User updated")

cursor.execute("""
DELETE FROM users
WHERE id = ?
""", (1,))

conn.commit()
print("User deleted")

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print("After delete:", rows)

conn.close()
print("Database connection closed")