#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
from sqlalchemy import exc
from werkzeug import exceptions

 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route("/campers", methods=["GET", "POST"])
def campers():

    if request.method == "GET":
        campers = Camper.query.all()

        campers_serialized = [camper.to_dict(only=("id","name", "age")) for camper in campers]
        response = make_response(
            jsonify(campers_serialized),
            200
        )
        return response
    elif request.method == "POST":
        data = request.get_json()
        try:
            camper = Camper(**data)
            db.session.add(camper)
            db.session.commit()
            code = 201
            response = make_response(
                jsonify(camper.to_dict()),
                code
            )
            return response
        
        except ValueError:

            response = make_response(
                jsonify({"errors": ["validation errors"]}),
                400
            )
            return response


@app.route("/campers/<int:id>", methods=["GET", "PATCH"])
def campers_by_id(id):
    if request.method == "GET":
        camper = Camper.query.filter(Camper.id == id).first()

        if not camper:
            camper_serialized = {"error": "Camper not found"}
            code = 404
        else:
            camper_serialized = camper.to_dict()
            code = 200

        response = make_response(
            jsonify(camper_serialized),
            code
        )

        return response
    
    elif request.method == "PATCH":
        camper = Camper.query.filter(Camper.id == id).first()

        if not camper:
            return {"error": "Camper not found"}, 404
 
        else:
            data = request.get_json()
        
            try:
                print("test before setting attr")
                [setattr(camper, attr, data[attr]) for attr in data]
                print("test before adding and commiting")
                db.session.add(camper)
                db.session.commit()
                print("success")
                camper_serialized = camper.to_dict()
                code = 202

            except ValueError:
                camper_serialized = {"errors": ["validation errors"]}
                code = 400

            finally:
                response = make_response(
                    jsonify(camper_serialized),
                    code
                )

                return response


@app.route("/activities", methods=["GET"])
def activities():
    if request.method == "GET":
        activities = Activity.query.all()

        activities_serialized = [activity.to_dict(only=["id", "name", "difficulty"]) for activity in activities]

        response = make_response(
            jsonify(activities_serialized),
            200
        )
        return response
    
@app.route("/activities/<int:id>", methods=["DELETE"])
def activities_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if not activity:
        return {"error": "Activity not found"}, 404
    
    else:
        db.session.delete(activity)
        response = make_response(
            jsonify({}),
            204
        )
        return response

@app.route("/signups", methods=["POST"])
def signups():
    data = request.get_json()

    try:
        new_signup = Signup(**data)
        db.session.add(new_signup)
        db.session.commit()

        signup_serialzied = new_signup.to_dict()
        code = 201

    except:
        signup_serialzied = {"errors": ["validation errors"]}
        code = 400
    
    finally:
        response = make_response(
            jsonify(signup_serialzied),
            code
        )

        return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
