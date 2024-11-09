from flask import Blueprint, request, jsonify
from backend.db import get_db_connection
from backend.models.sesion import Sesion
from backend.models.auth import token_required
from datetime import datetime

docente_blueprint = Blueprint('docente', __name__)