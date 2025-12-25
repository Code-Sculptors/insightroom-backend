from flask import Blueprint

conferences_bp = Blueprint('conferences', __name__)

from . import routes, sockets