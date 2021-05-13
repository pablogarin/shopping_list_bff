from typing import List
from api.db.invalid_id_error import InvalidIDError
from api.utils.config import get_env
import sqlite3
import os


class ProductModel(object):
  _id = None
  _name = None
  _quantity = None
  _lastPurchase = None

  def __init__(self, data):
    self.set_from_dict(data)

  def set_from_dict(self, data):
    if "id" in data.keys():
      self.id = data["id"]
    self.name = data["name"]
    self.quantity = data["quantity"]
    if "lastPurchase" in data.keys():
      self.lastPurchase = data["lastPurchase"]

  @property
  def id(self):
    return self._id
  
  @id.setter
  def id(self, id):
    self._id = id
  
  @property
  def name(self):
    return self._name
  
  @name.setter
  def name(self, name):
    self._name = name
  
  @property
  def quantity(self):
    return self._quantity
  
  @quantity.setter
  def quantity(self, quantity):
    self._quantity = quantity
  
  @property
  def lastPurchase(self):
    return self._lastPurchase
  
  @lastPurchase.setter
  def lastPurchase(self, lastPurchase):
    self._lastPurchase = lastPurchase
  
  def __iter__(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "quantity": self.quantity,
      "lastPurchase": self.lastPurchase
    }
    for key in data.keys():
      yield (key, data[key])
  

ShoppingList = List[ProductModel]


class Product(object):
  _table = "product"
  _schema = "CREATE TABLE IF NOT EXISTS product(\n" \
        "   id integer primary key autoincrement,\n" \
        "   name varchar(255),\n"\
        "   quantity int,\n"\
        "   lastPurchase datetime\n"\
        ");"

  def __init__(self):
    self._db_path = get_env("DB_PATH")
    if not os.path.isfile(self._db_path):
      with open(self._db_path, "w"):
        pass
    self._conn = sqlite3.connect(self._db_path)
    try:
      self._conn.row_factory = sqlite3.Row
      cursor = self._conn.cursor()
      cursor.execute(self._schema)
    except Exception as e:
      print(e)
  
  def fetch_all(self) -> ShoppingList:
    self._conn = sqlite3.connect(self._db_path)
    shopping_list = []
    try:
      self._conn.row_factory = sqlite3.Row
      c = self._conn.cursor()
      c.execute(f"SELECT * FROM {self._table} ORDER BY lastPurchase;")
      while True:
        row = c.fetchone()
        if row is None:
          break
        item = dict(ProductModel(row))
        shopping_list.append(item)
    except Exception as e:
      print(f"Error reading database: {e}")
    return shopping_list
  
  def fetch_by_id(self, id_) -> ProductModel:
    if not id_:
      raise InvalidIDError("You must provide an ID")
    self._conn = sqlite3.connect(self._db_path)
    result = None
    try:
      self._conn.row_factory = sqlite3.Row
      c = self._conn.cursor()
      c.execute(f"SELECT * FROM {self._table} WHERE id={id_} ORDER BY lastPurchase;")
      while True:
        row = c.fetchone()
        if row is None:
          break
        result = ProductModel(row)
    except Exception as e:
      print(f"Error reading database: {e}")
    return result
  
  def save(self, item: ProductModel):
    self._conn = sqlite3.connect(self._db_path)
    query = f"INSERT OR REPLACE\n" \
      f"INTO {self._table}\n" \
      f"VALUES(\n" \
      f"   COALESCE(\n" \
      f"       (SELECT id FROM {self._table} WHERE name='{item.name}'),\n" \
      f"       (SELECT MAX(id) FROM {self._table}) + 1\n" \
      f"   ),\n" \
      f"   '{item.name}',\n" \
      f"   {item.quantity},\n" \
      f"   datetime()\n" \
      f");"
    try:
      c = self._conn.cursor()
      res = c.execute(query)
      self._conn.commit()
      return c.lastrowid
    except Exception as e:
      print("Error writing into database: %s" % e)
  
  def delete(self, id_: int):
    print(id_)
    self._conn = sqlite3.connect(self._db_path)
    query = f"DELETE from {self._table} WHERE id={id_};"
    try:
      c = self._conn.cursor()
      res = c.execute(query)
      print(res)
      self._conn.commit()
      return c.lastrowid
    except Exception as e:
      print("Error writing into database: %s" % e)
