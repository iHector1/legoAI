from flask import request, jsonify
import firebase_admin
from firebase_admin import db, credentials

#auth credentials
cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred, { "databaseURL": "https://legoia-default-rtdb.firebaseio.com/" })


ref = db.reference("/")
def register_routes(app):
    @app.route("/api/v1/legoia", methods=["GET"])
    def get_legoia():
        return jsonify(ref.get())
    
    @app.route("/api/v1/legoia", methods=["POST"])
    def post_legoia():
        data = request.json
        ref.push(data)
        return jsonify(data)

    @app.route("/api/v1/legoia/<string:id>", methods=["PUT"])
    def put_legoia(id):
        data = request.json
        ref.child(id).update(data)
        return jsonify(data)

    @app.route("/api/v1/legoia/<string:id>", methods=["DELETE"])
    def delete_legoia(id):
        ref.child(id).delete()
        return jsonify({ "message": "Deleted" })
