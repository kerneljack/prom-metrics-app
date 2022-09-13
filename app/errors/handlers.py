from flask import render_template
from app.errors import bp
from app.main import metrics

@bp.app_errorhandler(404)
@metrics.http_request_time_histogram.time()
def not_found_error(error):
    template = render_template("errors/404.html"), 404
    metrics.http_4xx_errors.inc()
    metrics.http_requests.inc()

    return template


@bp.app_errorhandler(500)
def internal_error(error):
    template = render_template("errors/500.html"), 500
    metrics.http_5xx_errors.inc()
    metrics.http_requests.inc()

    return template
