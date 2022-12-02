import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
with app.app_context():
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,PATCH,POST,DELETE,OPTIONS"
        )
        return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        requires the 'get:drinks' permission which is public
        Contains the short drink data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/cafe_api/v1.01/drinks", methods=['GET'])
def retrieve_drinks():
    drinks = Drink.query.order_by(Drink.title).all()
    if drinks is None:
        return jsonify(
            {
                "success": True,
                "dirnks": None,
            }
        )
    else:
        return jsonify(
            {
                "success": True,
                "dirnks": drinks.short(),
            }
        )

'''
    GET /drinks-detail
        requires the 'get:drinks-detail' permission
        Contains the long drink data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/cafe_api/v1.01/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail():
    drinks = Drink.query.order_by(Drink.title).all()
    if drinks is None:
        return jsonify(
            {
                "success": True,
                "drinks": None,
            }
        )
    else:
        return jsonify(
            {
                "success": True,
                "dirnks": drinks.long(),
            }
        )

'''
    POST /drinks
        requires the 'post:drinks' permission
        Create a new row in the drinks table
        Output of drinks contains the long data representation
        Responds with a 422 error if drink already exists
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/cafe-api/v1.01/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink():
    try:
        body = request.get_json()
        data = []
        new_title = body.get("title", None)
        new_recipe = body.get("recipe", None)

        existing_drink = Drink.query.filter(Drink.title==new_title, Drink.recipe==new_recipe).one_or_none()
        if existing_drink is not None:
            print('drink already exists!!')
            abort(422)

        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        data.append(drink)

        return jsonify(
            {
                "success": True,
                "drinks": data,
            }
        )

    except:
        abort(422)


'''
    PATCH /drinks/<id>
        requires the 'patch:drinks' permission
        updates the drink DB referenced by <drink_id>
        Responds with a 404 error if <drink_id> is not found      
        Return of drinks contains the long data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/cafe_api/v1.01/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            print('Did not find drink for update. id = ', str(drink_id))
            abort(404)

        body = request.get_json()
        print("post:drinks for id: ", str(drink_id), ' with json body: ', body)

        drink.title = body['title']
        drink.recipe = body['recipe']
        drink.update()

        return jsonify(
            {
                "success": True,
                "drinks": drink.long(),
            }
        )

    except:
        print('caught exception in update_question')
        abort(422)

'''
    DELETE /drinks/<id>
        Requires the 'delete:drinks' permission
        Deletes the record in drink matching <drink_id>
        Responds with a 404 error if <drink_id> is not found
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/cafe_api/v1.01/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if question is None:
            print('Did not find drink for delete. id = ', str(question_id))
            abort(404)

        drink.delete()

        return jsonify(
            {
                "success": True,
                "delete": id,
            }
        )

    except:
        print('caught exception in delete_question')
        abort(422)


# Error Handling
'''
error handler for 422
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
error handler for 404
'''
@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )



'''
error handler for AuthError
'''
@app.errorhandler(AuthError)
def not_found(error):
    return (
        jsonify({"success": False, "error": error, "message": AuthError.description}),
        error,
    )
