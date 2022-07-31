from flask import Blueprint
from app.main.prom_metrics import Metrics

bp = Blueprint('main', __name__)

metrics = Metrics()

from app.main import routes
