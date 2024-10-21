from flask_frozen import Freezer
from app import app, dashboard  # Import your Flask app and routes

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()