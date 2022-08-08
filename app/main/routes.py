from flask import render_template
from app.main import bp, metrics
import time


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@metrics.http_request_time_histogram.time()
def index():
    metrics.http_successful_request.inc()
    metrics.http_requests.inc()

    return render_template("index.html", title="Home", metrics=metrics)


@bp.route("/do_task", methods=["GET", "POST"])
@metrics.http_request_time_histogram.time()
def do_task():
    process_request(5)

    metrics.http_successful_request.inc()
    metrics.http_requests.inc()

    return render_template("do_task.html", title="Do task", metrics=metrics)


@metrics.http_request_time_histogram.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)
