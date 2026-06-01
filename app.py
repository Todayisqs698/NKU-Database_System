from flask import Flask
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Register blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.steward import steward_bp
from routes.public import public_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(steward_bp)
app.register_blueprint(public_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
