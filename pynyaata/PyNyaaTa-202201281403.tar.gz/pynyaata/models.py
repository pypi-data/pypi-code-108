from .config import db


class AnimeFolder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(
        length=100,
        collation='utf8mb4_general_ci'
    ), unique=True, nullable=False)
    path = db.Column(db.String(length=100, collation='utf8mb4_general_ci'))
    titles = db.relationship(
        "AnimeTitle",
        backref="folder",
        cascade='all,delete-orphan'
    )


class AnimeTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(
        length=100,
        collation='utf8mb4_general_ci'
    ), unique=True, nullable=False)
    keyword = db.Column(db.Text(
        collation='utf8mb4_general_ci'
    ), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('anime_folder.id'))
    links = db.relationship(
        'AnimeLink',
        backref="title",
        cascade='all,delete-orphan'
    )


class AnimeLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    season = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    comment = db.Column(db.Text(collation='utf8mb4_general_ci'))
    vf = db.Column(db.Boolean, nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('anime_title.id'))


def create_all():
    db.create_all()
