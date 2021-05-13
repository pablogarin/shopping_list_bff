from api.routes.resource import ResourceInterface
from api.db.list import ShoppingList
from api.db.list import ShoppingListModel
import json


class ListItemNotFoundError(Exception):
  pass


class ListResource(ResourceInterface):
  def __init__(self, app, request, response):
    self._shopping_list = ShoppingList()
    self._setup(app, "/list", request, response)
  
  def get(self, resource_id=None):
    try:
      item = self._shopping_list.fetch_by_id(resource_id)
      if not item:
        raise ListItemNotFoundError("Item not found")
      self._response.set_data(json.dumps(dict(item)))
    except ListItemNotFoundError as e:
      self._response.set_data(json.dumps({"error": "Item not Found"}))
      self._response.status_code = 404
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response

  def get_all(self):
    try:
      items = self._shopping_list.fetch_all()
      self._response.set_data(json.dumps(items))
      self._response.status_code = 200
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response

  def create(self):
    try:
      data = self._request.json
      item = ShoppingListModel(data)
      res = self._shopping_list.save(item)
      item = self._shopping_list.fetch_by_id(res)
      self._response.set_data(json.dumps(dict(item)))
      self._response.status_code = 200
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response
  
  def update(self, resource_id=None):
    try:
      item = self._shopping_list.fetch_by_id(resource_id)
      if not item:
        raise ListItemNotFoundError("Item not found")
      data = self._request.json
      item.set_from_dict(data)
      res = self._shopping_list.save(item)
      item.id = res
      item = self._shopping_list.fetch_by_id(resource_id)
      print(data, dict(item))
      self._response.set_data(json.dumps(dict(item)))
      self._response.status_code = 200
    except ListItemNotFoundError as e:
      self._response.set_data(json.dumps({"error": "Item not Found"}))
      self._response.status_code = 404
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response
  
  def delete(self, resource_id=None):
    try:
      item = self._shopping_list.fetch_by_id(resource_id)
      if not item:
        raise ListItemNotFoundError("Item not found")
      self._shopping_list.delete(resource_id)
      self._response.set_data(json.dumps({"deleted": True, "id": resource_id}))
      self._response.status_code = 200
    except ListItemNotFoundError as e:
      self._response.set_data(json.dumps({"error": "Item not Found"}))
      self._response.status_code = 404
    except Exception as e:
      self._response.set_data(json.dumps({"error": e.message}))
      self._response.status_code = 500
    return self._response
  
