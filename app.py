from flask import Flask
from routes import session_bp

app = Flask(__name__)

# Register the routes blueprint
app.register_blueprint(session_bp)

if __name__ == "__main__":
    app.run(debug=True)
