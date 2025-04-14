# data_integration/roles.py
from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {
        'scrape_data': True,
    }

class User(AbstractUserRole):
    available_permissions = {
        'view_data': True,
    }