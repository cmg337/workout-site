from cs50 import SQL

# https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
from functools import reduce
import requests

db = SQL("sqlite:///workout.db")
# check if missed 51-56

# 73 pages of exercises on BB.com
FIRST_PAGE = 69
LAST_PAGE = 73


# returns all links to exercises on a page
def parsePage(page):

    # all exercise links have the same class
    names = page.find_all(class_ = 'ExHeading ExResult-resultsHeading')
    links = []


    # append each href to link list
    for name in names:
        links.append(name.find('a').get('href'))
    return links


# adds exercise info to db from an exercise page
def addExercise(link):
    # load page
    url = 'https://www.bodybuilding.com' + link
    response = requests.get(url)
    page = BeautifulSoup(response.text, 'html.parser')

    # get each peice of in based on specific html attributes
    infoList = page.find('ul', class_ = 'bb-list--plain')

    name = page.find(class_ = "ExHeading ExHeading--h2 ExDetail-h2").contents[0].replace('\n','').strip()
    type_ = infoList.find('a', href=re.compile('/exercises/exercise-type.*')).contents[0].replace('\n','').strip()
    muscle = infoList.find('a', href=re.compile('/exercises/muscle.*')).contents[0].replace('\n','').strip()
    level = infoList.contents[-2].contents[0].replace('\n','').replace('Level:','').strip()

    try:
        equipment = infoList.find('a', href=re.compile('/exercises/equipment.*')).contents[0].replace('\n','').strip()
    except:
        equipment = 'none'


    img = page.find(class_ = 'ExImg ExDetail-img js-ex-enlarge')['src']

    # instr = reduce(lambda x, y : x if y == ' ' else x + '\n' + y.contents[0], page.find(class_ = "ExDetail-descriptionSteps").contents, '')
    # instr = page.find(itemprop="description")



    # insert each value into the database
    db.execute('INSERT INTO BB_Workouts(name, link, type, muscle, equipment, level, img) VALUES (:name, :link, :type_, :muscle, :equipement, :level, :img)', \
        name=name,link=link,type_=type_,muscle=muscle,equipement=equipment,level=level,img=img)




def main():

    linkList = []

    for number in range(FIRST_PAGE,LAST_PAGE + 1):
        url = 'https://www.bodybuilding.com/exercises/finder/' + str(number)
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        linkList += parsePage(page)

    for link in linkList:
        print('starting    bodybuilding.com' + link)
        addExercise(link)
        print('added    ' + link)




def addIMGLinks():
    for exercise in db.execute("SELECT * FROM BB_Workouts"):
        link = exercise['img'][0:-5]
        numLinks = 0
        for i in range(1,5):
            newLink = link + str(i) + ".jpg"
            req = requests.get(newLink)
            if req.status_code == 200:
                numLinks += 1;
            else:
                break;
        db.execute("UPDATE BB_Workouts SET img = :link, numImgs = :numLinks WHERE id = :id1", link=link, numLinks=numLinks, id1=exercise['id'])
        





addIMGLinks()