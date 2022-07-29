from flask import render_template, redirect, url_for, request, current_app
from app.main import bp
from prometheus_client import Summary
import random
import time


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')

@bp.route('/time', methods=['GET', 'POST'])
def time():
    return process_request(random.random())


# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)