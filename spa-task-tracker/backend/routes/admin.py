from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required

from models import Task, User, db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/tasks", methods=["GET"])
@jwt_required()
def all_tasks():
    # JWT claim check only — no DB re-check. If admin flag is revoked in DB
    # after login, the token still grants access until expiry. Demo point.
    if not get_jwt().get("is_admin"):
        return jsonify({"error": "forbidden"}), 403

    rows = db.session.query(Task, User.username).join(User, Task.owner_id == User.id).all()
    result = []
    for task, username in rows:
        d = task.to_dict()
        d["owner_username"] = username
        result.append(d)

    return jsonify(result), 200
