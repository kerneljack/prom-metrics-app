from flask import Blueprint
from app.metrics import get_metrics_backend

bp = Blueprint("main", __name__)

metrics = get_metrics_backend()

from app.main import routes
