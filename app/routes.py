import os
import json
from flask import render_template, flash, url_for, request, send_from_directory
from sqlalchemy import and_
from werkzeug.utils import redirect
from app import app , db
from app.forms import LoginForm, RegistrationForm, SendMassage_addFriend, ProfileForm
from app.forms import LoginForm, RegistrationForm, SendMassage_addFriend, CourseForm
from flask_login import current_user, login_user, login_required , logout_user
from app.models import User, Course ,Category, Post , Enrollment, Comment, VideoViews, VideoRates, CourseVideo
from werkzeug.urls import url_parse

# @app.route('/home' , methods=['GET', 'POST'])  # bayad bere to home page(site landing page)
# def home():
#     courses = Course.query.all()
#     return render_template('home.html', title='Home' , courses = courses)

@app.route('/' , methods=['GET', 'POST'])
@app.route('/landing_page' , methods=['GET', 'POST'])
def landing_page():
    courses = Course.query.all()
    return render_template('landing_page/index.html', courses = courses)

@app.route('/about_us' , methods=['GET', 'POST'])
def about_us():
    return render_template('landing_page/about_us.html', title='About_us' )


def calc_avg_rate(course_id):
    avg_rate = 0
    video_rate = VideoRates.query.filter_by(course_id=course_id).all()
    if len(video_rate):
        for rate in video_rate:
            avg_rate += float(rate.rate)
        avg_rate /= len(video_rate)
    else:
        avg_rate = 0
    return str(avg_rate)


@app.route('/rate_video', methods=['POST'])
@login_required
def rate_video():
    video_rate = VideoRates.query.filter_by(course_id=request.form['course_id'], user_id=current_user.id).all()
    if len(video_rate):
        video_rate[0].rate = request.form['rate']
        db.session.commit()
    else:
        temp_rate = VideoRates(course_id=request.form['course_id'], user_id=current_user.id, rate=request.form['rate'])
        db.session.add(temp_rate)
        db.session.commit()

    return calc_avg_rate(request.form['course_id'])


@app.route('/my_course_views', methods=['GET'])
@login_required
def my_course_views():
    all_courses = Course.query.all()
    views_list = []
    for course in all_courses:
        all_views = VideoViews.query.filter_by(user_id=current_user.id, course_id=course.id).all()
        views_list.append([course.name, len(all_views)])
    return json.dumps(views_list)


@app.route('/course_video/<int:course_id>', methods=['GET', 'POST'])
@login_required
def comments(course_id):
    if request.method == 'GET':
        temp_rate = VideoRates.query.filter_by(course_id=course_id, user_id=current_user.id).all()
        if len(temp_rate):
            temp_rate = temp_rate[0].rate
        else:
            temp_rate = 0
        temp_view = VideoViews(course_id=course_id, user_id=current_user.id)
        db.session.add(temp_view)
        db.session.commit()
        all_views = VideoViews.query.filter_by(course_id=course_id).all()
        temp_comments = Comment.query.filter_by(course_id=course_id).all()
        course = Course.query.filter_by(id=course_id).first()
        video = CourseVideo.query.filter_by(course_id=course_id).first()
        return render_template('landing_page/video.html', title='course_video', temp_comments=temp_comments,
                               all_views=all_views,
                               temp_rate=temp_rate,
                               avg_rate=calc_avg_rate(course_id),
                               course_id=course_id,
                               course=course,
                               video=video)
    elif request.method == 'POST':
        course_id = request.form['course_id']
        email = request.form['email']
        author = request.form['author']
        text = request.form['text']
        temp_comment = Comment(text=text, author=author, email=email, course_id=course_id)
        db.session.add(temp_comment)
        db.session.commit()
        return redirect(url_for('comments', course_id=course_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_courses'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('my_courses')
        return redirect(next_page)
    return render_template('landing_page/login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('my_courses'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.set_img_url()
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('landing_page/register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing_page'))

@app.route('/profile' , methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    label1 =''
    label2 = ''
    flag =False
    if request.method=='POST' :
        if 'submitProfile' in request.form:
            if form.validate_on_submit()  :
                current_user.firstName = request.form['firstname']
                current_user.lastName = request.form['lastname']
                current_user.studyField = request.form['field_selection']
                print(request.form['field_selection'])
                current_user.university = request.form['university_selection']
                print(request.form['university_selection'])
                current_user.bio = request.form['bio']
                current_user.complete = True
                db.session.add(current_user)
                db.session.commit()
                label1 = 'your information submitted successfully ... '
        if 'changePassword' in request.form :
            if request.form['password'] !='':
                current_user.set_password(request.form['password'])
                db.session.add(current_user)
                db.session.commit()
                label2 = 'your password changed successfully ... '
            else:
                flag = True
                label2 = 'please enter correct password !! '

    return render_template('landing_page/profile.html', label1 = label1, label2 = label2 ,flag=flag,title='Friends' ,form=form)

@app.route('/dashboard' , methods=['GET', 'POST'])
@login_required
def my_courses():
    courses = Course.query.all()
    categories = Category.query.all()

    ens = current_user.enrollments
    goal_courses = []
    for enrollment in ens:
        if enrollment.user_id == current_user.id and enrollment.state == False:
            goal_courses.append(Course.query.filter_by(id=enrollment.course_id).first())

    friends = []
    frns_id = current_user.get_friend()
    for id in frns_id:
        friends.append(User.query.filter_by(id=id).first())

    # if request.method == 'POST':
    #     for category in categories:
    #         if category.ctg_name in request.form:
    #             courses = category.courses

    enrolled_courses = []
    # count enrolled courses for current_user to draw chart
    labels = []
    for ctg in categories:
        labels.append(ctg.ctg_name)

    values = []
    for ctg in categories:
        i = 0
        for enrollment in ens:
            crs = Course.query.filter_by(id=enrollment.course_id).first()
            if crs.related_category == ctg:
                i = i + 1
            # enrolled courses for current_user
            if enrollment.user_id == current_user.id and enrollment.state == True:
                if crs not in enrolled_courses :
                    enrolled_courses.append(crs)

        values.append(i)
    colors = ["#F7464A", "#46BFBD", "#FDB45C"]


    if request.method == 'POST':
        if 'course_name_filter' in request.form:
            filteredCourses = []
            filter = request.form['course_name_filter']
            if filter is not '':
                for crs in enrolled_courses:
                    if filter.lower() in crs.name.lower():
                        filteredCourses.append(crs)
                enrolled_courses = filteredCourses
        if 'course_name_desc_filter' in request.form:
            filteredCourses = []
            filter = request.form['course_name_desc_filter']
            if filter is not '':
                for crs in enrolled_courses:
                    if filter.lower() in crs.name.lower() or filter.lower() in crs.description.lower():
                        filteredCourses.append(crs)
                enrolled_courses = filteredCourses
        if 'goal_name_btn' in request.form:
            goal_id =request.form['goal_name_cancel']
            print('******************',goal_id,'*************________________***********')
            g = Course.query.filter_by(id=goal_id).first()
            en = Enrollment.query.filter(and_(Enrollment.related_course == g , Enrollment.related_user==current_user)).first()
            db.session.delete(en)
            db.session.commit()
            return redirect(url_for('my_courses'))
        if 'unfollow_btn' in request.form:
            friend_id =request.form['friend_name_unfollow']
            print('******************',friend_id,'*************________________***********')
            current_user.remove_friend(friend_id)
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('my_courses'))

    return render_template('landing_page/my_courses.html', title='Dashboard', courses=courses,
                           enrolled_courses=enrolled_courses,
                           categories=categories, goals=goal_courses, friends=friends,
                           max=12, labels=labels, values=values, set=zip(values, labels, colors))

@app.route('/all_courses' , methods=['GET', 'POST'])
@login_required
def all_courses():

    courses = Course.query.all()

    if request.method == 'POST':
        if 'course_name_filter' in request.form :
            filteredCourses=[]
            filter = request.form['course_name_filter']
            if filter is not '':
                for crs in courses:
                    if filter.lower() in crs.name.lower():
                        filteredCourses.append(crs)
                courses = filteredCourses
        if 'course_name_desc_filter' in request.form:
            filteredCourses = []
            filter = request.form['course_name_desc_filter']
            if filter is not '':
                for crs in courses:
                    if filter.lower() in crs.name.lower() or filter.lower() in crs.description.lower():
                        filteredCourses.append(crs)
                courses = filteredCourses
        if 'goal_name_btn' in request.form:
            goal_id =request.form['goal_name_cancel']
            print('******************',goal_id,'*************________________***********')
            g = Course.query.filter_by(id=goal_id).first()
            en = Enrollment.query.filter(and_(Enrollment.related_course == g , Enrollment.related_user==current_user)).first()
            db.session.delete(en)
            db.session.commit()
            return redirect(url_for('all_courses'))
        if 'unfollow_btn' in request.form:
            friend_id =request.form['friend_name_unfollow']
            print('******************',friend_id,'*************________________***********')
            current_user.remove_friend(friend_id)
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('all_courses'))

    categories = Category.query.all()

    ens = current_user.enrollments
    goal_courses = []
    for enrollment in ens:
        if enrollment.user_id == current_user.id and enrollment.state == False:
            goal_courses.append(Course.query.filter_by(id=enrollment.course_id).first())

    friends = []
    frns_id = current_user.get_friend()
    for id in frns_id:
        friends.append(User.query.filter_by(id=id).first())

    # if request.method == 'POST':
    #     for category in categories:
    #         if category.ctg_name in request.form:
    #             courses = category.courses


    enrolled_courses = []
    # count enrolled courses for current_user to draw chart
    labels = []
    for ctg in categories:
        labels.append(ctg.ctg_name)

    values = []
    for ctg in categories:
        i=0
        for enrollment in ens:
            crs = Course.query.filter_by(id = enrollment.course_id).first()
            if crs.related_category == ctg :
                i = i+1
            # enrolled courses for current_user
            if enrollment.user_id == current_user.id and enrollment.state == True:
                if crs not in enrolled_courses:
                    enrolled_courses.append(crs)

        values.append(i)
    colors = ["#F7464A", "#46BFBD", "#FDB45C"]

    return render_template('landing_page/all_courses.html', title='All Courses' , courses = courses , enrolled_courses = enrolled_courses ,
                           categories = categories , goals = goal_courses , friends = friends ,
                           max=12, labels=labels, values=values , set=zip(values, labels, colors))

@app.route('/all_courses/<int:category_id>' , methods=['GET', 'POST'])
@login_required
def filtered_courses(category_id):

    courses = Category.query.filter_by(id = category_id).first().courses

    if request.method == 'POST':
        filteredCourses=[]
        filter = request.form['course_name_filter']
        if filter is not '':
            for crs in courses:
                if filter.lower() in crs.name.lower():
                    filteredCourses.append(crs)
            courses = filteredCourses

    categories = Category.query.all()
    title = Category.query.filter_by(id = category_id).first().ctg_name
    ens = current_user.enrollments
    goal_courses = []
    for enrollment in ens:
        if enrollment.user_id == current_user.id and enrollment.state == False:
            goal_courses.append(Course.query.filter_by(id=enrollment.course_id).first())

    friends = []
    frns_id = current_user.get_friend()
    for id in frns_id:
        friends.append(User.query.filter_by(id=id).first())

    enrolled_courses = []
    # count enrolled courses for current_user to draw chart
    labels = []
    for ctg in categories:
        labels.append(ctg.ctg_name)

    values = []
    for ctg in categories:
        i=0
        for enrollment in ens:
            crs = Course.query.filter_by(id = enrollment.course_id).first()
            if crs.related_category == ctg :
                i = i+1
            # enrolled courses for current_user
            if enrollment.user_id == current_user.id and enrollment.state == True:
                if crs not in enrolled_courses:
                    enrolled_courses.append(crs)

        values.append(i)
    colors = ["#F7464A", "#46BFBD", "#FDB45C"]

    return render_template('landing_page/all_courses.html', title=title , courses = courses , enrolled_courses = enrolled_courses ,
                           categories = categories , goals = goal_courses , friends = friends,
                           max=12, labels=labels, values=values , set=zip(values, labels, colors))

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
@app.route('/allCourses/<int:courseId>' ,methods=['GET','POST'])
@login_required
def course(courseId) :

    course = Course.query.get(courseId)
    coursename = course.name
    description = course.description

    cform = CourseForm()

    # if (course) :
    #     #enrolledcourses = Enrollment.query.filter_by(and_(Enrollment.related_user==current_user ,Enrollment.state==True))

    if (request.method == 'POST') :

        if  'enroll' in request.form :
            en = Enrollment.query.filter(and_(Enrollment.related_course == course, Enrollment.related_user == current_user)).first()
            if en is None:
                enrollment = Enrollment(course_id=course.id , user_id=current_user.id ,state=True )
                db.session.add(enrollment)
                db.session.commit()
                flash('You are successfully enrolled in %s course!' %coursename)
                return redirect(url_for('viewCourse' , courseId=course.id))
            else:
                if en.state == False:
                    en.state = True
                    db.session.add(en)
                    db.session.commit()
                    return redirect(url_for('viewCourse', courseId=course.id))

        if 'remind' in request.form:
            en = Enrollment.query.filter(and_(Enrollment.related_course == course , Enrollment.related_user==current_user)).first()
            if en is None:
                remind = Enrollment(course_id=course.id , user_id=current_user.id, state = False)
                db.session.add(remind)
                db.session.commit()
                flash('You have added %s course to your goals.'%coursename )
                return redirect(url_for('my_courses'))
            else:
                return redirect(url_for('my_courses'))

    return render_template('landing_page/course-details.html', title='%s' % coursename, course=course)
    # else:
    #      return render_template('page_not_found.html'),404



@app.route('/viewCourse/<int:courseId>', methods=['GET','POST'])
@login_required
def viewCourse(courseId) :
    course = Course.query.get(courseId)
    #if (course) :
    return render_template('landing_page/learn-course.html', courseId=course.id, course=course)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../static'),
                               'favicon.ico', mimetype='img/vnd.microsoft.icon')

@app.route('/friends' , methods=['GET', 'POST'])
@login_required
def allFriends():
    form = SendMassage_addFriend()
    state=''
    friends_list=[]
    friends_id= User.get_friend(current_user)

    for id in friends_id:
     friend=User.query.get(id)
     friends_list.append(friend)

    uni = current_user.university
    field = current_user.studyField
    suggested=[]
    if current_user.complete == True and uni!='university' and field!='studyField':
        users = User.query.all()
        for user in users:
            if user!=current_user and user not in friends_list:
                if user.complete==True and user.university==uni and user.studyField==field:
                    suggested.append(user)

    error = ''
    if (request.method=='POST') and ('add' in request.form ) :

        friendusername =request.form['addfriend']
        new_friend = User.query.filter_by(username=friendusername).first()

        if (new_friend):
            if new_friend.id not in friends_id:
                User.add_friend(current_user,new_friend.id)
                db.session.commit()
                flash('Friend aded!')
                # redirect(url_for('allFriends'))
                return redirect(url_for('allFriends'))

            else:
                flash('Friend already exists!')
                error='exists'
        else:
            error = 'there is no account with this username !!'

    return render_template('landing_page/Friends.html', title='Friends' , Friends=friends_list, form=form ,error=error, state=state , suggested=suggested)


@app.route('/friends/<username>' , methods=['GET', 'POST'])
@login_required
def chat(username):
    form = SendMassage_addFriend()
    friend=User.query.filter_by(username=username).first()
    currentpost=Post.query.filter(and_(Post.user_id == current_user.id, Post.user2_id == friend.id,Post.send_receive == False ))
    friendpost=Post.query.filter(and_(Post.user_id == friend.id, Post.user2_id == current_user.id , Post.send_receive == False))
    posts=currentpost.union(friendpost)
    posts.order_by('post.timestamp')

    if (request.method == 'POST') and ( 'submit' in request.form ) :
        if (form.massage.data !=''):
            receiver =User.query.filter_by(username=username).first()
            post_sender= Post(body=form.massage.data,user_id=current_user.id ,user2_id=receiver.id,send_receive=False)
            post_receiver = Post(body=form.massage.data,user_id=receiver.id,user2_id=current_user.id, send_receive=True)
            db.session.add(post_sender)
            db.session.commit()
            db.session.add(post_receiver)
            db.session.commit()
            flash('Massage send!')
            form.massage.data=''
            form.receiver.data=''
        else:     flash('empty!')

    return render_template('landing_page/Chats.html',posts=posts,form=form,user=current_user,friend=friend)


@app.route('/activity' , methods=['GET'])
@login_required
def activity():
        return render_template('landing_page/Activity.html')












