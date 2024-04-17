from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,  \
    SearchField, SelectField, IntegerField, FloatField, MultipleFileField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])

    submit = SubmitField('Sign Me Up!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Let Me In!')

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class AddPlaceForm(FlaskForm):
    place_name = SearchField('Name of place:', validators=[DataRequired()])
    address = StringField('Address:', validators=[DataRequired()])
    type = SelectField('Type of place:',
                       choices=['Cafe', 'Co-Working space', 'Bakery', 'Restaurant', 'Hotel', 'Library', 'Art gallery',
                                'Bar', 'Other'],
                       validators=[DataRequired()])
    submit = SubmitField('Next')

class AddReviewForm(FlaskForm):
    coffee_rating = IntegerField('Coffee rating:', validators=[DataRequired()])
    download_mbps = FloatField('Download MBPS:', validators=[DataRequired()])
    upload_mbps = FloatField('Upload MBPS:', validators=[DataRequired()])
    recommendation = SelectField('Recommendations:',
                                 choices=['Good Coffee', 'Quiet Workplace', 'Comfy Seats', 'Enough Power Sockets',
                                          'Spacious Place', 'Shareable Long Table for Groups', 'Spacious Tables',
                                          'Tasty Food', 'With Healthy Food Options', 'Controllable Room Temperature',
                                          'Aesthetically Pleasing'],
                                 validators=[DataRequired()])
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    # image = MultipleFileField('Upload images:')
    submit = SubmitField('Submit')


