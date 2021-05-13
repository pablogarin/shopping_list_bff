import json
from api.db.product import Product
from api.db.product import ProductModel
from api.routes.resource import ResourceInterface


class ItemNotFoundError(Exception):
  pass


class ProductResource(ResourceInterface):
  def __init__(self, app, request, response):
    self._product = Product()
    self._setup(app, "/product", request, response)

  def get(self, resource_id=None):
    try:
      item = self._product.fetch_by_id(resource_id)
      if not item:
        raise ItemNotFoundError("Item not found")
      self._response.set_data(json.dumps(dict(item)))
    except ItemNotFoundError as e:
      self._response.set_data(json.dumps({"error": "Item not Found"}))
      self._response.status_code = 404
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response

  def get_all(self):
    try:
      items = self._product.fetch_all()
      self._response.set_data(json.dumps(items))
      self._response.status_code = 200
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response

  def create(self):
    try:
      data = self._request.json
      item = ProductModel(data)
      res = self._product.save(item)
      item = self._product.fetch_by_id(res)
      self._response.set_data(json.dumps(dict(item)))
      self._response.status_code = 200
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response
  
  def update(self, resource_id=None):
    try:
      item = self._product.fetch_by_id(resource_id)
      if not item:
        raise ItemNotFoundError("Item not found")
      data = self._request.json
      item.set_from_dict(data)
      res = self._product.save(item)
      item.id = res
      item = self._product.fetch_by_id(resource_id)
      self._response.set_data(json.dumps(dict(item)))
      self._response.status_code = 200
    except ItemNotFoundError as e:
      self._response.set_data(json.dumps({"error": "Item not Found"}))
      self._response.status_code = 404
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response
  
  def delete(self, resource_id=None):
    try:
      item = self._product.fetch_by_id(resource_id)
      if not item:
        raise ItemNotFoundError("Item not found")
      self._product.delete(resource_id)
      self._response.set_data(json.dumps({"deleted": True, "id": resource_id}))
      self._response.status_code = 200
    except ItemNotFoundError as e:
      self._response.set_data(json.dumps({"error": "Item not Found"}))
      self._response.status_code = 404
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response
