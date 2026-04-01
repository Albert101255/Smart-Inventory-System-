from flask import Blueprint
stock = Blueprint('stock', __name__, template_folder='../../templates/stock')
from app.stock import routes
