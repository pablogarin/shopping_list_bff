from flask import Flask
from flask import request
from flask import Response
from flask_cors import CORS
from api.routes.product_resource import ProductResource
from api.routes.list_resource import ListResource


def create_flask_app():
  app = Flask(__name__)
  app.config["DEBUG"] = True
  CORS(app)

  @app.route("/", methods=["GET"])
  def home():
    return 'UP'

  # Shopping List
  ProductResource(app, request, Response())
  ListResource(app, request, Response())

  return app
