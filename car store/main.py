from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import login_user, LoginManager, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config["SECRET_KEY"] = "3uK2tezJ4PJmYbERbKzn4jim44kZyDyAKi"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'photos')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


class SellCar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<SellCar %r>' % self.id


with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        firstName = request.form['firstName']
        phone = request.form['phone']
        email = request.form['email']
        description = request.form.get('description', '')
        price = request.form['price']

        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)

        photo = request.files['photo']

        if 'photo' not in request.files or not request.files['photo'].filename:
            flash('No file part or no selected file')
            return redirect(request.url)

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(file_path)

            # Store the relative path in the database
            photo.save(file_path)
            sell_car = SellCar(
                firstName=firstName,
                phone=phone,
                photo=filename,  # Store the filename instead of the full path
                email=email,
                description=description,
                price=price
            )

            try:
                db.session.add(sell_car)
                db.session.commit()
                return redirect('/posts')
            except Exception as e:
                flash(f"An error occurred while adding: {str(e)}")
                db.session.rollback()
                return render_template('posts.html')
        else:
            flash('File type not allowed')
            return redirect('/posts')
    else:
        return render_template('create.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/posts')
def posts():
    posts = SellCar.query.order_by(SellCar.date.desc()).all()
    return render_template('posts.html', posts=posts)


@app.route('/posts/<id>')
def posts_detail(id):
    user_post = SellCar.query.filter_by(
        id=id).first()
    print(user_post)
    # post = SellCar.query.get(username)

    return render_template('posts_detail.html', post=user_post)


@app.route('/posts/<int:id>/delete')
def posts_delete(id):

    post = SellCar.query.get_or_404(id)

    try:
        db.session.delete(post)
        db.session.commit()
        return redirect('/posts')
    except:
        return "An error occurred when deleting a post"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    user_post = SellCar.query.get(id)
    if request.method == "POST":
        user_post.firstName = request.form['firstName']
        user_post.phone = request.form['phone']
        user_post.email = request.form['email']
        user_post.description = request.form['description']
        user_post.price = request.form['price']

        # Handle file upload
        new_photo = request.files['photo']
        if new_photo.filename != '':
            # Save the uploaded file with a secure filename
            filename = secure_filename(new_photo.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            new_photo.save(file_path)
            user_post.photo = file_path

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "An error occurred while updating a post"
    else:
        return render_template('sell_car_update.html', user_post=user_post)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)