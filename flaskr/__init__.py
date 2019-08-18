from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
import random
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
import urllib.request
from bs4 import BeautifulSoup
import requests
from jinja2 import Markup, escape
import os
from flaskr import auth
from flaskr.auth import login_required
    

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure templates are auto-reloaded
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Configure session to use filesystem (instead of signed cookies)
    app.config["SESSION_FILE_DIR"] = mkdtemp()
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"


    # Ensure responses aren't cached
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    

    # Configure CS50 Library to use SQLite database
    db = SQL("sqlite:///flaskr/workout.db")
    
    
    # list of groups and types for exercises
    TYPES = list(map(lambda item: item['type'], db.execute(
        "SELECT DISTINCT type FROM BB_Workouts")))
    MUSCLES = list(map(lambda item: item['muscle'], db.execute(
        "SELECT DISTINCT muscle FROM BB_Workouts")))
    EQUIPMENTS = list(map(lambda item: item['equipment'], db.execute(
        "SELECT DISTINCT equipment FROM BB_Workouts")))
    LEVELS = list(map(lambda item: item['level'], db.execute(
        "SELECT DISTINCT level FROM BB_Workouts")))

    categories = {
        "type": TYPES,
        "muscle": MUSCLES,
        "equipment": EQUIPMENTS,
        "level": LEVELS
        }

    # handles authentication requests in auth.py
    app.register_blueprint(auth.bp)

    @app.route("/")
    def index():
        """Return random workout form"""
        return render_template("index.html", TYPES=TYPES, MUSCLES=MUSCLES, EQUIPMENTS=EQUIPMENTS, LEVELS=LEVELS)


    @app.route("/workout", methods=["POST"])
    def workout():
        """Generate Random Workout given user parameters"""




        # filter by each selection category on index page
        sqlQuery = "SELECT * FROM BB_Workouts WHERE (1" # set up query - uses 1 to allow first AND statement
        for key, list in categories.items():
            checker = 0 #add checker for each category to know when to add AND
            for item in list:
                if request.form.get(item):
                    # add AND to query for first type checked
                    if checker == 0:
                        checker = 1
                        sqlQuery += f') AND ({key} = "' + item + '"'
                    else:
                        sqlQuery += f' OR {key} = "' + item + '"'

        # add paranthesis for and statement
        sqlQuery += ")"
        # generate random workout from executed SQL query
        workoutPool = db.execute(sqlQuery)
        result = []
        for i in range(int(request.form.get("number"))):
            if len(workoutPool) > 0:
                randomInt = random.randrange(0, len(workoutPool))
                result.append(workoutPool[randomInt])
                del workoutPool[randomInt]
            else:
                break

        # see if user logged in to add option to save workout
        loggedIn = 0 if len(session) == 0 else 1

    

        return render_template("workout.html", workouts=result, loggedIn=loggedIn)

    @app.route("/exercise", methods=["GET"])
    def exercise():
        """Return Exercise description popup """

        # get id from search query
        id1 = request.args.get('id')
        exerciseInfo = db.execute("SELECT * FROM BB_Workouts WHERE id=:id1", id1=id1)

        # load page
        url = 'https://www.bodybuilding.com' + exerciseInfo[0]['link']
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')

        # get each peice of in based on specific html attributes
        infoList = page.find('section', class_ = 'ExDetail-guide').contents
        return render_template('exercise.html', html = infoList)



    


    @app.route("/saveWorkout", methods=["POST"])
    @login_required
    def saveWorkout():
        """ Save a workout to saved workouts table """

        # save user id as string to use in query later
        user_id = str(session["user_id"])

        # pick unused workoutID, each user gets 10
        workoutID = session["user_id"] * 10
        idList = []
        for x in range(10):
            idList.append(workoutID + x)

        userSaved = db.execute(
            "SELECT * FROM saved WHERE userID = :user_id", user_id=user_id)
        for exercise in userSaved:
            if exercise["workoutID"] in idList:
                idList.remove(exercise["workoutID"])

        # if user has 10 workouts return error
        if idList == []:
            return 'false'
        workoutID = idList[0]

        # loop through exercises in workout to save based on length
        for exerciseNum in range(int(request.form.get('length'))):
            # get exercise id from form
            exerciseID=request.form.get(str(exerciseNum))
            # insert info into saved table
            db.execute("INSERT INTO saved (workoutID, workoutName, userID, date, setCount, repCount, weight, exerciseID) VALUES (:workoutID, :workoutName, :userID, :date, 0, 0 ,0, :exerciseID)",
                       workoutName= request.form.get('name'), userID=user_id, date=date.today(), workoutID=workoutID, exerciseID=exerciseID)
        return 'true'


    @app.route("/saved", methods=["GET", "POST"])
    @login_required
    def saved():
        """ return saved workouts page and handle request from that page to edit or delete """
        # render template if get request
        if request.method == "GET":
            # get workouts where user id equals session id
            user_id = str(session["user_id"])
            exerciseDict = {}

            # http://www.martinbroadhurst.com/removing-duplicates-from-a-list-while-preserving-order-in-python.html
            saved = db.execute(
                "SELECT * FROM saved where userID = :userID ORDER BY date DESC", userID=user_id)
            seen = set()
            ids = [x['workoutID'] for x in saved if not (
                x['workoutID'] in seen or seen.add(x['workoutID']))]

            # add each exercise to dictionary
            for ex in saved:
                exerciseDict[ex["exerciseID"]] = db.execute("SELECT * FROM BB_Workouts WHERE id = :exID", exID=ex["exerciseID"])[0]
        

            return render_template("saved.html", saved=saved, ids=ids, exerciseDict = exerciseDict)

        # handle post method
        else:
            # delete workout from table
            if request.form.get("edit_type") == 'delete':
                db.execute("DELETE FROM saved WHERE workoutID=:workoutID",
                           workoutID=request.form.get("id"))
                return redirect('/saved')

            # delete all workouts for user
            elif request.form.get("edit_type") == 'deleteAll':
                user_id = str(session["user_id"])
                db.execute("DELETE FROM saved WHERE userID = :userID",
                           userID=user_id)
                return redirect("/saved")

            # pull up edit form for workout ie. create form with preinserted old values
            elif request.form.get("edit_type") == 'edit':
                workout = db.execute(
                    "SELECT * FROM saved WHERE workoutID = :workoutID", workoutID=request.form.get("id"))
                exerciseList = [];
                for exercise in workout:
                    newEx = db.execute("SELECT * FROM BB_Workouts WHERE id = :exID", exID = exercise["exerciseID"])
                    exerciseList.append(newEx[0])
                return render_template("create.html", error=0, edit=1, workout=workout, exerciseList=exerciseList)

            # open error form otherwise
            else:
                return render_template("error.html")


    @app.route("/create", methods=["GET", "POST"])
    @login_required
    def create():
        """ create new workouts or edits existing workout """
        # load page at get request
        if request.method == "GET":
            return render_template("create.html", error=0, edit=0)

        # add workout at post
        else:

            # save user id as string to use in query later
            user_id = str(session["user_id"])

            # create new workout
            if request.form.get("edit") == '0':

                # pick unused workoutID, each user gets 10
                workoutID = session["user_id"] * 10
                idList = []
                for x in range(10):
                    idList.append(workoutID + x)
                userSaved = db.execute(
                    "SELECT workoutID FROM saved WHERE userID = :user_id", user_id=user_id)
                for exercise in userSaved:
                    if exercise['workoutID'] in idList:
                        idList.remove(exercise["workoutID"])

                # if user has 10 workouts return error
                if idList == []:
                    return render_template("create.html", error=1, edit=0)
                workoutID = idList[0]

            # if edited workout, get previous id
            else:
                workoutID = int(request.form.get("id"))
                # check for malicious attempt to overwrite other user's data
                if user_id != db.execute("SELECT userID FROM saved WHERE workoutID = :workoutID", workoutID = workoutID)[0]['userID']:
                    render_template("error.html")
                # delete previous workout if exists
                db.execute(
                    "DELETE FROM saved WHERE workoutID = :workoutID", workoutID=workoutID)

            # add each exercise to saved table with same workoutid
             # use try incase user inputs excerise name not in database
            try:
                for exNumber in range(int(request.form.get("numberExercises"))):

                    exerciseInfo = db.execute("SELECT id FROM BB_Workouts WHERE name = :name", name=request.form.get("name" + str(exNumber)))[0]
                    exerciseID = exerciseInfo["id"]
                    workoutName=request.form.get("workoutName")
                    setCount=request.form.get("sets" + str(exNumber))
                    repCount=request.form.get("reps" + str(exNumber))
                    weight=request.form.get("weight" + str(exNumber))

                    db.execute("INSERT INTO saved (workoutID, workoutName, userID, setCount, repCount, weight, date, exerciseID) VALUES (:workoutID\
                            , :workoutName, :userID, :setCount, :repCount, :weight, :date, :exerciseID)", workoutID=workoutID, workoutName=workoutName, userID=user_id, setCount=setCount, repCount=repCount, weight=weight, date=date.today(), exerciseID = exerciseID)

                return redirect("/saved")
            except:
                return render_template("error.html")

    @app.route("/search", methods=["GET"])
    @login_required
    def search():
        q = request.args.get("query")
        if not q:
            q = ""
        searchResults = db.execute('SELECT * FROM BB_Workouts WHERE (name LIKE :q OR muscle LIKE :q OR equipment LIKE :q OR type LIKE :q)', q= "%" + q + '%' )
        return jsonify(searchResults)

    if __name__ == "__main__":
        app.run()

    return app