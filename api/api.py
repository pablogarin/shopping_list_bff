from flask import Flask
from flask import request
from flask import Response
from flask_cors import CORS
# Resources
from api.routes.list_resource import ListResource
from api.routes.product_resource import ProductResource
from api.routes.sale import Sale


def create_flask_app():
  app = Flask(__name__)
  CORS(app)

  @app.route("/", methods=["GET"])
  def home():
    return 'UP'

  # Shopping List
  ProductResource(app, request, Response())
  ListResource(app, request, Response())
  Sale(app, request, Response())

  return app
