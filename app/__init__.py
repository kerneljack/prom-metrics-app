import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from config import Config
from app.tracing import init_tracing
from app.metrics import get_backend_type


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_tracing(app)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    # Add prometheus wsgi middleware to route /metrics requests (only for prometheus backend)
    if get_backend_type() == "prometheus":
        from werkzeug.middleware.dispatcher import DispatcherMiddleware
        from prometheus_client import make_wsgi_app
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

    if not app.debug and not app.testing:
        if app.config["LOG_TO_STDOUT"]:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/prom-metrics-app.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s "
                    "[in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("prom-metrics-app startup")

    return app
