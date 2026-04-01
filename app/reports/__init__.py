from flask import Blueprint
reports = Blueprint('reports', __name__, template_folder='../../templates/reports')
from app.reports import routes
