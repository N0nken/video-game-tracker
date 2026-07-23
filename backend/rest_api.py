from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from database import Database
from token_manager import TokenManager

from dotenv import load_dotenv
import os


load_dotenv()


db_host = os.getenv("SQL_HOST")
db_user = os.getenv("SQL_USER")
db_password = os.getenv("SQL_PASS")
db_name = os.getenv("SQL_DATABASE")

db_encryption_key = os.getenv("DB_ENCRYPTION_SECRET")

token_secret_key = os.getenv("TOKEN_SECRET_KEY")
token_algorithm = os.getenv("TOKEN_ALGORITHM")
token_type = os.getenv("TOKEN_TYPE")


app = Flask(__name__)
CORS(app)
token_manager = TokenManager(token_secret_key, token_algorithm, token_type)
database = Database(db_host, db_user, db_password, db_name, db_encryption_key)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)


@app.route("/auth/login", methods=["POST"])
@limiter.limit("10 per hour")
def auth_login():
    if request.method == "POST":
        request_json = request.get_json()

        if ((not "email" in request_json.keys()) or
            (not "password" in request_json.keys())):

            print("invalid params")

            return jsonify({"error": "Error: Bad request"}), 400
        
        email = request_json.get("email")
        password = request_json.get("password")

        login_successful = database.login(email, password)

        if not login_successful:
            print("incorrect email/password")

            return jsonify({"error": "Invalid email or password"}), 400

        return jsonify({"token": token_manager.issue_token(3600, email, 0)}), 200


@app.route("/auth/sign_up", methods=["POST"])
@limiter.limit("10 per hour")
def auth_sign_up():
    if request.method == "POST":
        request_json = request.get_json()

        email = request_json.get("email")
        username = request_json.get("username")
        password = request_json.get("password")

        sign_up_result = database.sign_up(email, username, password)
        
        if not sign_up_result["OK"]:
            return jsonify({"error": sign_up_result["ERROR"]}), 400
        
        login_successful = database.login(email, password)

        if not login_successful:
            return jsonify({"error": "Error logging in. Try logging in again."}), 400

        return jsonify({"token": token_manager.issue_token(3600, email, 0)}), 200


@app.route("/lists", methods=["GET", "POST", "PATCH", "DELETE"])
@limiter.limit("60 per minute")
def lists():
    if request.method == "GET":
        pass
    
    if not "Token" in request.headers.keys():
        return jsonify({"error": "No token given"}), 403

    token = token_manager.verify_token(request.headers["Token"])["OK"]

    if not token["OK"]:
        return jsonify({"error": token["content"]}), 403

    user_email = token_manager.get_user_id(token["token"])

    # add list entry
    if request.method == "POST":
        # must include:
        # --- game id
        # --- status
        request_json = request.get_json()

        if ((not "game_id" in request_json.keys()) or
            (not "status" in request_json.keys())):
            return jsonify({"error": "bad request"}), 400

        game_id = request_json.get("game_id")
        status = request_json.get("status")

        # may include:
        # --- score
        # --- favourite
        # --- comment
        score = 0
        if "score" in request_json.keys():
            score = request_json.get("score")
        
        favourite = False
        if "favourite" in request_json.keys():
            favourite = request_json.get("favourite")
        
        comment = ""
        if "comment" in request_json.keys():
            comment = request_json.get("comment")
        
        result = database.track(user_email, game_id, status, score, favourite, comment)

        if result["OK"]:
            return jsonify({"error": "success"}), 200

        return jsonify({"error": result["error"]}), 400

    # update list entry
    if request.method == "PATCH":
        pass

    # delete list entry
    if request.method == "DELETE":
        pass


if __name__ == '__main__':
    app.run(debug=True)