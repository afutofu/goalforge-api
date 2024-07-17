from flask import Blueprint, request, jsonify
from middleware.token_required import token_required
from database import db
from models import Goal
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

goals_blueprint: Blueprint = Blueprint("goals", __name__)


# Get user's goals from the database
# Example: GET /api/v1/goals
@goals_blueprint.route("", methods=["GET"])
@token_required
def get_goals(current_user):

    # Logic to fetch goals based on the period
    goals = []
    goals = (
        Goal.query.filter_by(user_id=current_user["userID"])
        .order_by(Goal.created_at.asc())
        .all()
    )

    goals = [goal.to_dict() for goal in goals]

    # print("goals:", goals)

    return jsonify(goals), 200


# Add goals to the database
# Example: POST /api/v1/goals
# Takes in a JSON object with the following keys:
# - name: string
# - color: boolean
@goals_blueprint.route("", methods=["POST"])
@token_required
def add_goal(current_user):
    goal = request.json
    if "name" not in goal:
        response = {"error": "'name' is required"}
        return jsonify(response), 400

    if "color" not in goal:
        response = {"error": "'color' is required"}
        return jsonify(response), 400

    name = goal["name"].strip()
    color = goal["color"].strip()

    if name == "":
        response = {"error": "'name' cannot be empty"}
        return jsonify(response), 400

    if color == "":
        response = {"error": "'color' cannot be empty"}
        return jsonify(response), 400

    current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Create a new goal object
    new_goal = Goal(
        name=goal["name"],
        color=goal["color"],
        user_id=current_user["userID"],
        created_at=current_utc_time,
        updated_at=current_utc_time,
    )

    db.session.add(new_goal)
    db.session.commit()

    return jsonify(new_goal.to_dict()), 201


# Update goals from the database
# Example: PUT /api/v1/goals/goal_id
# Takes in a JSON object with the following:
# - name: string
# - color: boolean
@goals_blueprint.route("/<string:goal_id>", methods=["PUT"])
@token_required
def update_goal(current_user, goal_id):
    print("GOAL ID:", goal_id)

    updated_goal = request.json

    if goal_id is None:
        response = {"error": "goal ID is required"}
        return jsonify(response), 400

    if "name" not in updated_goal:
        response = {"error": "'name' is required"}
        return jsonify(response), 400

    if "color" not in updated_goal:
        response = {"error": "'color' is required"}
        return jsonify(response), 400

    name = updated_goal["name"].strip()
    color = updated_goal["color"].strip()

    if name == "":
        response = {"error": "'name' cannot be empty"}
        return jsonify(response), 400

    if color == "":
        response = {"error": "'color' cannot be empty"}
        return jsonify(response), 400

    found_goal = Goal.query.filter_by(
        user_id=current_user["userID"], id=goal_id
    ).first()

    if not found_goal:
        return jsonify({"error": "goal not found"}), 404

    found_goal.name = updated_goal["name"]
    found_goal.color = updated_goal["color"]
    found_goal.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    db.session.commit()

    print("Updated Goal:", found_goal.to_dict())

    return jsonify(found_goal.to_dict()), 200


# Delete goals from the database
# Example: DELETE /api/v1/goals/goal_id
@goals_blueprint.route("/<string:goal_id>", methods=["DELETE"])
@token_required
def delete_goal(current_user, goal_id):

    if goal_id is None:
        response = {"error": "Goal ID is required"}
        return jsonify(response), 400

    found_goal = Goal.query.filter_by(
        user_id=current_user["userID"], id=goal_id
    ).first()

    if not found_goal:
        return jsonify({"error": "Goal not found"}), 404

    db.session.delete(found_goal)
    db.session.commit()

    return jsonify({"message": "Goal deleted successfully"}), 200
