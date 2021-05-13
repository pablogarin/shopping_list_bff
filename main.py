from api.api import create_flask_app


if __name__ == "__main__":
  app = create_flask_app()
  app.run(port=5012)