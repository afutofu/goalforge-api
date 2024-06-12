from flask import Blueprint, request, jsonify
from middleware.token_required import token_required
from database import db
from models import Category
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
from models import Category

categories_blueprint: Blueprint = Blueprint("categories", __name__)


# Get user's categories from the database
# Example: GET /api/v1/categories
@categories_blueprint.route("", methods=["GET"])
@token_required
def get_categories(current_user):

    # Logic to fetch categories based on the period
    categories = []
    categories = (
        Category.query.filter_by(user_id=current_user["userID"])
        .order_by(Category.created_at.desc())
        .all()
    )

    categories = [category.to_dict() for category in categories]

    # print("categories:", categories)

    return jsonify(categories), 200


# Add categories to the database
# Example: POST /api/v1/categories
# Takes in a JSON object with the following keys:
# - name: string
# - color: boolean
@categories_blueprint.route("", methods=["POST"])
@token_required
def add_category(current_user):
    category = request.json
    if "name" not in category:
        response = {"error": "'name' is required"}
        return jsonify(response), 400

    if "color" not in category:
        response = {"error": "'color' is required"}
        return jsonify(response), 400

    name = category["name"].strip()
    color = category["color"].strip()

    if name == "":
        response = {"error": "'name' cannot be empty"}
        return jsonify(response), 400

    if color == "":
        response = {"error": "'color' cannot be empty"}
        return jsonify(response), 400

    # Create a new category object
    new_category = Category(
        name=category["name"],
        color=category["color"],
        user_id=current_user["userID"],
    )

    db.session.add(new_category)
    db.session.commit()

    return jsonify(new_category.to_dict()), 201


# Update categories from the database
# Example: PUT /api/v1/categories/category_id
# Takes in a JSON object with the following:
# - name: string
# - color: boolean
@categories_blueprint.route("/<string:category_id>", methods=["PATCH"])
@token_required
def update_category(current_user, category_id):
    print("CATEGORY ID:", category_id)

    updated_category = request.json

    if category_id is None:
        response = {"error": "Category ID is required"}
        return jsonify(response), 400

    if "name" not in updated_category:
        response = {"error": "'name' is required"}
        return jsonify(response), 400

    if "color" not in updated_category:
        response = {"error": "'color' is required"}
        return jsonify(response), 400

    name = updated_category["name"].strip()
    color = updated_category["color"].strip()

    if name == "":
        response = {"error": "'name' cannot be empty"}
        return jsonify(response), 400

    if color == "":
        response = {"error": "'color' cannot be empty"}
        return jsonify(response), 400

    found_category = Category.query.filter_by(
        user_id=current_user["userID"], id=category_id
    ).first()

    if not found_category:
        return jsonify({"error": "Category not found"}), 404

    found_category.name = updated_category["name"]
    found_category.color = updated_category["color"]
    found_category.updated_at = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    db.session.commit()

    print("Updated Category:", found_category.to_dict())

    return jsonify(found_category.to_dict()), 200


# Delete categories from the database
# Example: DELETE /api/v1/categories/category_id
@categories_blueprint.route("/<string:category_id>", methods=["DELETE"])
@token_required
def delete_category(current_user, category_id):

    if category_id is None:
        response = {"error": "Category ID is required"}
        return jsonify(response), 400

    found_category = Category.query.filter_by(
        user_id=current_user["userID"], id=category_id
    ).first()

    if not found_category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(found_category)
    db.session.commit()

    return jsonify({"message": "Category deleted successfully"}), 200
