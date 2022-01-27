import os
from datetime import date, datetime

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("SECRET_KEY") or "dev_key",
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(os.getcwd(), "status.sqlite"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy(app)
db.drop_all()
db.create_all()


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


app.json_encoder = CustomJSONEncoder


class SP(db.Model):
    service_point = db.Column(db.String(80), primary_key=True)
    project = db.Column(db.String(20), primary_key=True)
    state = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    last_update = db.Column(db.DateTime(), onupdate=datetime.utcnow)
    hot = db.Column(db.Boolean(), default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Heartbeat(db.Model):
    project = db.Column(db.String(20), primary_key=True)
    reporter = db.Column(db.String(20), primary_key=True)
    last_beat = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        req = request.json
        role = req.get("role", None)
        if role == "server":
            service_point = req.get("service_point", "")
            project = req.get("project", "")
            sp = SP.query.filter_by(service_point=service_point, project=project).first()
            sp.state = "registered"
            sp.hot = True
            db.session.commit()
            sps = SP.query.all()
            hot_sp = ""
            for sp in sps:
                if sp.hot:
                    hot_sp = sp.service_point
                    break
            return jsonify({"hot_sp": hot_sp, "all_sp": [item.as_dict() for item in SP.query.all()]})


if __name__ == "__main__":
    app.run(ssl_context=("./sds.crt", "./server.key"))
