from flask import Blueprint

routes = Blueprint('routes', __name__)
auth = Blueprint('auth', __name__)
home = Blueprint('home', __name__)
users = Blueprint('users', __name__)
loans = Blueprint('loans', __name__)
contribution = Blueprint('contribution', __name__)
reminder = Blueprint('reminders', __name__)
meetings = Blueprint('meetings', __name__)
settings = Blueprint('settings', __name__)