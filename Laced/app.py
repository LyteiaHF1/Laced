from flask import Flask, redirect, url_for, render_template, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
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
     #dispaly  trades added to trade floor and shop items
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    #selects product, price and image form database
    cur.execute('select productId,productName, price, Img, size, descript,con from store WHERE con = "8/10"')
    data = cur.fetchall()
    #grabs trades from database
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur1 = db.cursor()
    cur1.execute('select id, tradeName, descript, imgUrl,con from trade WHERE con = "10"')
    tradedata = cur1.fetchall()
    return render_template('home.html', pagedata = data, trade = tradedata)
    
@app.route('/store')
def shop():
#display fruits
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    #selects product, price and image form database
    cur.execute('select productId, productName, price, Img, descript from store')
    data = cur.fetchall()
    return render_template('shop.html', pagedata = data)


@app.route('/shop/<id>')
def shopdetail(id):
    #need to associate each shop item by id, detail page gets id from clicked on link in shop then takes to item page where user can add to cart and view more images if avalibile
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    #selects product, price and image form database
     cur.execute('select productId,productName, price, Img,size,descript from store WHERE productId =' + id )
    data = cur.fetchall()
    return render_template('detail.html', pagedata = data)

@app.route('/shop/<id>/cart')
def cart(id): 
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    #selects product, price and image form database
    cur.execute('select productId,productName, price, Img from store WHERE productId =' + id )
    data = cur.fetchall()
    #have to make the session variable so when user leaves off cart page the item stays but checkout works[just one item] 

#def update(id):
    #if id == id:
        #print 'item is here now'
    
    return render_template('cart.html', pagedata = data)

@app.route('/trade')
def trade():
    #display trades
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    #selects product, price and image form database
    cur.execute('select id, tradeName, size, con from trade')
    data = cur.fetchall()
    return render_template('trade.html', pagedata = data)

@app.route('/trade/<id>')
def tradedetail(id):
      #need to associate each shop item by id, detail page gets id from clicked on link in shop then takes to item page where user can add to cart and view more images if avalibile
    db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', port='8889', database='Laced')
    cur = db.cursor()
    #selects product, price and image form database
    cur.execute('select id, tradeName, size, imgUrl,descript from trade WHERE id =' + id )
    data = cur.fetchall()
    return render_template('tradedetail.html', pagedata = data)

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
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
