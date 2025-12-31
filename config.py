import os
import secrets

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
    METRICS_BACKEND = os.environ.get("METRICS_BACKEND", "prometheus")
