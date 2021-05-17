import json
from api.db.purchase import Purchase


class InvalidRequestError(Exception):
  pass


class PurchaseNotFoundError(Exception):
  pass


class Sale(object):
  def __init__(self, app, request, response) -> None:
    self._purchase = Purchase()
    self._request = request
    self._response = response
    self._response.headers["Content-type"] = "application/json"
    app.route("/sale", methods=["POST"], endpoint="finish_sale")(self.finish_sale)
    app.route("/sale/<purchase_id>", methods=["GET"], endpoint="get_sale")(self.get)

  def finish_sale(self):
    try:
      data = self._request.json
      if "products" not in data:
        raise InvalidRequestError("Request must contain a product list")
      products = data["products"]
      sale = self._purchase.create_purchase(products)
      return json.dumps({"success": True, "sale": sale})
    except InvalidRequestError as e:
      self._response.set_data(json.dumps({"error": str(e)}))
      self._response.status_code = 422
      return self._response
    except Exception as e:
      self._response.set_data(json.dumps({"error": str(e)}))
      self._response.status_code = 500
      return self._response

  def get(self, purchase_id):
    try:
      purchase = self._purchase.get_purchase(purchase_id)
      if purchase is None:
        raise PurchaseNotFoundError(f"Purchase with id '{purchase_id}' was not found.")
      self._response.set_data(json.dumps(purchase))
      self._response.status_code = 200
      return self._response
    except PurchaseNotFoundError as e:
      self._response.set_data(json.dumps({"error": str(e)}))
      self._response.status_code = 404
      return self._response
    except Exception as e:
      self._response.set_data(json.dumps({"error": str(e)}))
      self._response.status_code = 500
      return self._response
