from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models import Task, db

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["GET"])
@jwt_required()
def list_tasks():
    user_id = int(get_jwt_identity())
    tasks = Task.query.filter_by(owner_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400

    task = Task(title=title, notes=data.get("notes"), owner_id=user_id)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(task_id)

    if task.owner_id != user_id and not get_jwt().get("is_admin"):
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json()
    if "title" in data:
        task.title = data["title"]
    if "notes" in data:
        task.notes = data["notes"]
    if "completed" in data:
        task.completed = data["completed"]

    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.get_or_404(task_id)

    if task.owner_id != user_id and not get_jwt().get("is_admin"):
        return jsonify({"error": "forbidden"}), 403

    db.session.delete(task)
    db.session.commit()
    return "", 204
