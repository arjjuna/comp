from flask import Blueprint

mybp = Blueprint('mybp', __name__)

from . import views, errors