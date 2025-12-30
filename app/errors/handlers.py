from flask import render_template
from app.errors import bp
from app.metrics import get_metrics_backend


@bp.app_errorhandler(404)
def not_found_error(error):
    metrics = get_metrics_backend()
    with metrics.time_request():
        metrics.inc_4xx()
        metrics.inc_requests()
        return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    metrics = get_metrics_backend()
    with metrics.time_request():
        metrics.inc_5xx()
        metrics.inc_requests()
        return render_template("errors/500.html"), 500
