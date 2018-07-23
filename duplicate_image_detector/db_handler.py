import os
import sqlite3

class ImagesDB(object):
    def __init__(self, dbFileName="images_info.db"):            
        self.dbFileName = dbFileName
        if os.path.exists(self.dbFileName):
            os.remove(self.dbFileName)

        self.conn = sqlite3.connect(self.dbFileName)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS IMAGES(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        count           INT      NOT NULL,
        name            TEXT       NOT NULL
        )''')
        

    def insert_in_db(self, count, name):
        self.cursor.execute("INSERT INTO IMAGES VALUES (NULL, ?, ?)", (count, name))
        conn.commit()
        conn.close()

    def insert_batch(self, batch):
        for record in batch:
            self.insert_in_db(record[1], record[0])

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        self.conn.commit()
        self.conn.close()
        del self.cursor
        del self.conn