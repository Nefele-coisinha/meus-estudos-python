from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 🔥 ISSO AQUI RESOLVE

usuarios = {
    "admin": "1234"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = data.get("username")
    password = data.get("password")

    if user in usuarios and usuarios[user] == password:
        return jsonify({"status": "ok"})
    return jsonify({"status": "erro"}), 401

if __name__ == '__main__':
    app.run(debug=True)