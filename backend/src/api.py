import os
from flask import Flask, request, jsonify, abort
from flask.json import tojson_filter
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#To reset Database uncomment following line:
# db_drop_and_create_all() 

def retrieve_short_drinks():
    drinks = Drink.query.all()
    short_drinks = []
    
    for drink in drinks:
        short_drinks.append(drink.short())

    return short_drinks

def retrieve_long_drinks():
    drinks = Drink.query.all()
    long_drinks = []

    for drink in drinks:
        long_drinks.append(drink.long())

    return long_drinks

# ROUTES

@app.route('/drinks', methods=['GET'])
def retrieve_drinks():
    try:
        short_drinks = retrieve_short_drinks()

        if len(short_drinks) == 0:
            abort(404)

        else:
            return jsonify({
                'success': True,
                'drinks': short_drinks
            }), 200

    except Exception as error:
        print(error)
        abort(422) #not able to process request

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        long_drinks = retrieve_long_drinks()

        if len(long_drinks) == 0:
            abort(404)
        
        else:
            return jsonify({
                'success': True,
                'drinks': long_drinks
            }), 200

    except Exception as error:
        print(error)
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):

    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')

    try:
        drink = Drink(
            title = new_title,
            recipe = json.dumps(new_recipe)
        )
        drink.insert()
        
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    
    except Exception as error:
        print(error)
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):

    body = request.form
    new_title = body.get('title')
    new_recipe = body.get('recipe')

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
        else:
            drink.title = new_title
            if new_recipe is not None:
                drink.recipe = json.dumps(new_recipe)
            drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except Exception as error:
        print(error)
        abort(422)
        
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        else:
            drink.delete()
        
        return jsonify({
            'success': True,
            'delete': drink.id
        }), 200

    except Exception as error:
        print(error)
        abort(422)



# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):

    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(500)
def server_error(error):

    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }), 404

@app.errorhandler(AuthError)
def AuthError(error):
    return jsonify (error.error), error.status_code
