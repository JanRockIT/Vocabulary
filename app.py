from flask import Flask
import os

app = Flask(__name__)

@app.get("/")
def hello_world():
    return """
    <body style="text-align: center; font-family: courier new, consolas, "consolas", "currier new";">
        <strong>
            <h1 style="font-size: 65px; color: grey; margin-top: 20%;">Welcome to the vocabulary API</h1>
        </strong>
    </body>""", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render gibt $PORT vor
    app.run(host="0.0.0.0", port=port)
