from prometheus_client import Summary, Counter, Histogram

class Metrics():
    # success / total metrics
    http_success_counter = Counter('http_access_success', 'Description of counter')
    http_total_counter = Counter('http_access_total', 'Description of counter')

    # error tracking metrics
    http_4xx_errors_counter = Counter('http_access_error_4xx', 'Description of counter')
    http_5xx_errors_counter = Counter('http_access_error_5xx', 'Description of counter')

    # Create a metric to track time spent and requests made.
    http_request_time_summary = Summary('request_processing_seconds_s', 'Time spent processing request (Summary)')
    http_request_time_histogram = Histogram('request_processing_seconds_h', 'Time spent processing request (Histogram)')

    def inc_http_success_counter(self):
        self.http_success_counter.inc()

    def inc_http_total_counter(self):
        self.http_total_counter.inc()

    def inc_http_4xx_errors_counter(self):
        self.http_4xx_errors_counter.inc()

    def inc_http_5xx_errors_counter(self):
        self.http_5xx_errors_counter.inc()

