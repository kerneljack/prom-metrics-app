from flask import render_template, redirect, url_for, request, current_app
from app.main import bp, metrics
import time

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@metrics.http_request_time_summary.time()
@metrics.http_request_time_histogram.time()
def index():
    template = render_template('index.html', title='Home')

    metrics.inc_http_success_counter()
    metrics.inc_http_total_counter()
    return template

@bp.route('/do_task', methods=['GET', 'POST'])
@metrics.http_request_time_summary.time()
@metrics.http_request_time_histogram.time()
def do_task():
    process_request(5)
    template = render_template('do_task.html', title='Do task')

    metrics.inc_http_success_counter()
    metrics.inc_http_total_counter()
    return template


@metrics.http_request_time_summary.time()
@metrics.http_request_time_histogram.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)
