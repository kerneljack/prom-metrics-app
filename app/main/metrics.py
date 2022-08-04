from prometheus_client import Summary, Counter, Histogram


class Metrics:
    # success / total metrics
    http_success_counter = Counter("http_successful_access", "Successful HTTP counts")
    http_total_counter = Counter("http_total_access", "Total HTTP counts")

    # error tracking metrics
    http_4xx_errors_counter = Counter("http_access_error_4xx", "Description of counter")
    http_5xx_errors_counter = Counter("http_access_error_5xx", "Description of counter")

    # Create a metric to track time spent and requests made.
    http_request_time_histogram = Histogram(
        "request_processing_seconds", "Time spent processing request (Histogram)"
    )
