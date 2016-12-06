from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from functools import wraps
import random
import string

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database and create database session
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.context_processor
def logged_in():
    return dict(logged_in='username' not in login_session)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# User Helper Functions

def createUser(login_session):
    print '->createUser'
    for i in login_session.keys():
        print i, login_session[i]
    new_user = User(name=login_session['username'], email=login_session['email'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in login_session:
            return f(*args, **kwargs)
        else:
            return redirect('/login')
    return decorated_function


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope=['profile', 'email'])
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # if stored_access_token is not None and gplus_id == stored_gplus_id:
    #     response = make_response(json.dumps('Current user is already connected.'),
    #                              200)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'access token:', login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')
    # print 'result is ', result[0], result[1]

    if result[0]['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(CategoryItem).limit(len(categories))
    if 'user_id' in login_session:
        return render_template('categories.html', categories=categories, items=items)
    else:
        return render_template('categories_public.html', categories=categories, items=items)


# JSON API to view all categories)
@app.route('/json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    # Show all categories and the items for the selected category
    categories = session.query(Category).order_by(asc(Category.name))
    selected_category = session.query(Category).filter_by(id=category_id).one()
    return render_template('categories2.html', categories=categories, selected_category=selected_category)


# JSON API to view a category item
@app.route('/category/json/<int:category_id>/')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category.serialize)


# Show a category item
@app.route('/item/<int:item_id>/')
def showItem(item_id):
    # Show an individual item
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    if 'user_id' in login_session and login_session['user_id'] == item.user_id:
        return render_template('item.html', item=item)
    else:
        return render_template('item_public.html', item=item)


# JSON API to view an individual item
@app.route('/item/json/<int:item_id>/')
def itemJSON(item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(item.serialize)


@app.route('/item/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        category = session.query(Category).filter_by(id=request.form['category_id']).one()
        new_item = CategoryItem(title=request.form['item_title'], description=request.form['item_description'], category=category, user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newitem.html', categories=categories)


# Edit a category item
@app.route('/item/edit/<int:item_id>/', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    edited_item = session.query(CategoryItem).filter_by(id=item_id).one()
    if login_session['user_id'] != edited_item.user_id:
        return redirect(url_for('showItem', item_id=item_id))

    if request.method == 'POST':
        if request.form['item_title']:
            edited_item.title = request.form['item_title']
        if request.form['item_description']:
            edited_item.description = request.form['item_description']
        if request.form['category_id']:
            category = session.query(Category).filter_by(id=request.form['category_id']).one()
            edited_item.category = category
        session.add(edited_item)
        session.commit()
        return redirect(url_for('showItem', item_id=item_id))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('edititem.html', categories=categories, item=edited_item, user_id=login_session['user_id'])


# Delete a menu item
@app.route('/item/delete/<int:item_id>/', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    item_to_delete = session.query(CategoryItem).filter_by(id=item_id).one()
    if login_session['user_id'] != item_to_delete.user_id:
        return redirect(url_for('showItem', item_id=item_id))

    if request.method == 'POST':
        print 'deleteItem POST'
        for i in request.form.keys():
            print request.form[i]

        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('showCategory', category_id=item_to_delete.category_id))
    else:
        return render_template('deleteitem.html', item=item_to_delete,
                               user_id=login_session['user_id'])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
