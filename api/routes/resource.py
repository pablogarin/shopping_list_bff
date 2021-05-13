from abc import ABC
from abc import abstractmethod


class ResourceInterface(ABC):
  def _setup(self, app, path, request, response):
    self._request = request
    self._response = response
    self._response.headers["Content-type"] = "application/json"
    self._set_routes(path, app)

  def _set_routes(self, path, app):
    class_prefix = self.__class__.__name__
    app.route(
      f"{path}",
      methods=["GET"],
      endpoint=f"{class_prefix}_get_all")(self.get_all)
    app.route(
      f"{path}/<resource_id>",
      methods=["GET"],
      endpoint=f"{class_prefix}_get")(self.get)
    app.route(
      f"{path}",
      methods=["POST"],
      endpoint=f"{class_prefix}_post")(self.create)
    app.route(
      f"{path}/<resource_id>",
      methods=["PUT"],
      endpoint=f"{class_prefix}_put")(self.update)
    app.route(
      f"{path}/<resource_id>",
      methods=["DELETE"],
      endpoint=f"{class_prefix}_delete")(self.delete)
  
  @abstractmethod
  def get(self):
    pass

  @abstractmethod
  def get_all(self):
    pass

  @abstractmethod
  def create(self):
    pass

  @abstractmethod
  def update(self):
    pass

  @abstractmethod
  def delete(self):
    pass