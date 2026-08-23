import sqlite3

connection = sqlite3.connect("database.db")

connection.execute(
    "ALTER TABLE subjects ADD COLUMN class_id INTEGER"
)

connection.commit()

print("class_id added to subjects!")

connection.close()