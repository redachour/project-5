import models
import forms
import re

from flask import Flask, g, render_template, flash, redirect, url_for
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required
from models import User, Entry


app = Flask(__name__)
app.secret_key = 'gcftdrxdc451hb24gvfgcfghj4jhbgfqwertyui'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    '''Loads a User from the Database'''
    try:
        return User.get(User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    '''Connect to the database before each request'''
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    '''Close the database after each request'''
    g.db.close()
    return response


@app.route('/login', methods=('GET', 'POST'))
def login():
    '''Login user to add, edit and delete entries.'''
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = User.get(User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your username and password doesn't match", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Your username and password doesn't match", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    '''Logout user'''
    logout_user()
    flash("You've been logged out",  "success")
    return redirect(url_for('index'))


def slugify(slug):
    '''Delete all special characters from a slug'''
    return (re.sub('[^a-z0-9_\-]+', '', slug.lower()))


@app.route('/entry', methods=('GET', 'POST'))
@login_required
def add():
    '''Add an entry using a form and store it'''
    form = forms.AddEditForm()
    if form.validate_on_submit():
        Entry.create(title=form.title.data.strip(),
                     date=form.date.data,
                     time_spent=form.time_spent.data,
                     learned=form.learned.data.strip(),
                     resources=form.resources.data.strip(),
                     slug=slugify(form.title.data.strip()),
                     tags=form.tags.data.strip())
        flash("Entry added", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/')
@app.route('/entries')
@app.route('/entries/<tag>')
def index(tag=None):
    '''Home page which list all entries or specific tag entries'''
    if tag:
        entries = []
        for entry in Entry.select():
            for x in entry.tags.split(' '):
                if x == tag:
                    entries.append(entry)
    else:
        entries = Entry.select()
    return render_template('index.html', entries=entries)


@app.route('/details/<slug>')
def detail(slug):
    '''Shows details of a single entry'''
    entry = Entry.get(Entry.slug == slug)
    return render_template('detail.html', entry=entry)


@app.route('/entries/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit(slug=None):
    '''Allows the editing of entries'''
    form = AddEditForm()
    if form.validate_on_submit():
        Entry.update(title=form.title.data.strip(),
                     date=form.date.data.strip(),
                     time_spent=form.time_spent.data.strip(),
                     learned=form.learned.data.strip(),
                     resources=form.resources.data.strip(),
                     slug=slugify(form.title.data.strip()),
                     tags=form.tags.data.strip()
                     ).where(Entry.slug == slug).execute()
        flash("Entry Updated", 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form)


@app.route('/entries/delete/<slug>')
@login_required
def delete(slug):
    '''Allows the deleting of entries'''
    Entry.get(slug=slug).delete_instance()
    flash("Entry deleted", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    models.initialize()
    try:
        User.create_user(username='username',
                         password='password')
    except ValueError:
        pass
    app.run(debug=True)
