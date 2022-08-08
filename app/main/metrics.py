from prometheus_client import Summary, Counter, Histogram


class Metrics:
    # success / total metrics
    http_successful_request = Counter("http_successful_request", "Successful HTTP counts")
    http_requests = Counter("http_requests", "Total HTTP counts")

    # error tracking metrics
    http_4xx_errors = Counter("http_error_4xx", "Description of counter")
    http_5xx_errors = Counter("http_error_5xx", "Description of counter")

    # Create a metric to track time spent and requests made.
    http_request_time_histogram = Histogram(
        "request_processing_seconds", "Time spent processing request (Histogram)"
    )
