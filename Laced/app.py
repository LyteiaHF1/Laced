from flask import Flask, redirect, url_for, render_template, session,flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
from werkzeug import secure_filename
from config import config, interface
import mysql.connector
import os
import model
from sqlalchemy import *
db = create_engine('sqlite:///laced.db')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laced.db'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '903491159707098',
        'secret': 'd5cabb938679cc675b6363c5d0dbff8e'
    },
    'twitter': {
        'id': 'S7mOaScN2xYfhsulJ3bD45xj4',
        'secret': 'M7nm9itITXPfOIadGcHgYZviTuCElqeTIH3vCmIKKFyP6Ej8ui'
    }
}

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Insert filename into database 
def add_pic(filename, label, size, con, descript):
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    cur.execute("insert into trade (imgUrl,tradeName,size,con,descript) values (%s,%s,%s,%s,%s)", (filename,label,size,con,descript)) #values is how many columns in database
    db.commit()


db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    profilepic = db.Column(db.BLOB, nullable=True)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    if current_user.is_authenticated():
        return render_template('closet.html')
    else:
        return render_template('index.html')

    
@app.route('/home')
def home():
    #query to db is done in model so all thats needed is call the function to grab it and render it on page
    shoes = model.Shoe.get_all_home()
    trades = model.Trade.get_all_hometrades()
    return render_template("home.html",shoe_list=shoes, trade_list=trades)
    

@app.route('/store')
def shop():
    shoes = model.Shoe.get_all()
    return render_template("shop.html",shoe_list=shoes)


    
@app.route("/store/<int:id>")
def shopdetail(id):
    shoe = model.Shoe.get_by_id(id) 
    return render_template('detail.html', display_shoe=shoe)
 
    

@app.route("/cart")
def shopping_cart():
    """Display content of shopping cart."""

    # TODO: Display the contents of the shopping cart.
    #   - The cart is a list in session containing shoes added

    cart_dict = {}
    if not session:                                 # if nothing has been added to cart yet
        shoe_info = []
        return render_template('cart.html', shoe_info=shoe_info)

    for id in session['cart']:
        cart_dict[id] = cart_dict.setdefault(id, 0) + 1

    shoe_info = []
    for id in cart_dict.keys():
        shoe = model.Shoe.get_by_id(id)
        name = shoe.common_name
        price = shoe.price
        img = shoe.imgurl
        num = cart_dict[id]
        shoe_info.append((name, num, price,img))

    return render_template("cart.html", shoe_info=shoe_info)


@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    """Add a Shoe to cart and redirect to shopping cart page.

    When a shoe is added to the cart, redirect browser to the shopping cart
    page and display a confirmation message: 'Successfully added to cart'.
    """
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(id)
    return redirect('/cart')
    

#DO NOT USE NOT WORKING PROPERLY ONCE CART IS CLEAR THE SEEION DOSENT RESTART SO NOTHING CAN BE ADDED TO CART    
@app.route('/clearcart')
def clear_cart():
    session['cart'] = []
    return redirect("/cart") 

@app.route("/checkout")
def checkout():
    """Temporary Checkout redirect til fix paypal header issue."""

    flash("Sorry! Cant Checkout at This Tim.")
    return redirect("/store")


@app.route('/trade')
def trade():
    filename = request.args.get('filename', '')
    t = (filename,)
    trades = model.Trade.get_all_trades()
    return render_template("trade.html",trade_list=trades, filename = filename)
    

@app.route('/trade/<id>')
def tradedetail(id):
      #need to associate each shop item by id, detail page gets id from clicked on link in shop then takes to item page where user can add to cart and view more images if avalibile
    trade = model.Trade.get_by_id(id) 
    return render_template('tradedetail.html', display_trade=trade)

@app.route('/closet')
def closet():
    return render_template('closet.html')

@app.route('/tradeupload')
def tradeupload():
        return render_template('tradeuplaodform.html')

    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        label = request.form['label']
        size = request.form['size']
        con = request.form['con']
        descript = request.form['descript']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        add_pic(filename, label, size, con, descript)
        return redirect(url_for('trade', filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    #print "test"
    #return Test
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email,profile_image_url_https = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email,profilepic=profile_image_url_https)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
