from flask_login import UserMixin
from flask_login import  LoginManager

class UserUtils(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id, db_session):
        user = db_session.execute(
            "SELECT * FROM public.users WHERE id = '{}'".format(user_id)
        ).fetchone()
        if not user:
            return None

        user = UserUtils(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic, db_session):
        db_session.execute(
            "INSERT INTO public.users (id, name, email, profile_pic) "
            "VALUES ('{}', '{}', '{}', '{}')".format(id_, name, email, profile_pic)
        )
        db_session.commit()
