import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from flasgger import Swagger, swag_from
from flask_jwt_extended import JWTManager
from flask import Flask, jsonify, redirect
from src.config.swagger import template, swagger_config
from src.constants.http_status_code import (
    HTTP_200_OK, 
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)

# this function takes a config
def create_app(test_config=None):    
    # instance_relative_config=True } tell that we might have some configurations that are gonna be defined in some files
    app = Flask(__name__, instance_relative_config=True)
    
    # configuring secreat key
    if test_config is None:
        app.config.from_mapping(
            SECREAT_KEY=os.getenv("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
            SWAGGER = {
                "title":"Bookmarks API",
                "uiversion":3
                }
        )
        
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config=swagger_config, template=template)

    @app.route("/<short_url>", methods=['GET'])
    @swag_from("/home/hardikve/Desktop/LINK_SAVER_WEB_APP/src/docs/bookmarks/short_url.yaml")
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits+1
            db.session.commit()

            return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({"error":"Not Found."}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({"error":"Something went wrong we are working on it."}), HTTP_500_INTERNAL_SERVER_ERROR

    app.app_context().push()
    return app
