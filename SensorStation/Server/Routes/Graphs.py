from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from django.http import HttpResponse
import json, orjson
import sqlite3, ast
import pandas as pd



