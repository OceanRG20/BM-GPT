from flask import Flask, request

app = Flask(__name__)

@app.route("/bookmap", methods=["POST"])
def handle_bookmap_data():
    data = request.get_json()
    print("✅ Received from Bookmap:", data)
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(port=5005)
