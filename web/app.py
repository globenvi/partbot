from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, Product
import os

WEBHOOK_LISTEN = "0.0.0.0"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = "kljdklsahiopduy1y298e319hdskajh"
app.config['UPLOAD_FOLDER'] = 'static/product_images'  # Define upload folder for product images

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# Create all tables on startup if they do not exist
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index_page():
    if request.method == "POST":
        product_name = request.form.get('product_name')
        product_description = request.form.get('product_description')
        product_price = request.form.get('product_price')
        product_category = request.form.get('product_category')
        product_tags = request.form.get('product_tags')
        product_images = request.files.getlist('product_photos')  # List of uploaded images

        # Save product to the database
        image_filenames = []
        for image in product_images:
            if image:
                image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(image_filename)
                image_filenames.append(image.filename)  # Add the image filename to the list

        new_product = Product(
            name=product_name,
            description=product_description,
            price=float(product_price),
            category=product_category,
            tags=product_tags,  # Tags can be stored as a comma-separated string
            images=",".join(image_filenames)  # List of image filenames
        )

        # Add product to the session and commit to the database
        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!", category="success")
        return redirect(url_for('index_page'))

    products = Product.query.all()
    return render_template('index.html', user=current_user, products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("Все поля обязательны для заполнения!", "danger")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Пользователь с таким именем уже зарегистрирован!", "danger")
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Пользователь с таким email уже зарегистрирован!", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Вы успешно зарегистрировались!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Успешная авторизация!", "success")
            return redirect(url_for('profile'))  # После входа перенаправляем на профиль
        else:
            flash("Неверный логин или пароль!", "danger")

    return render_template('login.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host=WEBHOOK_LISTEN, debug=False)
