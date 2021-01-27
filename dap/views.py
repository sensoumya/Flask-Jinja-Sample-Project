from . import app
from datetime import timedelta
from .forms import RegistrationForm, LoginForm
from .db import UIUsers, Templates
from .data import getUIData
from .format import format
from flask import render_template, url_for, flash, redirect, request, jsonify, session, g
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if g.user:
            return f(*args, **kwargs)
        else:
            flash('Login Required!', 'danger')
            return redirect(url_for('login', next=request.path[1:]))
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if UIUsers.find_user(g.user).access == 'admin':
            return f(*args, **kwargs)
        else:
            flash("You don't have admin rights!", 'danger')
            return redirect(url_for('home'))
    return wrapper


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10)


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    templates = Templates.fetchTemplates()
    all_attrib = []
    if 'all' in templates:
        templates.remove('all')
        all_attrib = Templates.findTemplate('all').templatedata
    attribs = []
    template = ''
    if request.method != 'POST':
        return render_template('home.html', all_attrib=all_attrib, templates=templates)
    if request.form.get('tmplt') is None and request.form.get('new_template_name') is None:
        flash(f'Select a template first', 'danger')
        return render_template('home.html', all_attrib=all_attrib, templates=templates)
    if request.form.get('tmplt'):
        template = request.form.get('new_template_name') if request.form.get(
            'new_template_name') else request.form.get('tmplt')
        attribs = Templates.fetchAttributes(template)
    return render_template('home.html', all_attrib=all_attrib,
                           sel_attrib=attribs, template=template, templates=templates)


@app.route("/update", methods=['GET', 'POST'])
@login_required
def update():
    if request.form.get('tmplt') is None:
        return redirect(url_for('home'), code=307)
    if request.method == 'POST' and request.form.get('tmplt'):
        temp = request.form.get('tmplt')
        attribs = request.form.getlist('attr[]')
        template = Templates.findTemplate(temp)
        template.templatedata = attribs
        template.save()
        flash(f'{temp} updated successfully!', 'success')
        return redirect(url_for('home'), code=307)


@app.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
    if request.form.get('tmplt') is None:
        return redirect(url_for('home'), code=307)
    if request.method == 'POST' and request.form.get('tmplt'):
        Templates.delTemplate(request.form.get('tmplt'))
        flash(f'{request.form.get("tmplt")} deleted!', 'success')
        return redirect(url_for('home'))


@app.route("/save", methods=['GET', 'POST'])
@login_required
def save():
    if request.form.get('new_template_name'):
        template_name = request.form.get('new_template_name')
        template_attribs = request.form.get('template_attribs').split(
            ',') if request.form.get('template_attribs') else request.form.getlist('attr[]')
        if Templates.findTemplate(template_name):
            flash('Save with different name', 'danger')
            return redirect(url_for('home'), code=307)
        try:
            Templates.saveTemplate(template_name, template_attribs)
            flash(f'{template_name} saved', 'success')
        except:
            flash(f'Unable to save {template_name}!', 'danger')
            return redirect(url_for('home'), code=307)
        return redirect(url_for('home'), code=307)
    return redirect(url_for('home'))


@app.route("/data", methods=['GET', 'POST'])
@login_required
def data():
    if request.form.getlist('attr[]'):
        return jsonify(getUIData(request.form.getlist('attr[]')))
    return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if not form.access.data:
            print('Danger')
            flash('Fill all the details!', 'danger')
            return redirect(url_for('register'))
        user = UIUsers(username=form.username.data, password=UIUsers.generate_hash(form.password.data),
                       access=form.access.data)
        try:
            user.save()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('register'))
        except:
            flash('Something went wrong!', 'danger')
    return render_template('register.html', form=form)


@app.route("/users", methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    all_users = [u.username for u in UIUsers.query.all()]
    if request.method != 'POST':
        return render_template('users.html', all_users=all_users)
    username = request.form.get('sel_user')
    user = UIUsers.find_user(username)
    if request.form.get('change_pass'):
        user.password = UIUsers.generate_hash(request.form.get('password'))
        user.save()
        flash(f'Password for {username} has been updated!', 'success')
        return redirect(url_for('users'))
    if request.form.get('change_access'):
        user.access = request.form.get('access')
        user.save()
        flash(f'Access permission for {username} has been updated!', 'success')
        return redirect(url_for('users'))
    if request.form.get('del_user'):
        if user.username == 'admin@admin.com':
            flash(f'Admin user deletion not allowed!', 'danger')
            return redirect(url_for('users'))
        user.remove()
        flash(f'User: {user.username} deleted', 'success')
        return redirect(url_for('users'))
    return render_template('users.html', user=user, all_users=all_users)


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UIUsers.find_user(form.username.data)
        if user and UIUsers.verify_hash(form.password.data, user.password):
            session['user'] = form.username.data
            if request.args.get(next):
                return redirect(url_for(request.args.get(next)))
            return redirect(url_for('home'))
        else:
            flash(f'Invalid credentials, try again!', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
