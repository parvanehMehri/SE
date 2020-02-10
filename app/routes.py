import os

from flask import render_template, flash, url_for, request, send_from_directory
from werkzeug.utils import redirect
from app import app , db
from app.forms import LoginForm, RegistrationForm, SendMassage_addFriend
from flask_login import current_user, login_user, login_required , logout_user
from app.models import User, Course , Post , Enrollment
from werkzeug.urls import url_parse

@app.route('/home' , methods=['GET', 'POST'])  # bayad bere to home page(site landing page)
def home():
    courses = Course.query.all()
    return render_template('home.html', title='Home' , courses = courses)

@app.route('/landing_page' , methods=['GET', 'POST'])
def landing_page():
    courses = Course.query.all()
    return render_template('landing_page/index.html', courses = courses)

@app.route('/about_us' , methods=['GET', 'POST'])
def about_us():
    return render_template('landing_page/about_us.html', title='About_us' )


@app.route('/index')  # manzoor az index va home hamon dashboard ast ... :)
@login_required
def index():
    return render_template('index.html', title='Index')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.set_img_url()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/allCourses' , methods=['GET', 'POST'])
@login_required
def allCourses():
    courses = Course.query.all()
    if request.method == 'POST':
        filter = request.form['course_name_filter']
        if filter is not '':
            filtered_courses = Course.query.filter_by(name=filter)
            courses = filtered_courses
    return render_template('allCourses.html', title='all courses' , courses = courses)

@app.route('/goals' , methods=['GET', 'POST'])
@login_required
def goals():
    ens = current_user.enrollments
    goal_courses= []
    for enrollment in ens :
        if enrollment.state == False :
            goal_courses.append( Course.query.filter_by(id = enrollment.course_id).first() )

    return render_template('goals.html', title='goals' , courses = goal_courses)

# @app.route('/course#1' , methods=['GET', 'POST'])
# @login_required
# def course():
#     if request.method == 'POST':
#         # enroll
#         crs = Course.query.get(1)
#         en = Enrollment(related_course = crs , related_user = current_user , state = True)
#         db.session.add(en)
#         db.session.commit()
#
#         # read later
#         crs = Course.query.get(1)
#         en = Enrollment(related_course=crs, related_user=current_user, state=False)
#         db.session.add(en)
#         db.session.commit()
#
#     return render_template('course#1.html', title='Course#1')


#
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('page_not_found.html'), 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='img/vnd.microsoft.icon')

@app.route('/friends' , methods=['GET', 'POST'])
@login_required
def allFriends():

 friends_list=[]
 form = SendMassage_addFriend()
 if (current_user.friends):
       frnds_id= User.get_friend(current_user)

       for id in frnds_id:
          friend_user= User.query.get(id)
          friends_list.append(friend_user)

       if request.method == 'POST' and form.massage.data !='':
            receiver_username =form.receiver.data
            receiver =User.query.filter_by(username=receiver_username).first()
            post_sender = Post(body=form.massage.data,user_id=current_user.id ,send_receive=False)
            post_receiver = Post(body=form.massage.data,user_id=receiver.id, send_receive=True)
            db.session.add(post_sender)
            db.session.commit()
            db.session.add(post_receiver)
            db.session.commit()
            flash('Massage send!')
            form.massage.data=''
 else: flash('no friend')

 if request.method=='POST'and form.addfriend.data !='' :
    fuser =request.form['addfriend']
    new_friend = User.query.filter_by(username=fuser).first()
    User.add_friend(current_user,new_friend.id)
    db.session.commit()
    flash('Friend aded!')
    return redirect(url_for('allFriends'))

 return render_template('Friends.html', title='Friends' , Friends=friends_list,form=form )





