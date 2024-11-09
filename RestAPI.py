import sys
from flask import Flask, jsonify, abort, request, make_response
from flask_restful import reqparse, Resource, Api
import os
import json
from db_util import db_access

app = Flask(__name__)

####################################################################################
#
# Error handlers
#
@app.errorhandler(400)  # decorators to add to 400 response
def bad_request(error):
    return make_response(jsonify({'status': 'Bad request'}), 400)

@app.errorhandler(401)  # decorators to add to 401 response
def unauthorized_request(error):
    return make_response(jsonify({'status': 'Unauthorized request'}), 401)

@app.errorhandler(404)  # decorators to add to 404 response
def resource_not_found(error):
    return make_response(jsonify({'status': 'Resource not found'}), 404)

######################################
# User 
######################################
class User(Resource):
    def get(self, api_key):
        if api_key in API_KEYS:
            if not request.json or 'username' not in request.json:
                abort(400)  # bad request

            username = request.json['username']
            password = request.json['password']

            # Determine if the input is a phone number or username
            if username.isdigit():
                sqlProc = 'getUserByPhoneNumber'
                sqlArgs = [username]
            else:
                sqlProc = 'getUserByUsername'
                sqlArgs = [username]

            try:
                user = db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))  # server error

            if not user:
                return make_response(jsonify({'status': 'User not found'}), 404)

            # Validate the password
            if user[0]['user_password'] != password:
                return make_response(jsonify({'status': 'Invalid password'}), 403)

            return make_response(jsonify({'user_id': user[0]['user_id']}), 200)
        
        else:
            abort(401)
        
    def post(self, api_key):
        if api_key in API_KEYS:
            if not request.json or 'username' not in request.json:
                abort(400)  # bad request

            username = request.json['username']
            user_surname = request.json['user_surname']
            user_firstname = request.json['user_firstname']
            user_phone_number = request.json['user_phone_number']
            user_email = request.json['user_email']
            user_date_of_birth = request.json['user_date_of_birth']
            password = request.json['password']

            # Check if the username or phone number already exists
            try:
                existing_user = db_access('getUserByUsername', [username])
                if existing_user:
                    return make_response(jsonify({'status': 'Username already exists'}), 409)  # Conflict
            except Exception as e:
                abort(500, description=str(e))  # server error

            try:
                existing_user = db_access('getUserByPhoneNumber', [user_phone_number])
                if existing_user:
                    return make_response(jsonify({'status': 'Phone number already exists'}), 409)  # Conflict
            except Exception as e:
                abort(500, description=str(e))  # server error

            # Insert the new user into the database
            try:
                db_access('addUser', [user_surname, user_firstname, user_phone_number, user_email, password, user_date_of_birth])
                return make_response(jsonify({'status': 'User created successfully'}), 201)  # Created
            except Exception as e:
                abort(500, description=str(e))  # server error

        else:
            abort(401)

################################################
# Letter
################################################
class Letter(Resource):
    def get(self, user_id, api_key):
        if api_key in API_KEYS:
            sqlProc = 'getUserLetters'
            sqlArgs = [user_id]
            try:
                rows = db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))
            return make_response(jsonify({'Letters': rows}), 200)
        else:
            abort(401)

    def post(self, user_id, api_key):
        if api_key in API_KEYS:
            if not request.json:
                abort(400)  # bad request

            recipient_username = request.json['recipient']
            letter_message = request.json['letter_message']
            design_id = 1

            if recipient_username.isdigit():
                sqlProc = 'getUserByPhoneNumber'
                sqlArgs = [recipient_username]
            else:
                sqlProc = 'getUserByUsername'
                sqlArgs = [recipient_username]

            try:
                recipient = db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))  # server error

            if not recipient:
                return make_response(jsonify({'status': 'Recipient not found'}), 404)
            
            recipient_id = recipient[0]['user_id']

            sqlProc = 'createLetter'
            sqlArgs = [user_id, recipient_id, letter_message, design_id]
        
            try:
                db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))

            return make_response(jsonify({'status': 'success'}), 200)
        else:
            abort(401)

    def put(self, user_id, letter_id, option, api_key):
        if api_key in API_KEYS:
            if option == 'delete':
                sqlProc = 'deleteLetter'
                sqlArgs = [letter_id]
            elif option == 'read':
                sqlProc = 'readLetter'
                sqlArgs = [letter_id]
            elif option == 'P.S':
                letter_PS = request.json['letter_PS']
                sqlProc = 'addPS'
                sqlArgs = [letter_id, letter_PS]
            else:
                abort(500, description='Invalid option')
            
            try:
                db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))
            return make_response(jsonify({'status': 'success'}), 200)
        else:
            abort(401)

#############################################
# Draft 
#############################################
class Draft(Resource):
    def get(self, user_id, api_key):
        if api_key in API_KEYS:
            sqlProc = 'getUserDrafts'
            sqlArgs = [user_id]
            try: 
                rows = db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))
            return make_response(jsonify({'Drafts': rows}), 200)
        else:
            abort(401)
    
    def post(self, user_id, api_key):
        if api_key in API_KEYS:
            if not request.json:
                abort(400)  # bad request

            recipient_username = request.json['recipient']
            message = request.json['draft_message']

            sqlProc = 'createDraft'
            sqlArgs = [user_id, recipient_username, message, 0]

            try:
                db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))

            return make_response(jsonify({'status': 'success'}), 200)
        else:
            abort(401)

    def put(self, user_id, draft_id, api_key):
        if api_key in API_KEYS:
            if not request.json:
                abort(400)  # bad request

            recipient_username = request.json['recipient']
            message = request.json['draft_message']

            sqlProc = 'editDraft'
            sqlArgs = [draft_id, recipient_username, message, 0]

            try:
                db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))

            return make_response(jsonify({'status': 'success'}), 200)
        else:
            abort(401)

    def delete(self, user_id, draft_id, api_key):
        if api_key in API_KEYS:
            sqlProc = 'deleteDraft'
            sqlArgs = [draft_id]
            try:
                db_access(sqlProc, sqlArgs)
            except Exception as e:
                abort(500, description=str(e))
            return make_response(jsonify({'status': 'success'}), 200)
        else:
            abort(401)

api = Api(app)
api.add_resource(User, '/api/<string:api_key>/user')
api.add_resource(Letter, '/api/<string:api_key>/user/<int:user_id>/letter',
                 '/api/<string:api_key>/user/<int:user_id>/letter/<int:letter_id>',
                 '/api/<string:api_key>/user/<int:user_id>/letter/<int:letter_id>/<string:option>')
api.add_resource(Draft, '/api/<string:api_key>/user/<int:user_id>/draft', '/api/<string:api_key>/user/<int:user_id>/draft/<int:draft_id>')

if __name__ == "__main__":
    app.run(
        host=APP_HOST,
        port=APP_PORT,
    )