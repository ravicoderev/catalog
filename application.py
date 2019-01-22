#! Python 3.6


#  Flask modules from flask library
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from flask import session as login_session

# SQL Alchemy modules
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, Category, Item, User

# Authentication modules for google OAuth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import random
import string
import json
import requests


''' 
Enable Foreign Key Support Using Passive Deletes
https://docs.sqlalchemy.org/en/latest/orm/collections.html#using-passive-deletes
Implementing ON DELETE CASCADE
https://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#sqlite-foreign-keys
'''
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sporting Goods Catalog App"


engine = create_engine('sqlite:///sportscatalogitems.db', connect_args={'check_same_thread': False})
DBSession = sessionmaker(bind=engine)
session = DBSession()


# **** OAuth **** Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    # return "The current session state is %s" % login_session['state']


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
        response = make_response(json.dumps('Current user is already connected.'), 200)
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

    # Check for existing/new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        print("Create New User ID")
        new_user_id = createUser(login_session)
        print(new_user_id)
        login_session['user_id'] = new_user_id
        print("New User ID :", login_session['user_id'])
    else:
        login_session['user_id'] = user_id
        print("Existing User ID :", login_session['user_id'])

    output = b''
    output += b'<h1>Welcome, '
    output += bytes(login_session['username'], encoding="utf-8")
    output += b'!</h1>'
    output += b'<img src="'
    output += bytes(login_session['picture'], encoding="utf-8")
    output += b' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              b'-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    print(login_session)
    return output

# END gconnect() 



# User details
def createUser(login_session):
    newUser = User(user_name=login_session['username'], user_email=login_session['email'],
                   user_picture=login_session['picture'])
    session.add(newUser)
    try:
        session.commit()
        print("Create User: Session Commit")
        user = session.query(User).filter_by(user_email=login_session['email']).one()
        return user.user_id
    except:
        print("Create User:Exception occurred in createUser() method")
        session.rollback()
        return None
    finally:
        session.close()
        print("Create User: Session Closed")


def getUserInfo(user_id):
    user = session.query(User).filter_by(user_id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(user_email=email).one()
        return user.user_id
    except:
        return None
# User Details END


# START gdisconnect() - DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    try:
        access_token = login_session.get('access_token')
    except KeyError:
        flash('Failed to get access token')
        return redirect(url_for('showCategories'))
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Check that the access token is valid. Converted to python 3 using requests instead of httplib2
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    token_url = requests.get(url=url)
    result = json.loads(token_url.text)
   
    if result is None:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        del login_session['access_token']
        del login_session['g_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print('gdisconnect - ok')
        flash('Google Sign Out - Successfull!!')
 
        return response

    
# END OAuth **** gdisconnect()


# Check login status
def loginStatus():
    print(login_session.get('access_token'), login_session.get('email'))
    if 'access_token' in login_session:
        login_status = True
    else:
        login_status = False
    return login_status


# Home Page without Login - Show all Categories and Recent 10 Items Added
@app.route('/')
@app.route('/home/', methods=['GET', 'POST'])
def home():
    categories = (session.query(Category).order_by(Category.category_name).all())
    recentItemsAdded = (session.query(Item).order_by(Item.item_id.desc()).limit(10))
    login_status = loginStatus()
    if login_status is True:
        return render_template('categories.html', categories=categories, recentItemsAdded=recentItemsAdded)
    else:
        return render_template('home.html', categories=categories, recentItemsAdded=recentItemsAdded)
    
    if request.method == 'POST':
        return redirect(url_for('login'))
    

# **** START CATEGORY ****


# Show all categories
@app.route('/category/')
def showCategories():
    login_status = loginStatus()
    if login_status is True:
        categories = (session.query(Category).order_by(Category.category_name).all())
        recentItemsAdded = (session.query(Item).order_by(Item.item_id.desc()).limit(10))
        return render_template('categories_only.html', categories=categories, recentItemsAdded=recentItemsAdded)
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))



# Check if the category alredy exists
def checkCategoryNameExists(category_name_exists):
    name_exists = None
    print(category_name_exists)
    try:
        categoryquery = (session.query(Category).filter_by(category_name=category_name_exists).one())
        name_exists=True
    except:
        name_exists=False
    
    return name_exists
            

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    login_status = loginStatus()
    if login_status is True:
        if request.method == 'POST':
            newCategory = Category(category_name=request.form['name'], user_id=login_session['user_id'])
            print(newCategory)
            if checkCategoryNameExists(newCategory.category_name) is True:
                flash('DUPPLICATE CATEGORY!!: " %s " ...category name already exists' % newCategory.category_name)
                return redirect(url_for('showCategories'))
            else:
                print("Inside ELSE")
                session.add(newCategory)
                try:
                    session.commit()
                    flash('CREATE SUCCESS!!: " %s " ...new category added' % newCategory.category_name)
                    return redirect(url_for('showCategories'))
                except:
                    print("Create New Category: Exception during commit")
                finally:
                    session.close()
        else:
            return render_template('newCategory.html')
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))


# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    login_status = loginStatus()
    if login_status is True:
        editQuery = session.query(Category).filter_by(category_id=category_id).one()
        if editQuery.user_id != login_session['user_id']:
            flash('EDIT NOT ALLOWED!!: " %s " ...creator alone has permission to edit' % editQuery.category_name)
            return redirect(url_for('showCategories'))

        if request.method == 'POST':
            
            if request.form['name']:
                editQuery.category_name = request.form['name']
                session.add(editQuery)
                try:
                    session.commit()
                    flash('EDIT SUCCESS!!: " %s " ...category modified' % editQuery.category_name)
                    return redirect(url_for('showCategories'))
                except:
                    flash('EDIT EXCEPTION OCCURRED!! Unable to edit. Something went wrong when saving the changes...')
                    return redirect(url_for('showCategories'))
                    
                finally:
                    session.close() 
        else:
            return render_template('editcategory.html', category=editQuery)
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))
    

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    login_status = loginStatus()
    if login_status is True:
        deleteQuery = session.query(Category).filter_by(category_id=category_id).one()
        items = session.query(Item).filter_by(category_id=category_id).all()
        if deleteQuery.user_id != login_session['user_id']:
                flash('DELETE NOT ALLOWED!!: " %s " ...creator alone has permission to delete' % deleteQuery.category_name)
                return redirect(url_for('showCategories'))

        if request.method == 'POST':
            session.delete(deleteQuery)
            try:
                session.commit()
                flash('DELETE SUCCESS!!: " %s " ...category deleted' % deleteQuery.category_name)
                return redirect(url_for('showCategories'))
            except:
                flash('DELETE EXCEPTION OCCURRED!!: Delete Failed. Something went wrong when deleting category')
                return redirect(url_for('showCategories'))
                
            finally:
                session.close() 
        else:
            return render_template('deletecategory.html', category=deleteQuery, items=items)
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))

# **** END CATEGORY ****


# **** START ITEMS ****
# Show all items
@app.route('/items/')
def showAllItems():
    
        items = session.query(Item).order_by(asc(Item.item_name))
        return render_template('items.html', items=items)


# Show all items in Category
@app.route('/category/<int:category_id>/items/')
def showCategoryItems(category_id):
    category = session.query(Category).filter_by(category_id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('categoryitems.html', items=items, category=category)


# Add new item for a Category
@app.route('/category/<int:category_id>/new', methods=['GET', 'POST'])
def addNewItemForCategory(category_id):
    login_status = loginStatus()
    if login_status is True:
        category = session.query(Category).filter_by(category_id=category_id).one()
        
        if request.method == 'POST':
            newItem = Item(item_name=request.form['name'], item_description=request.form['description'],
            category_id=category_id, user_id=login_session['user_id'])
            session.add(newItem)
            try:
                session.commit()
                flash('CREATE SUCCESS!!: " %s " ...new item added to category' % newItem.item_name)
                return redirect(url_for('showCategoryItems', category_id=category.category_id))
            except:
                flash('CREATE EXCEPTION OCCURRED!!: Failed to add new item. Something went wrong when adding new item.')
                return redirect(url_for('showCategoryItems', category_id=category.category_id))
            finally:
                session.close()
        else:
            return render_template('newitem.html', category=category)
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))


# Edit item in a Category
# @app.route('/items/edit')
@app.route('/category/<int:category_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItemInCategory(category_id, item_id):
    login_status = loginStatus()
    if login_status is True:
        editItem = session.query(Item).filter_by(item_id=item_id).one()
        category = session.query(Category).filter_by(category_id=category_id).one()
        
        if editItem.user_id != login_session['user_id']:
            flash('EDIT NOT ALLOWED!!: " %s " ...creator alone has permission to edit' % editItem.item_name)
            return redirect(url_for('showCategoryItems', category_id=category.category_id))

        if request.method == 'POST':
            if request.form['name']:
                editItem.item_name = request.form['name']
                editItem.item_description = request.form['description']
                session.add(editItem)
                try:
                    session.commit()
                    flash('EDIT SUCCESS!!: " %s " ...item name modified' % editItem.item_name)
                    return redirect(url_for('showCategoryItems', category_id=category.category_id))
                except:
                    flash('EDIT EXCEPTION OCCURRED!!: Edit Failed. Something went wrong when saving changes')
                    return redirect(url_for('showCategoryItems', category_id=category.category_id))
                finally:
                    session.close()
        else:
            return render_template('edititem.html', item=editItem, category=category)
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))
   

# Delete item in a Category
@app.route('/category/<int:category_id>/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItemInCategory(category_id, item_id):
    login_status = loginStatus()
    if login_status is True:
        deleteItem = session.query(Item).filter_by(item_id=item_id).one()
        category = session.query(Category).filter_by(category_id=category_id).one()
        
        if deleteItem.user_id != login_session['user_id']:
            flash('DELETE NOT ALLOWED!!: " %s " ...creator alone has permission to edit' % deleteItem.item_name)
            return redirect(url_for('showCategoryItems', category_id=category.category_id))

        if request.method == 'POST':
            
            session.delete(deleteItem)
            try:
                session.commit()
                flash('DELETE SUCCESS!!: " %s " ...item name deleted' % deleteItem.item_name)
                return redirect(url_for('showCategoryItems', category_id=category.category_id))
            except:
                flash('DELETE EXCEPTION OCCURRED!!: Delete Failed. Something went wrong when deleting item')
                return redirect(url_for('showCategoryItems', category_id=category.category_id))
            finally:
                session.close()
        else:
            return render_template('deleteitem.html', item=deleteItem, category=category)
    else:
        flash('LOGIN!!: Feature requires login. Please log in. You are redirected to the home page...')
        return redirect(url_for('home'))


# **** END ITEMS ****


# JSON API End Points 

# Show all categories
@app.route('/categories/JSON')
def showCategoriesJSON():
    categories = (session.query(Category).order_by(Category.category_name).all())
    return jsonify(Categories=[c.serialize for c in categories])

# Show details of a specific category
@app.route('/categorydetails/<int:category_id>/JSON')
def categoryDetailsJSON(category_id):
    category = session.query(Category).filter_by(category_id=category_id).one()
    return jsonify(CategoryDetails=category.serialize)


@app.route('/recentitems/JSON')
def showrecentItems():
    recentItemsAdded = (session.query(Item).order_by(Item.item_id.desc()).limit(10))
    return jsonify(RecentItems=[c.serialize for c in recentItemsAdded])

# Show all items in Category
@app.route('/category/<int:category_id>/items/JSON')
def showItemsInCategory(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])

# END API End Points


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
    