from flask import Flask, g
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Teardown database connection
    @app.teardown_appcontext
    def close_db(error):
        if 'db' in g:
            g.db.close()

    return app

# Database connection function
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('instance/Checkpoint3.db')
        g.db.row_factory = sqlite3.Row  # Enables access by column name
    return g.db

# Cursor retrieval function
def get_cursor():
    return get_db().cursor()
