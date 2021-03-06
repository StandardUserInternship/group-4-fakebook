from enum import unique
from flask import Flask, render_template, url_for, flash, redirect
from flask_login import login_required, LoginManager, UserMixin, current_user, login_user
from flask_sqlalchemy import SQLAlchemy 
from forms import RegistrationForm, LoginForm, PostForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import login
from app.models import User
from bcrypt import bcrypt

# Test Comment
app = Flask(__name__)
#app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245' #TODO: Remove hardcoded secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
''' this code needs a home for the login to work again
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
'''

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
#   admin = db.Column(db.String(129), unique=True, nulabble=False) doesn't work.
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) #these have to be lowercase.

    def set_password(self, pw): #register
        self.password = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password, pw)
            
    def __repr__(self):
        return f"USER('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)#i don't know if i want to use this time zone
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



    def __repr__(self):
        return f"POST('{self.title}', '{self.date_posted}')" #one-to-many

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route("/admin", methods=['GET', 'POST'])

@login_required
def admin():
    form = LoginForm()
    if form.validate_on_submit():#retieve "filter_all" user
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('Welcom, adminstrator', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

if __name__ == '__main__':
    app.run(debug=True)

#@app.route("/post/new", methods=['GET', 'POST'])
#@login_required
#def new_post():
#    form = PostForm()
#    if form.validate_on_submit():
#        flash('Post successfully uploaded.', 'success')
#        return redirect(url_for('home'))
#    return render_template('create_post.html', title='New Post', form=form)
