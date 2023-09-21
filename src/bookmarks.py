import validators
from flask.json import jsonify  
from flasgger import swag_from
from flask import Blueprint, request
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from src.constants.http_status_code import (
    HTTP_400_BAD_REQUEST, 
    HTTP_409_CONFLICT, 
    HTTP_201_CREATED, 
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND
)

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route("/",methods=['GET','POST']) 
@jwt_required() 
def handle_bookmarks():

    current_user = get_jwt_identity()

    # If POST than user is trying to create a new link
    if request.method == 'POST':
        body = request.get_json().get("body", "")
        url = request.get_json().get("url", "")
        
        if not validators.url(url):
            return ({"error": "Enter valid URL."}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return ({"error": "URL already exists."}), HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            "id":bookmark.id, 
            "url":bookmark.url, 
            "short_url":bookmark.short_url, 
            "visit":bookmark.visits, 
            "body":bookmark.body, 
            "created_at":bookmark.created_at, 
            "updated_at":bookmark.updated_at
        }), HTTP_201_CREATED

    else:
        page = request.args.get("page",1,type=int)
        per_page = request.args.get("per_page",5,type=int)

        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
        
        data = []
        for bookmark in bookmarks.items:
            data.append({
                "id":bookmark.id, 
                "url":bookmark.url, 
                "short_url":bookmark.short_url, 
                "visit":bookmark.visits, 
                "body":bookmark.body, 
                "created_at":bookmark.created_at, 
                "updated_at":bookmark.updated_at
            })

        meta = {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "prev_page":bookmarks.prev_num,
            "next_page":bookmarks.next_num,
            "has_next":bookmarks.has_next,
            "has_prev":bookmarks.has_prev
        }

        return jsonify({"data":data, "meta":meta}), HTTP_200_OK

@bookmarks.route("/<int:id>", methods=['GET'])
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"message":"Item not found."}), HTTP_404_NOT_FOUND

    return jsonify({
            "id":bookmark.id, 
            "url":bookmark.url, 
            "short_url":bookmark.short_url, 
            "visit":bookmark.visits, 
            "body":bookmark.body, 
            "created_at":bookmark.created_at, 
            "updated_at":bookmark.updated_at
        }), HTTP_200_OK

@bookmarks.route("/<int:id>", methods=['PUT','PATCH'])
@jwt_required()
def editbookmark(id):
    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"message":"Item not found."}), HTTP_404_NOT_FOUND

    body = request.get_json().get("body", "")
    url = request.get_json().get("url", "")
    
    if not validators.url(url):
        return ({"error": "Enter valid URL."}), HTTP_400_BAD_REQUEST

    bookmark.url=url
    bookmark.body=body

    db.session.commit()

    return jsonify({
        "id":bookmark.id, 
        "url":bookmark.url, 
        "short_url":bookmark.short_url, 
        "visit":bookmark.visits, 
        "body":bookmark.body, 
        "created_at":bookmark.created_at, 
        "updated_at":bookmark.updated_at
    }), HTTP_200_OK

@bookmarks.route("/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({"message":"Item not found."}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@bookmarks.route("/stats",methods=['GET'])
@jwt_required()
@swag_from("/home/hardikve/Desktop/LINK_SAVER_WEB_APP/src/docs/bookmarks/stats.yaml")
def get_stats():
    # this will return link and how many time its visited
    data = []
    current_user = get_jwt_identity()

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for i in items:
        new_link = {
            "visits":i.visits,
            "url":i.url,
            "id":i.id,
            "short_url":i.short_url
            }
        data.append(new_link)

    return jsonify({"data":data}), HTTP_200_OK