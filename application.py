import random
import string
import requests
import httplib2
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
from flask import session as login_session
from functools import wraps

# Instance, every time it runs create instance name
app = Flask(__name__)

# Client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "EDotTech Shop"


# Session section
engine = create_engine('sqlite:///edottechshop.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    '''
    Login Section by third party google
    Create anti-forgery state token
    Login using google
    return: login.html file
    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
    using post method to login using google
    gconnect(): to connect and validate the token
    '''
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user
        is already connected.'''),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    # create User Id
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
    output += ''' " style = "width: 300px; height: 300px;border-radius:
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    '''
    gdisconnect(): check if the user is connected - log out
    DISCONNECT - Revoke a current user's token and reset their login_session
    '''
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('''Current
        user not connected.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You have successfully logged out')
        return redirect('/')
    else:
        response = make_response(json.dumps('''Failed to
        revoke token for given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    '''
    User Helper Function
    Create a user in a databas, name, email, picture
    return: user's id
    '''
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    '''
    User Helper Function
    get user object info by passing id
    return: user object
    '''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    '''
    User Helper Function
    get user id by email
    return: user id or none if the user doesn't exist
    '''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


def login_required(f):
    '''
    A decorator is a function that wraps and replaces another function.
    To Make sure user is logged in.
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function
# end login and adding user section


@app.route('/catalog/JSON')
# Show all categories and its items in JSON format
def catalogJSON():
    '''
    JSON Application: View items in json format
    This part consists of 4 sections to show all
    categories, all items, details of a
    specific item and show all what we have in database
    '''
    categories = session.query(Category).all()
    categoryInJSON = [category.serialize for category in categories]
    for category in range(len(categoryInJSON)):
        items = [i.serialize for i in session.query(Items).
                 filter_by(category_id=categoryInJSON[category]["id"]).all()]
        if items:
            categoryInJSON[category]["i"] = items
    return jsonify(Category=categoryInJSON)


@app.route('/categories/JSON')
# Show all categories in JSON format
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/categories/<int:category_id>/items/JSON')
# Show all items for a specific category in JSON format
def categoryItemsJSON(category_id):
    items = session.query(Items).filter_by(category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/categories/<int:category_id>/items/<int:item_id>/JSON')
# Show item's details in JSON format
def itemDetailsJSON(category_id, item_id):
    item = session.query(Items).filter_by(id=item_id,
                                          category_id=category_id).one()
    return jsonify(item=item.serialize)


# end JSON section


@app.route('/')
@app.route('/categories')
def allCategoryAndItems():
    '''
    Show all categories and its items in main page which has log out button
    return:
    -If the user logged in show main page
    -If not show the public main page which has login button
    '''
    if 'username' not in login_session:
        categories = session.query(Category).all()
        # Show Latest 5 Items
        latestItems = session.query(Items).order_by(Items.id.desc()).limit(5)
        items = latestItems[::1]
        return render_template('public_main.html',
                               categories=categories, items=items)
    else:
        categories = session.query(Category).all()
        # Show Latest 5 Items
        latestItems = session.query(Items).order_by(Items.id.desc()).limit(5)
        items = latestItems[::1]
        return render_template('main.html', categories=categories, items=items)


@app.route('/<int:category_id>/items')
@login_required
def showItems(category_id):
    '''
    Show all item for a specific category
    return:
    -If the user logged in show all the items under selected category
    -If not redirect the user to login page
    '''
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    return render_template('allItems.html', items=items, category=category)


@app.route('/<int:category_id>/items/<int:item_id>/')
@login_required
def showDetails(category_id, item_id):
    '''
    Show all item'a details
    return:
    -If the user logged in show all the item's details
    -If not redirect the user to login page
   '''
    item = session.query(Items).filter_by(id=item_id).one()
    return render_template('itemDetails.html', item=item)


@app.route('/<int:category_id>/items/new/', methods=['GET', 'POST'])
@login_required
def addItem(category_id):
    '''
    Add a new item
    return:
    -If the user logged in, it allows
    the user to add a new item to a specific category
    -If not redirect the user to login page
    '''
    if request.method == 'POST':
        newItem = Items(name=request.form['name'],
                        description=request.form['description'],
                        price=request.form['price'],
                        category_id=category_id,
                        user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('A new item has been added')
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('addItem.html', category_id=category_id)


@app.route('/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    '''
    Edit Item Details
    return:
    -If the user logged in, it allows the user to edit
    the fields if he/she is the owner that item or cancel
    -otherwise, it gives an alert message the
    the user cann't update the item
    '''
    editItem = session.query(Items).filter_by(id=item_id,
                                              category_id=category_id,).one()
    if editItem.user_id != login_session['user_id']:
            flash('You are not the author of this item, you can not update it')
            return redirect(url_for('showDetails', category_id=category_id,
                                    item_id=item_id))
    if request.method == 'POST':
        if (request.form['name'] and request.form['description'] and
           request.form['description']):
            editItem.name = request.form['name']
            editItem.description = request.form['description']
            editItem.price = request.form['price']
        elif (request.form['name'] == '' or request.form['description'] == ''
              or request.form['description'] == ''):
            flash('you should fill in all the fields')
            return render_template('editItem.html', category_id=category_id,
                                   item_id=item_id, item=editItem)
        session.add(editItem)
        session.commit()
        flash('Item details have been successfully updated')
        return redirect(url_for('showDetails', category_id=category_id,
                                item_id=item_id))
    else:
        return render_template('editItem.html', category_id=category_id,
                               item_id=item_id, item=editItem)


@app.route('''/<int:category_id>/items/<int:item_id>/delete/''',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    '''
    Delete Item
    return:
    -If the user logged in, it allows the user to delete
    an item if he/she is the owner of that item or cancel
    -otherwise, it gives an alert message that
    the user cann't delete the item
    '''
    itemToDelete = session.query(Items).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        flash('You are not the author of this item, you can not delete it')
        return redirect(url_for('showDetails',
                                category_id=category_id, item_id=item_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Main part runs if there is no exceptions, from python interpretur
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
