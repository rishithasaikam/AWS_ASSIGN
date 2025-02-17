import sys
import os
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/ubuntu/flaskapp")


from flaskapp import app as application  # Replace 'your_application' with your Flask app's module name
