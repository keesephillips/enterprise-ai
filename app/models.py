from flask_login import UserMixin

users_db = {
    "1": {"username": "testuser", "password": "password123", "id": "1"},
    "2": {"username": "admin", "password": "adminpassword", "id": "2"}
}

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    
    @staticmethod
    def get(user_id):
        user_data = users_db.get(str(user_id))
        if user_data:
            return User(id=user_data["id"], username=user_data["username"])
        return None

    @staticmethod
    def find_by_username(username):
        for _id, data in users_db.items():
            if data["username"] == username:
                return User(id=data["id"], username=data["username"])
        return None

    @staticmethod
    def check_password(username, password):
        for _id, data in users_db.items():
            if data["username"] == username and data["password"] == password:
                return True
        return False