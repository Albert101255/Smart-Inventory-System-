from flask import Blueprint
products = Blueprint('products', __name__, template_folder='../../templates/products')
from app.products import routes
