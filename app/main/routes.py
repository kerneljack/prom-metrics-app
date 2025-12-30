from flask import render_template
from app.main import bp, metrics
import time


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@metrics.time_request_decorator()
def index():
    metrics.inc_successful()
    metrics.inc_requests()

    return render_template("index.html", title="Home")


@bp.route("/view_metrics", methods=["GET", "POST"])
def view_metrics():
    summary = metrics.get_metrics_summary()
    return render_template("view_metrics.html", title="View Metrics", metrics_summary=summary)


@bp.route("/do_task", methods=["GET", "POST"])
@metrics.time_request_decorator()
def do_task():
    process_request(5)

    metrics.inc_successful()
    metrics.inc_requests()

    return render_template("do_task.html", title="Do task")


def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)
