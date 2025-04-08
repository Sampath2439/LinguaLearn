"""
Shared extensions and configurations for the application.
This helps avoid circular imports by placing shared objects in a separate file.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Create the database extension
db = SQLAlchemy(model_class=Base)