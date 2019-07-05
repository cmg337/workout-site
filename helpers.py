import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_images(link):
    linkList =[]
    link = link[0:-5]
    for i in range(1,4):
        newLink = link + str(i) + ".jpg"
        req = requests.get(newLink)
        if req.status_code == 200:
            linkList.append(newLink)
        else:
            break;
    return linkList;
    

