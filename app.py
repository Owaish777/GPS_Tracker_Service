from flask import Flask
from routes import session_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register the routes blueprint
app.register_blueprint(session_bp)

if __name__ == "__main__":
    app.run(debug=True)
