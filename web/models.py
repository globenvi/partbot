from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    phone = db.Column(db.String(10), nullable=True)
    telegram_id = db.Column(db.String(256), nullable=True, unique=True)
    telegram_notifications = db.Column(db.Boolean(), default=True)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(200), nullable=True)  # Tags stored as comma-separated values
    images = db.Column(db.String(500), nullable=False)  # List of image filenames
    availability = db.Column(db.String(50), nullable=False, default='in_stock')  # Default value for availability
    discount = db.Column(db.Float, nullable=False, default=0)  # Default value for discount
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Automatically set creation timestamp
