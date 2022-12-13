import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/Bookkeeper-Server/venv/lib/python3.8/site-packages")
sys.path.insert(0, "/var/www/Bookkeeper-Server")

from main import app as application
