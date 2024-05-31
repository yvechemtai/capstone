from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class BaseMixin:
  id = db.Column(db.Interger, primary_key=True)
  deleted = db.Column(db.Boolean, nullable=False, default=False)
  created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
  updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, **kwargs):
    for attr, value in kwargs.items():
      setattr(self, attr, value)
    db.session.commit()

  def delete(self):
    #db.session.delete(self)
    self.deleted = True
    db.session.commit()



class Users(db.Modal, BaseMixin):
  __tablename__ = 'users'

  email = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  first_name = db.Column(db.String(20))
  last_name = db.Column(db.String(20))
  is_admin = db.Column(db.Boolean, nullable=False)

class Products(db.Modal, BaseMixin):
  __tablename__ = 'products'

  name = db.Column(db.String(50), unique=True, nullable=False)
  price = db.Column(db.Interger, nullable=False)
  quantity = db.Column(db.Interger, nullable=False)

class Orders(db.Modal, BaseMixin):
  __tablename__ = 'orders'

  customer_id = db.Column(db.String(50), unique=True, nullable=False)
  product_id = db.Column(db.String(50), unique=True, nullable=False)
  unit_price = db.Column(db.Interger, nullable=False)
  total_price = db.Column(db.Interger, nullable=False)
  quantity = db.Column(db.Interger, nullable=False)
  status = db.Column(db.Boolean, nullable=False, default='Pending')

class Payments(db.Modal, BaseMixin):
  __tablename__ = 'payments'

  customer_id = db.Column(db.String(50), unique=True, nullable=False)
  order_id = db.Column(db.Interger, nullable=False)
  amount = db.Column(db.Interger, nullable=False)
  transaction_id = db.Column(db.Interger, nullable=False)
