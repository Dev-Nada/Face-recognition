import sqlite3

db = "attendance.db"


def get_connection():
    connection = sqlite3.connect(db)
    connection.row_factory = sqlite3.Row
    return connection
