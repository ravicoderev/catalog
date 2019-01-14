#! Python 3.7


#  Flask modules from flask library
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session

# SQL Alchemy modules
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, Category, Item, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

# Authentication modules for google OAuth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import random, string, json, requests
import httplib2



app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sporting Goods Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# **** OAuth ****
# START OAuth
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    # return "The current session state is %s" % login_session['state']

# --------------- gconnect()

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid. Converted to python 3 using requests instead of httplib2
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    token_url = requests.get(url=url)
    result = json.loads(token_url.text)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_g_id = login_session.get('g_id')
    if stored_access_token is not None and g_id == stored_g_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['g_id'] = g_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = b''
    output += b'<h1>Welcome, '
    output += bytes(login_session['username'], encoding="utf-8")
    output += b'!</h1>'
    output += b'<img src="'
    output += bytes(login_session['picture'], encoding="utf-8")
    output += b' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# ----------------- gconnect() end


#  END OAuth ****


# **** START CATEGORY ****


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.category_name))
    return render_template('categories.html', categories=categories)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(category_name=request.form['name'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.category_name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    # categories = session.query(Category).order_by(asc(Category.category_name))
    print(category_id)
    editQuery = session.query(Category).filter_by(category_id=category_id).one()
    
    if request.method == 'POST':
        if request.form['name']:
            editQuery.category_name = request.form['name']
            flash('Edit Successful: %s' % editQuery.category_name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category=editQuery)
    # return "Feature WIP"


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    deleteQuery = session.query(
        Category).filter_by(category_id=category_id).one()
    if request.method == 'POST':
        session.delete(deleteQuery)
        flash('Delete Successful: %s' % deleteQuery.category_name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deletecategory.html', category=deleteQuery)

# **** END CATEGORY ****

# **** START ITEMS ****

# Show all items
@app.route('/items/')
def showAllItems():
    items = session.query(Item).order_by(asc(Item.item_name))
    return render_template('items.html', items=items)

# Show all items in Category
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showCategoryItems(category_id):
    category = session.query(Category).filter_by(category_id=category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()

    return render_template('items1.html', items=items, category=category)


# Add new item for a Category
@app.route('/category/<int:category_id>/new', methods=['GET', 'POST'])
def addNewItemForCategory(category_id):
    category = session.query(Category).filter_by(category_id=category_id).one()
    if request.method == 'POST':
        newItem = Item(item_name=request.form['name'], item_description=request.form['description'], 
        category_id=category_id, user_id=request.form['user_id'])
        session.add(newItem)
        flash('SUCCESS: New Item %s Successfully Created' % newItem.item_name)
        session.commit()
        return redirect(url_for('showAllItems'))
    else:
        return render_template('newitem.html', category=category)


# Edit item in a Category
# @app.route('/items/edit')
@app.route('/category/<int:category_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItemInCategory(category_id, item_id):
    editItem = session.query(Item).filter_by(item_id=item_id).one()
    category = session.query(Category).filter_by(category_id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editItem.item_name = request.form['name']
            flash('Edit Successful: %s' % editItem.item_name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('edititem.html', item=editItem, category=category)
    # return("Edit item in a Category: WIP")


# Delete item in a Category

@app.route('/category/<int:category_id>/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItemInCategory(category_id, item_id):
    deleteItem = session.query(Item).filter_by(item_id=item_id).one()
    category = session.query(Category).filter_by(category_id=category_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash('Delete Successful: %s' % deleteItem.item_name)
        return redirect(url_for('showCategoryItems', category_id=category.category_id))
    else:
        return render_template('deleteitem.html', item=deleteItem, category=category)
    # return("Delete item in a Category: WIP")


# **** END ITEMS ****



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)