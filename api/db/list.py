from typing import List
from api.db.invalid_id_error import InvalidIDError
from api.utils.config import get_env
import sqlite3
import os


class ShoppingListModel(object):
  _id = None
  _product_id = None
  _needed = None
  _purchased = None

  def __init__(self, data):
    self.set_from_dict(data)

  def set_from_dict(self, data):
    if "id" in data.keys():
      self.id = data["id"]
    self.product_id = data["product_id"]
    self.needed = data["needed"]
    purchased = 0
    if "purchased" in data.keys():
      purchased = data["purchased"]
    self.purchased = purchased

  @property
  def id(self):
    return self._id
  
  @id.setter
  def id(self, id):
    self._id = id
  
  @property
  def product_id(self):
    return self._product_id

  @product_id.setter
  def product_id(self, product_id):
    self._product_id = product_id

  @property
  def needed(self):
    return self._needed

  @needed.setter
  def needed(self, needed):
    self._needed = needed

  @property
  def purchased(self):
    return self._purchased

  @purchased.setter
  def purchased(self, purchased):
    self._purchased = purchased
  
  def __iter__(self) -> dict:
    data = {
      "id": self.id,
      "product_id": self.product_id,
      "needed": self.needed,
      "purchased": self.purchased
    }
    for key in data.keys():
      yield (key, data[key])
  

ShoppingListGroup = List[ShoppingListModel]


class ShoppingList(object):
  _table = "shopping_list"
  _schema = "CREATE TABLE IF NOT EXISTS shopping_list(\n" \
        "   id integer primary key autoincrement,\n" \
        "   product_id integer,\n"\
        "   needed int,\n"\
        "   purchased int,\n"\
        "   FOREIGN KEY(product_id) REFERENCES product(id)\n"\
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
  
  def fetch_all(self) -> ShoppingListGroup:
    self._conn = sqlite3.connect(self._db_path)
    shopping_list = []
    try:
      self._conn.row_factory = sqlite3.Row
      c = self._conn.cursor()
      c.execute(f"SELECT * FROM {self._table};")
      while True:
        row = c.fetchone()
        if row is None:
          break
        item = dict(ShoppingListModel(row))
        shopping_list.append(item)
    except Exception as e:
      print(f"Error reading database: {e}")
    return shopping_list
  
  def fetch_by_id(self, id_) -> ShoppingListModel:
    if not id_:
      raise InvalidIDError("You must provide an ID")
    self._conn = sqlite3.connect(self._db_path)
    result = None
    try:
      self._conn.row_factory = sqlite3.Row
      c = self._conn.cursor()
      c.execute(f"SELECT * FROM {self._table} WHERE id={id_};")
      while True:
        row = c.fetchone()
        if row is None:
          break
        result = ShoppingListModel(row)
    except Exception as e:
      print(f"Error reading database: {e}")
    return result
  
  def save(self, item: ShoppingListModel):
    self._conn = sqlite3.connect(self._db_path)
    query = f"INSERT OR REPLACE\n" \
      f"INTO {self._table}\n" \
      f"VALUES(\n" \
      f"   COALESCE(\n" \
      f"       (SELECT id FROM {self._table} WHERE product_id={item.product_id}),\n" \
      f"       (SELECT MAX(id) FROM {self._table}) + 1\n" \
      f"   ),\n" \
      f"   {item.product_id},\n" \
      f"   {item.needed},\n" \
      f"   {item.purchased}\n" \
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
