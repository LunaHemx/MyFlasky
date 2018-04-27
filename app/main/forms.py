from flask.ext.wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from ..models import User

class PostForm(FlaskForm):
    body=TextAreaField("What's on your mind?",validators=[DataRequired()])
    submit=SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name=StringField('Real name',validators=[Length(0,64)])
    about_me=TextAreaField('About me')
    submit=SubmitField('Submit')


class CommentForm(FlaskForm):
    body=StringField('',validators=[DataRequired()])
    submit=SubmitField('Submit')


