import base64
import os
import sqlite3

from dataclasses import dataclass
from datetime import datetime
from typing import List

from PyQt5.QtGui import QPixmap


@dataclass
class Media:
    title: str
    director: str
    cast: List[str]
    code: int
    date: datetime
    media_type: str
    tags: List[str]
    favourite: bool
    archive: bool
    thumb: str


def load_media_from_json(db_path: str) -> List[Media]:
    """Load media list from a JSON file."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Media")
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    media_list = [
        Media(
            title=row[column_names.index('Title')],
            director=row[column_names.index('Director')],
            cast=row[column_names.index('Cast')].split(', '),
            code=row[column_names.index('ID')],
            date=datetime.fromisoformat(row[column_names.index('Date')]),
            media_type=row[column_names.index('Type')].split(', '),
            tags=row[column_names.index('Tags')],
            favourite=row[column_names.index('Favourite')],
            archive=row[column_names.index('Archive')],
            thumb=row[column_names.index('Thumb')]
        )
        for row in data
    ]

    return media_list


def insert_row(player, file_name, code):
    conn = sqlite3.connect(player.db_path)
    cursor = conn.cursor()

    query = f"""
        INSERT INTO Media
        ("ID", "Title", "Director", "Cast", "Date", "Type", "Favourite", "Archive", "Thumb")
        VALUES ({code}, "{file_name.strip("'")}", 'Unknown', 'Unknown', '1900-01-01', 'Video', 0, 0, NULL);
    """
    cursor.execute(query)

    conn.commit()
    conn.close()


def get_thumbnail(player, code):
    conn = sqlite3.connect(player.db_path)  # use your real db path / self.conn
    try:
        row = conn.execute("SELECT Thumb FROM Media WHERE ID = ?", (code,)).fetchone()
    finally:
        conn.close()

    pixmap = QPixmap()
    thumb = row[0] if row else None
    if thumb:
        pixmap.loadFromData(base64.b64decode(thumb.split(",", 1)[-1]))
    return pixmap


def populate_thumbs(player):
    conn = sqlite3.connect(player.db_path)
    cursor = conn.cursor()

    for med in player.media:
        code = med.code
        code_path = fr"C:\Storage\Programming\ContentManager_V3\thumbs\{code}"
        if os.path.exists(code_path):
            with open(code_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                query = f"""
                    UPDATE Media
                    SET THUMB = "{b64}"
                    WHERE ID = {code};
                """
                cursor.execute(query)

        else:
            print(code_path)


    conn.commit()
    conn.close()


def update_db(player, column: str, value: str):
    conn = sqlite3.connect(player.db_path)
    cursor = conn.cursor()

    for med in player.media:
        if med.code == player.selected_media.code:
            if column == 'Title':
                med.title = value
            elif column == 'Director':
                med.director = value
            elif column == 'Cast':
                med.cast = [value]
            elif column == 'Tags':
                med.tags = value
            elif column == 'Favourite':
                med.favourite = value
            elif column == 'Archive':
                med.archive = value
            elif column == 'Thumb':
                med.thumb = value

    query = f"""
        UPDATE Media
        SET {column} = "{value}"
        WHERE ID = {player.selected_media.code};
    """
    cursor.execute(query)

    conn.commit()
    conn.close()
