import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # drinks = Drink.query.all()
    Drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': Drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details():
    # if 'authenticated' == True:
        drinks = Drink.query.all()
        Drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': Drinks
        })
    # else:
    #     abort(401)
                

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink():
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title is None or recipe is None:
        abort(422)

    try:
        recipe = json.dumps(recipe)

        drink = Drink(title=title, recipe=recipe)
        db.session.add(drink)
        db.session.commit()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(400)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink_details(id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    # try:
    if 'title' in body:
        drink.title = title
    if 'recipe' in body:
        drink.recipe = json.dumps(recipe)

    # db.session.add(drink)
    db.session.commit()

    return jsonify({
        'success': True,
        'drinks': drink
    })

    # except:
    #     abort(400)
# 20220804001614
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    if drink is None:
        abort(404)

    try:
        db.session.delete(drink)

        return jsonify({
            'success': True,
            'delete': drink.id
        })

    except:
        abort(400)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "page not found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def AuthError(error):
    response = jsonify(error)
    response.status_code = error.status_code
    return response


#barista token -- eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjJiWkJaVk5sOGEtdE5vTDNMVzVoWSJ9.eyJpc3MiOiJodHRwczovL2Rldi0tcnVoc3lsai51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjJkNDgyZjA2OWU5NWY2NGJlOGFhNDc4IiwiYXVkIjoiQ29mZmVlLXNob3AiLCJpYXQiOjE2NTgyMjg0MzksImV4cCI6MTY1ODIzNTYzOSwiYXpwIjoicEJUb2ptYWlUM0RCdG1Gc2Y1QVVGUkQ1ZWhCSHFHb0giLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.kZssUFysjF1Cf21QtmQFYFceje01Kl7vSGcVLvpG0Uv4JJ23v8hAlUVozUO29z-4NlmmPa5eNAkTCTVQTtgcjxC1339oohP_ewUr-2uDGhoGAAF8TrtuipHq23_MdTF0Ya2k5N7w-acNS1f_p5S8D0GUfHh1jOjwhSOb3JzxeUKVT0OpKcEqdOunK4VJAbUTxibAL2I00-Z6Ys7-BY6loHS6Bif9mlRP4I8kC0E1ELY3qmlhhrlH_7Miymqlkd9P_ocRlFK57veq_Frxq31ktvAms67gG-a_ahsOIMMcet6Pvho4n5zChqoOiEOAGaesqY0amqy2ijnqr459xBW2vQ


#Manager token -- eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjJiWkJaVk5sOGEtdE5vTDNMVzVoWSJ9.eyJpc3MiOiJodHRwczovL2Rldi0tcnVoc3lsai51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjJkM2RmOGQ2OWU5NWY2NGJlOGE5NTAwIiwiYXVkIjoiQ29mZmVlLXNob3AiLCJpYXQiOjE2NTgzNTk5NDgsImV4cCI6MTY1ODM2NzE0OCwiYXpwIjoiaVNEQU9icnloYkRRZ1FGdnFCOEVEUjZ5NHd2eXg4ckQiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.FkBy_6Xtyj4mfy_jjFnfxL5xukAZ9R4dGGwPhywONutDoCJnw5n_sJD4GMUptSiDHgErFd1b51dqlXzAHQnmTi8vPbkinfdGm54ZKZJ8C2--qaDH7Yv4mdY3ZjgweUwVB0xFvnaspsWaCgEjCudhXraW51pauf9u-DyD4P18K_gwIhn3XjZTWxm79LmoVf6TzKA4JyDMlqShrAd86ucO4gY9jCIOsn5mH-7ZiYujn4QwOK4prOgrK89bH9TTJ_9Ad43VGKSNpz8HWQLd3QkRipVsU0ZW3GUz4ox6vsml9Wncho6ov56AdBrQHnBKcBrmbJXzR11sSjEjRwFNA5cCBQ