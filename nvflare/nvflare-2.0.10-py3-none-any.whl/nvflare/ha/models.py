import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

# print(app.config)

app.config.from_mapping(
    SECRET_KEY=os.environ.get("SECRET_KEY") or "dev_key",
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(os.getcwd(), "status.sqlite"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)
# migrate = Migrate()


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hot_sp = db.Column(db.String(80), nullable=True)

    def __repr__(self):
        return f"<id: {self.id}, hot_sp: {self.hot_sp}>"
