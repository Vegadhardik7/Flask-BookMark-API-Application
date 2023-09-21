from flask_sqlalchemy import SQLAlchemy
from flasgger import swag_from
from datetime import datetime
from enum import unique
import random
import string

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    Bookmarks = db.relationship("Bookmark", backref="user") # Bookmark relationship with user

    # string representation of model class
    def __repr__(self) -> str:
        return f"User>>> {self.user_name}"

# find relation for the bookmarks
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text(), nullable=True)
    url = db.Column(db.Text(), nullable=False)
    short_url = db.Column(db.String(5), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_url(self):
        """
        We are going to find a way of getting all the possible characters and picking random 3 from those possible characters.
        Once we picked we have to make sure that we have not picked them before.
        """
        characters = string.digits+string.ascii_letters
        picked_char = ''.join(random.choices(characters, k=3))

        # duplicate picked_char should not be in db
        link = self.query.filter_by(short_url=picked_char).first()

        if link:
            self.generate_short_url()
        else:
            return picked_char


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url = self.generate_short_url()

    # string representation of model class
    def __repr__(self) -> str:
        return f"User>>> {self.url}"