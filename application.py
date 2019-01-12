from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, Category
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
# def editCategory(category_id):
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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)