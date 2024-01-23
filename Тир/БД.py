import sqlite3


def get_points():
    fileBD = sqlite3.connect("База данных.db")
    cursor = fileBD.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY,
                point INTEGER NOT NULL)''')
    cursor.execute("SElECT * FROM points")
    spisok = cursor.fetchall()
    fileBD.close()
    return spisok

def connection_BD(points):
    fileBD = sqlite3.connect("База данных.db")
    cursor = fileBD.cursor()
    cursor.execute("INSERT INTO points (point) VALUES (?)", [points])
    fileBD.commit()
    fileBD.close()