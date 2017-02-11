from flask import Blueprint

prof = Blueprint('prof', __name__)

from . import views, errors