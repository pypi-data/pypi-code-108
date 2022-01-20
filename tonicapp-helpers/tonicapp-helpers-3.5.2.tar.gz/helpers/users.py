import hashlib

default_salt: str = "3CD13NwnvxQmwc3WLaeE"


def get_user_id_with_uid(user_hash, salt=default_salt, user_dict=None):
    """
      params: user_hash and salt
      return: user_id
    """
    while len(user_hash) < 32:
        user_hash = f'0{user_hash}'

    if user_dict is None:
        user_dict = generate_id_dict(salt)

    return user_dict[user_hash]


def generate_id_dict(salt=default_salt):
    users = {}

    for i in range(200000):
        text = str(i) + salt
        hash_object = hashlib.md5(text.encode('utf-8'))
        users[hash_object.hexdigest()] = str(i)

    return users


def get_user_hash(id, salt=default_salt):
    to_hash = str(id) + salt
    return hashlib.md5(to_hash.encode('utf-8')).hexdigest()
