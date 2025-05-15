import os
from flask import Flask
app = Flask(__name__)


app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")
@app.route("/")
def home():
    return "Hello, CATAMS!"

@app.route("/health")

def health():

        return {"status": "ok"}, 200



if __name__ == "__main__":
    app.run(debug=True)

