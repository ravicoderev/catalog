from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, Category, Item, User
# from flask import session as login_session
import random
import string
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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


# Add new item for a Category
# @app.route('/items/new/', methods=['GET', 'POST'])
# def addItem():
#     if request.method == 'POST':
#         newItem = Item(item_name=request.form['name'])
#         newItem = Item(item_description=request.form['description'])
#         newItem = Item(category_id=request.form['category_id'])
#         newItem = Item(user_id=request.form['user_id'])
#         session.add(newItem)
#         flash('SUCCESS: New Item %s Successfully Created' % newItem.item_name)
#         session.commit()
#         return redirect(url_for('showAllItems'))
#     else:
#         return render_template('newitem.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)