from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, email, phone, role='user'):
        self.id = str(id) # flask_login requires a string ID usually
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role
        
class Admin(UserMixin):
    def __init__(self, id, username, role='admin'):
        self.id = f"admin_{id}" # Prefix admin ID to distinguish from user IDs
        self.admin_id = str(id)
        self.username = username
        self.role = role
