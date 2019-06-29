from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import random
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from datetime import datetime, date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///workout.db")

# list of groups and types for exercises
muscle_groups = ["chest", "biceps", "triceps", "back", "legs", "shoulders", "traps", "abs"]
workout_types = ["body", "weight", "machine"]


@app.route("/")
def index():
    """Return random workout form"""
    return render_template("index.html", muscle_groups = muscle_groups, workout_types = workout_types)


@app.route("/workout", methods=["POST"])
def workout():
    """Generate Random Workout given user parameters"""

    # see if user logged in to use their table
    if len(session) != 0:
        table = user_id = str(session["user_id"])
    # use default table otherwise
    else:
        table = 'workouts'

    # set up SQL query
    sql_search = "SELECT * FROM :table WHERE ("
    # filter by muscle group
    for group in muscle_groups:
        if request.form.get(group):
            if sql_search != "SELECT * FROM :table WHERE (":
                sql_search += "OR "
            sql_search += "\"groups\" LIKE '%" + group + "%' "

    # add check variable to see if type queried yet
    type_check = 0
    # filter by workout type
    for wtype in workout_types:
        if request.form.get(wtype):
            # add AND to query for first type checked
            if type_check == 0:
                type_check = 1
                sql_search += ") AND (\"type\" LIKE '%" + wtype +"%'"
            else:
                sql_search += " OR \"type\" LIKE '%" + wtype +"%'"
    # add paranthesis for and statement
    sql_search += ")"

    workout_pool = db.execute(sql_search, table=table)

    result = []
    for i in range(int(request.form.get("number"))):
        if len(workout_pool) > 0:
            random_int = random.randrange(0, len(workout_pool))
            result.append(workout_pool[random_int])
            del workout_pool[random_int]
        else:
            break

    # see if user logged in to add option to save workout
    loggedIn = 0
    if len(session) != 0:
        loggedIn = 1

    print(result)

    return render_template("workout.html", workouts = result, loggedIn = loggedIn)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""

    #forget user info
    session.clear()

    # return register page if get
    if request.method == "GET":
        return render_template("register.html", error = 0)

    # register user if meets requirements
    elif request.method == "POST":
        email = request.form.get("email")
        firstname = request.form.get("first-name")
        lastname = request.form.get("last-name")
        password = request.form.get("password")

        # check if username exists
        if len(db.execute("SELECT * FROM users WHERE email = :email", email=email)) != 0:
            return render_template("register.html", error = 1)

        # add user to database
        db.execute("INSERT INTO users (email, firstname, lastname, password) VALUES (:email, :firstname, :lastname, :password)",
                    email = email, password = generate_password_hash(password), firstname = firstname, lastname = lastname )

        #start session after registering
        session["user_id"] = db.execute("SELECT id FROM users WHERE email = :email", email = email)[0]["id"]
        user_id = str(session["user_id"])

        # create user table to store exercises
        db.execute("CREATE TABLE :user_id (id INTEGER PRIMARY KEY, name, groups, type)", user_id = user_id)
        db.execute("INSERT INTO :user_id (id, name, groups, type) SELECT * FROM workouts", user_id = user_id)


        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log User In"""

    #forget user info
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("login.html", error = 1)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", error = 0)



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/add", methods=["GET","POST"])
@login_required
def add():
    """Add workouts to user's database"""

    # return blank form if get method
    if request.method == "GET":
        return render_template("add.html", workout_types = workout_types, muscle_groups = muscle_groups, added = 0)

    # add workout to user's database, and return add page again
    else:
        # create user database if does not exist
        user_id = str(session["user_id"])
        name = request.form.get("name")
        group = request.form.get("group")
        _type = request.form.get("type")

        # insert exercise into users table if table exists
        # try:
        db.execute("INSERT INTO :user_id (name, groups, type) VALUES (:name, :group, :_type)",  user_id = user_id, name = name, group = group, _type = _type)

        # return add page again
        return render_template("add.html", workout_types = workout_types, muscle_groups = muscle_groups, added = 1)


@app.route("/edit", methods = ["GET", "POST"])
@login_required
def edit():
    """Return edit form"""

    # return form if request is get type
    if request.method == "GET":
        user_id = str(session["user_id"])
        workout_table = db.execute("SELECT id, name, groups, type FROM :user_id", user_id = user_id)
        return render_template("edit.html", workout_table = workout_table)

    # handle post methods
    else:
        # delete exercise from table
        if request.form.get("edit_type") == 'delete':
            user_id = str(session["user_id"])
            db.execute("DELETE FROM :table WHERE id=:exercise_id", table = user_id, exercise_id = request.form.get("id"))
            workout_table = db.execute("SELECT id, name, groups, type FROM :user_id", user_id = user_id)
            return render_template("edit.html", workout_table = workout_table)

        # delete All exercises
        elif request.form.get("edit_type") == 'deleteAll':
            user_id = str(session["user_id"])
            db.execute("DELETE FROM :table", table=user_id)
            workout_table = db.execute("SELECT id, name, groups, type FROM :user_id", user_id = user_id)
            return render_template("edit.html", workout_table = workout_table)

        # open edit page for exercise
        else:
            user_id = str(session["user_id"])
            exercise_info = db.execute("SELECT * FROM :table WHERE id=:exercise_id", table = user_id, exercise_id = request.form.get("id"))[0]
            return render_template("editItem.html", exercise_info = exercise_info, workout_types = workout_types, muscle_groups = muscle_groups)


@app.route("/editItem", methods = ["POST"])
@login_required
def editItem():
    """ Return Individual Edit Form for Exercise """
    # get edited info
    _type = request.form.get("type")
    group = request.form.get("group")
    name = request.form.get("newName")
    _id = request.form.get("id")
    user_id = str(session["user_id"])

    # edit db with new info
    db.execute("UPDATE :table SET type = :_type, groups = :group, name = :name WHERE id = :_id", table=user_id, _type=_type, group=group, name=name, _id=_id)

    # return to edit page
    workout_table = db.execute("SELECT id, name, groups, type FROM :user_id", user_id = user_id)
    return render_template("edit.html", workout_table = workout_table)


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

    userSaved = db.execute("SELECT * FROM saved WHERE userID = :user_id", user_id = user_id)
    for exercise in userSaved:
        if exercise["workoutID"] in idList:
            idList.remove(exercise["workoutID"])

    # if user has 10 workouts return error
    if idList == []:
        return 'false'
    workoutID = idList[0]

    # loop through exercises in workout to save based on length
    for exercise_num in range(int(request.form.get('length'))):
        # get exercise info from user table based on exercise id
        exercise_info = db.execute("SELECT name, groups, type FROM :table WHERE id = :exercise_id", table = user_id, exercise_id = request.form.get(str(exercise_num)))[0]
        # insert info into saved table
        db.execute("INSERT INTO saved (workoutName, userID, exerciseName, groups, type, date, workoutID, setCount, repCount, weight) VALUES (:workoutName, :userID, :exerciseName, :group, :_type, :date, :workoutID, 0, 0 ,0)",\
            workoutName = 'Saved Workout ' + str(datetime.now())[0:-10], userID = user_id, exerciseName = exercise_info['name'], group = exercise_info['groups'], _type = exercise_info['type'],\
            date=date.today(), workoutID = workoutID)
    return 'true'


@app.route("/saved", methods = ["GET", "POST"])
@login_required
def saved():
    """ return saved workouts page and handle request from that page to edit or delete """
    # render template if get request
    if request.method == "GET":
        # get workouts where user id equals session id
        user_id = str(session["user_id"])

        # http://www.martinbroadhurst.com/removing-duplicates-from-a-list-while-preserving-order-in-python.html
        saved = db.execute("SELECT * FROM saved where userID = :userID ORDER BY date DESC", userID = user_id)
        seen = set()
        ids =  [x['workoutID'] for x in saved if not (x['workoutID'] in seen or seen.add(x['workoutID']))]
        # ids = set([exercise["workoutID"] for exercise in saved])
        # render template
        return render_template("saved.html", saved = saved, ids = ids)

    # handle post method
    else:
        # delete workout from table
        if request.form.get("edit_type") == 'delete':
            db.execute("DELETE FROM saved WHERE workoutID=:workoutID",  workoutID = request.form.get("id"))
            return redirect('/saved')

        # delete all workouts for user
        elif request.form.get("edit_type") == 'deleteAll':
            user_id = str(session["user_id"])
            db.execute("DELETE FROM saved WHERE userID = :userID", userID = user_id)
            return redirect("/saved")

        # pull up edit form for workout AKA create form with preinserted old values
        elif request.form.get("edit_type") == 'edit':
            workout = db.execute("SELECT * FROM saved WHERE workoutID = :workoutID", workoutID = request.form.get("id"))
            user_id = str(session["user_id"])
            exerciseTable = db.execute("SELECT * FROM :table", table = user_id)
            return render_template("create.html", error = 0, edit = 1, workout = workout, exerciseTable = exerciseTable)

        # open edit page for workout
        else:
            workout_info = db.execute("SELECT * FROM saved WHERE workoutID = :workoutID", workoutID = request.form.get("id"))[0]
            return render_template("editWorkout.html", workout_info = workout_info)


@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    """ create new workouts or edits existing workout """
    # load page at get request
    if request.method == "GET":
        user_id = str(session["user_id"])
        exerciseTable = db.execute('SELECT * FROM :table', table = user_id)

        return render_template("create.html", error = 0, exerciseTable = exerciseTable, edit = 0)

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
            userSaved = db.execute("SELECT workoutID FROM saved WHERE userID = :user_id", user_id = user_id)
            for exercise in userSaved:
                if exercise['workoutID'] in idList:
                    idList.remove(exercise["workoutID"])

            # if user has 10 workouts return error
            if idList == []:
                return render_template("create.html", error = 1, edit = 0)
            workoutID = idList[0]

        # handle editing workouts
        else:
            workoutID = int(request.form.get("id"))
            keptExercises = {}
            for exNumber in range(int(request.form.get("numberExercises"))):
                if request.form.get("createWorkoutSelect" + str(exNumber)) == 'same':
                    keptExercises[exNumber] = [request.form.get("nameActual" + str(exNumber)), request.form.get("groups" + str(exNumber)), request.form.get("type" + str(exNumber))]

            db.execute("DELETE FROM saved WHERE workoutID = :workoutID", workoutID = workoutID)

        # add each exercise to saved table with same workoutid

        for exNumber in range(int(request.form.get("numberExercises"))):

            if request.form.get("edit") == '1' and (exNumber in keptExercises):
                groups = keptExercises[exNumber][1]
                types = keptExercises[exNumber][2]
                exerciseName = keptExercises[exNumber][0]
            else:
                exerciseInfo = db.execute("SELECT * FROM :table WHERE id = :exID", table = user_id, exID = request.form.get("createWorkoutSelect" + str(exNumber)))[0]
                groups = exerciseInfo['groups']
                types = exerciseInfo["type"]
                exerciseName = exerciseInfo["name"]

            db.execute("INSERT INTO saved (workoutID, workoutName, exerciseName, groups, type, userID, setCount, repCount, weight, date) VALUES (:workoutID\
                , :workoutName, :exerciseName, :groups, :types, :userID, :setCount, :repCount, :weight, :date)", workoutID = workoutID, workoutName = request.form.get("workoutName")\
                , userID = user_id, setCount = request.form.get("sets" + str(exNumber)), repCount = request.form.get("reps" + str(exNumber)), weight = request.form.get("weight" + str(exNumber))\
                , date = date.today(), groups = groups, types = types, exerciseName = exerciseName)

        return redirect("/saved")



@app.route("/editWorkout", methods = [ "POST"])
@login_required
def editWorkout():
    """ Return Individual Edit Form for Workout """


