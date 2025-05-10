from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Hello World mit Animation</title>
    <style>
        @keyframes slide-in {
            0%   { transform: translateY(-100px); opacity: 0; }
            100% { transform: translateY(0);      opacity: 1; }
        }
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #6B73FF, #000DFF);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        h1 {
            font-size: 4rem;
            animation: slide-in 1s ease-out forwards;
        }
    </style>
</head>
<body>
    <h1>Hello World!</h1>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    # Für lokale Entwicklung
    app.run(host='0.0.0.0', port=5000, debug=True)
