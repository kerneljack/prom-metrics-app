from flask import Blueprint
from app.main.metrics import Metrics

bp = Blueprint("main", __name__)

metrics = Metrics()

from app.main import routes
