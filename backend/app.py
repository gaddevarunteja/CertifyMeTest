from flask import Flask
from flask_cors import CORS
from models import db
from routes.auth import auth_bp
from routes.opportunities import opportunities_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certifyme.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(
    app,
    origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=True
)
app.register_blueprint(auth_bp)
app.register_blueprint(opportunities_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)