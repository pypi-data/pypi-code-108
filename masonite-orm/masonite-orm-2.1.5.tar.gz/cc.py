"""Sandbox experimental file used to quickly feature test features of the package
"""

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.connections import MySQLConnection, PostgresConnection
from src.masoniteorm.query.grammars import MySQLGrammar, PostgresGrammar
from src.masoniteorm.models import Model
from src.masoniteorm.models.Pivot import Pivot
from src.masoniteorm.relationships import has_many, belongs_to_many, belongs_to, has_one
from src.masoniteorm.scopes import SoftDeletesMixin, UUIDPrimaryKeyMixin
from src.masoniteorm.expressions import Raw
from src.masoniteorm.scopes import scope
from dotenv import load_dotenv

load_dotenv()



# class Member(Model):

#     __connection__ = "mysql"

#     __fillable__ = ["name"]

#     __table__ = "users"

#     @has_one
#     def profile(self):
#         return Profile
    
#     def set_ip_attribute(self, value):
#         import ipaddress
#         return int(ipaddress.ip_address(value))
    
#     def get_ip_attribute(self):
#         import ipaddress
#         return str(ipaddress.ip_address(self.get_raw_attribute('ip')))

class TestJSON(Model):
    __connection__ = "postgres"

    __table__ = "test_json"

    __timestamps__ = None

    __casts__ = {
        "payload": "json"
    }

class People(Model):
    __connection__ = "mysql"

    @belongs_to_many("people_id", "user_id", "people_id", "id", table="users_people", with_fields=['is_head'], with_timestamps=True)
    def users(self):
        return User


class User(Model, SoftDeletesMixin):

    __connection__ = "mysql"

    # __relationship_hidden__ = {"people": ['pivot']}

    # __force_update__ = True
    __timestamps__ = None
    __table__ = "users"
    __dates__ = ["birth_date"]

    __fillable__ = ["name", "email", "password", "remember_token"]

    @belongs_to("id", "member_id")
    def profile(self):
        return Profile

    @belongs_to_many("user_id", "people_id", "id", "people_id", table="users_people", with_fields=['is_head'], with_timestamps=True)
    def people(self):
        return People

    
class Profile(Model):
    __connection__ = "mysql"
    __timestamps__ = False

    @belongs_to("member_id", "id")
    def user(self):
        return User


# user = User()
# # profile = Profile.create({
# #     "name": "Bob Test"
# # })
# print(user)
# print(user.serialize())
# print(user.serialize())
# print(User.find(1).people.serialize())



class Permission(Model):
    __fillable__ = ['name']

    __timestamps__ = False
    
    @belongs_to_many('permission_id', 'role_id', 'id', 'role_id', pivot_id="permission_role_id", table="permission_role")
    def role(self):
        return Role

class PermissionRole(Model):
    __fillable__ = ['permission_id', 'role_id']

class Role(Model):
    __timestamps__ = False
    __hidden__ = ['name']
    __fillable__ = ['name']
    __primary_key__ = "role_id"

    @belongs_to_many('role_id', 'permission_id', 'role_id', 'id', pivot_id="permission_role_id", table="permission_role")
    def permissions(self):
        return Permission

role = Role.find(5)
print(role)

permission = Permission.find(2)
print(permission)
# role.attach('permissions', permission)
# permission.save_many('role', [role])

user = User.find(6)
profile = Profile.first()

user.attach_related('profile', profile)


# users = User.with_("people").get()
# people = People.with_('users').get()
# users = User.with_("profile").where('id', '2').get()
# for user in users:
#     # pass
#     print(user.serialize())
#     # print(user.serialize())