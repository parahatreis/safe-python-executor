from flask import Flask

app = Flask(__name__)

from app.api.routes import bp as api_bp
app.register_blueprint(api_bp)
