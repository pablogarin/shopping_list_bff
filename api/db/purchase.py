from typing import List
from api.db.invalid_id_error import InvalidIDError
from api.utils.config import get_env
import sqlite3
import os


class PurchaseModel(object):
  _id = None
  _datetime = None

  def __init__(self, data):
    self.set_from_dict(data)
    
  def set_from_dict(self, data):
    self.id = data["id"]
    self.datetime = data["datetime"]

  @property
  def id(self):
    return self._id

  @id.setter
  def id(self, id):
    self._id = id

  @property
  def datetime(self):
    return self._datetime

  @datetime.setter
  def datetime(self, datetime):
    self._datetime = datetime
  
  def __iter__(self):
    data = {
      "id": self._id,
      "datetime": self._datetime
    }
    for key, value in data.items():
      yield (key, value)


class Purchase(object):
  _purchase_table = "purchase"
  _purchase_schema = f"CREATE TABLE IF NOT EXISTS {_purchase_table}(\n"\
    "   id integer PRIMARY KEY AUTOINCREMENT,\n"\
    "   datetime integer NOT NULL\n"\
    ");"
  
  _purchase_products_table = "purchase_product"
  _purchase_products_schema = f"CREATE TABLE IF NOT EXISTS {_purchase_products_table}(\n"\
    f"   id integer PRIMARY KEY AUTOINCREMENT,\n"\
    f"   purchase_id integer NOT NULL,\n"\
    f"   product_id integer NOT NULL,\n"\
    f"   quantity integer NOT NULL,\n"\
    f"   FOREIGN KEY(purchase_id) REFERENCES {_purchase_table}(id),\n"\
    f"   FOREIGN KEY(product_id) REFERENCES product(id)\n"\
    f");"

  def __init__(self) -> None:
    self._db_path = get_env("DB_PATH")
    if not os.path.isfile(self._db_path):
      with open(self._db_path, "w"):
        pass
    self._conn = sqlite3.connect(self._db_path)
    try:
      self._conn.row_factory = sqlite3.Row
      cursor = self._conn.cursor()
      cursor.execute(self._purchase_schema)
      cursor.execute(self._purchase_products_schema)
    except Exception as e:
      print(e)
  
  def execute_read(self, query):
    result = []
    try:
      self._conn = sqlite3.connect(self._db_path)
      self._conn.row_factory = sqlite3.Row
      c = self._conn.cursor()
      c.execute(query)
      while True:
        row = c.fetchone()
        if row is None:
          break
        result.append(dict(row))
    except Exception as e:
      print("Error writing into database: %s" % e)
    return result
  
  def execute_mutation(self, query):
    try:
      self._conn = sqlite3.connect(self._db_path)
      c = self._conn.cursor()
      res = c.execute(query)
      self._conn.commit()
      return c.lastrowid
    except Exception as e:
      print("Error writing into database: %s" % e)
  
  def create_purchase(self, products):
    query = f"INSERT OR REPLACE\n" \
      f"INTO {self._purchase_table}\n" \
      f"VALUES(\n" \
      f"   (SELECT MAX(id) FROM {self._purchase_table}) + 1,\n" \
      f"   datetime()\n" \
      f");"
    try:
      purchase_id = self.execute_mutation(query)
      if purchase_id:
        for product in products:
          self._insert_purchase_product(purchase_id, product)
      result = self.get_purchase(purchase_id)
      return result
    except Exception as e:
      print(e, query)
  
  def _insert_purchase_product(self, purchase_id, product):
    product_id = product["id"]
    quantity = product["quantity"]
    query = f"INSERT OR REPLACE\n" \
      f"INTO {self._purchase_products_table}\n" \
      f"VALUES(\n" \
      f"   (SELECT MAX(id) FROM {self._purchase_products_table}) + 1,\n" \
      f"   {purchase_id},\n" \
      f"   {product_id},\n" \
      f"   {quantity}\n" \
      f");"
    self.execute_mutation(query)
    query = f"DELETE FROM shopping_list WHERE product_id = {product_id};"
    self.execute_mutation(query)
    query = f"UPDATE product SET lastPurchase = datetime() WHERE id = {product_id};"
    self.execute_mutation(query)

  def get_purchase(self, purchase_id):
    rows = self.execute_read(f"SELECT * FROM  purchase WHERE id = {purchase_id};")
    if rows:
      purchase = rows[0] 
      query = f"SELECT\
        product.name,\
        purchase_product.quantity\
        FROM purchase_product\
        LEFT JOIN product ON product.id = purchase_product.product_id\
        WHERE purchase_id = {purchase_id}"
      product_list = self.execute_read(query)
      purchase["products"] = product_list
      return purchase
    return None