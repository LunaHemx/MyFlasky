from flask import render_template,redirect,request,url_for,flash,abort
from flask.ext.login import login_user,logout_user,login_required,current_user
from . import main
from ..__init__ import db
from ..models import User,Permission,Post
from .forms import PostForm,EditProfileForm,CommentForm
from flask.ext.sqlalchemy import get_debug_queries


@main.route('/',methods=['GET','POST'])
def index():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('index.html',form=form)


@main.route('/user/<username>')
def user(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)


@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data=current_user.name
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)


@main.route('/post/<int:id>')
def post(id):
    post=Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])


@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


