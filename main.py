from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from forms import RegisterForm, LoginForm, ContactForm, AddPlaceForm, AddReviewForm
from flask import Flask, abort, render_template, redirect, url_for, flash, jsonify
from flask_login import UserMixin,login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
import smtplib

# https://flask.palletsprojects.com/en/2.3.x/quickstart/
app = Flask(__name__)
# https://flask-wtf.readthedocs.io/en/1.2.x/form/#secure-form
app.config['SECRET_KEY'] = 'secret_key'
# https://bootstrap-flask.readthedocs.io/en/stable/basic/#initialization
ckeditor = CKEditor()
Bootstrap5(app)

my_email = "test.email.mcfp@gmail.com"
my_password = "okauhakjzhykwubp"

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# For adding profile images to the comments
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Connect to DB
# https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/#configure-the-extension
db = SQLAlchemy()
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

# CONFIGURE TABLES
# Relationships: Place - User -> One to Many; Place - Review -> One to Many; User - Review -> One to Many

# Create a Place table
class Place(db.Model):
    __tablename__ = "places"
    id: Mapped[int] = mapped_column(primary_key=True)

    place_name: Mapped[str] = mapped_column(String(250), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    type: Mapped[str] = mapped_column(String(250), nullable=False)


    # user = relationship("User", back_populates="place")
    review = relationship("Review", back_populates="place")


# Create a User table for all registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    # place_id: Mapped[int] = mapped_column(ForeignKey("places.id"))

    email: Mapped[str] = mapped_column(String(100), unique=False)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

    # place = relationship("Place", back_populates="user")
    review = relationship("Review", back_populates="user")


# Create Review table
class Review(db.Model):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)

    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    coffee_rating: Mapped[int] = mapped_column(Integer)
    download_mbps: Mapped[int] = mapped_column(Integer)
    upload_mbps: Mapped[int] = mapped_column(Integer)
    recommendation: Mapped[str] = mapped_column(String(250))
    comment_text: Mapped[str] = mapped_column(Text())

    place = relationship("Place", back_populates="review")
    user = relationship("User", back_populates="review")

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user email is already present in the database
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, please log in.")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-login
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template('register.html', form=form, current_user=current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password, incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html', form=form, current_user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_password)
            connection.sendmail(
                from_addr=my_email, to_addrs="test_email_mcfp@yahoo.com",
                msg=f"Subject:Working Nomad: {form.subject}\n\n{form.message}"
            )
    return render_template('contact.html', form=form)

@app.route("/add_place", methods=['GET', 'POST'])
def add_place():
    form = AddPlaceForm()
    if form.validate_on_submit():
        # Check if the place is already present in the database
        result_place = db.session.execute(db.select(Place).where((Place.place_name == form.place_name.data) &
                                                                 (Place.address == form.address.data)))
        place = result_place.scalar()
        # If the place is not yet present in the database, add the place
        if not place:
            new_place = Place(
                place_name=form.place_name.data,
                address=form.address.data,
                type=form.type.data
            )
            db.session.add(new_place)
            db.session.commit()
            # Get the id of the new_place added
            result_place = db.session.execute(db.select(Place).where((Place.place_name == form.place_name.data) &
                                                                     (Place.address == form.address.data)))
            place = result_place.scalar()

        # Get the id of the place, whether it's newly added or not
        return redirect(url_for("add_review", place_id=place.id))
    return render_template('add.html', form=form)

@app.route("/add_review/<int:place_id>", methods=['GET', 'POST'])
def add_review(place_id):
    place = db.get_or_404(Place, place_id)
    form = AddReviewForm()
    if form.validate_on_submit():
        new_review = Review(
            coffee_rating=form.coffee_rating.data,
            download_mbps=form.download_mbps.data,
            upload_mbps=form.upload_mbps.data,
            recommendation=form.recommendation.data,
            comment_text=form.comment_text.data,
            user=current_user,
            place=place

        )
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for("get_all_places"))
    return render_template('add.html', form=form)


@app.route("/places")
def get_all_places():
    result = db.session.execute(db.select(Place.id.label("place_id"),
                                          Review.id.label("review_id"),
                                          Place.place_name,
                                          Place.address,
                                          Place.type,
                                          func.avg(Review.coffee_rating).label("average_coffee_rating"),
                                          func.avg(Review.download_mbps).label("average_download_mbps"),
                                          func.avg(Review.upload_mbps).label("average_upload_mbps"),
                                          func.group_concat(Review.recommendation).label("recommendations"),
                                          func.group_concat(Review.comment_text).label("comments")
                                          )
                                .select_from(Place)
                                .join(Review, Place.id == Review.place_id)
                                .group_by(Place.id)
                                )
    places = result.all()

    result_review = db.session.execute(db.select(Place.id.label("place_id"),
                                          Review.id.label("review_id"),
                                          Review.recommendation,
                                          Review.comment_text
                                          )
                                .select_from(Place)
                                .join(Review, Place.id == Review.place_id)
                                .order_by(Place.id)
                                )
    reviews = result_review.all()

    # result = db.session.execute(db.select(Place))
    # places = result.scalars().all()
    # for place in places:
    #     print(place)
    #     print(place.place_id)
    #     print(place.review_id)

    # for place in places:
    #     for review in reviews:
    #         if review.place_id == place.place_id:
    #             print(place.recommendation)
    for review in reviews:
        print(review)
        print(review.place_id)
        print(review.review_id)

    formatted_reviews = []
    for review in reviews:
        formatted_reviews.append({
            "place_id": review.place_id,
            "review_id": review.review_id,
            "recommendation": review.recommendation,
            "comment_text": review.comment_text
        })

    return render_template('places.html', all_places=places)
    # return render_template('places.html', all_places=places, all_reviews=json.dumps(formatted_reviews))


if __name__ == "__main__":
    app.run(debug=True, port=5001)

