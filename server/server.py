from flask import request
from flask import jsonify
from flask import send_file
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson.binary import Binary
from dotenv import load_dotenv
from datetime import datetime

import cv2 as cv
import numpy as np
import re
import base64
import math
import random
import copy
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import io
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from backend import create_app

app = create_app()

# Generate pdf

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9050)

# Activate environment with flask
# source venv/bin/activate

# Run flask server
# python3 -m flask --app server run --host=0.0.0.0 --port=9050
# or 
# python3 server.py

# http request endpoint
# http://192.168.1.103:9050
