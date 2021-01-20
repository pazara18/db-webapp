from flask import Flask, render_template, flash, redirect, url_for, session, request
from wtforms import Form, StringField, TextAreaField, IntegerField, PasswordField, SelectField, DateTimeField, \
    validators
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from passlib.hash import sha256_crypt
import psycopg2 as dbapi2
import psycopg2.extras as dbapi2extras
from functools import wraps
from werkzeug.utils import secure_filename
import ast
from datetime import datetime
from uuid import uuid4
import os

ENV = 'PROD'

app = Flask(__name__)
app.secret_key = 'secret123'
UPLOAD_PATH = "static/uploads/"
MYDIR = os.path.dirname(__file__)
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
DIR = MYDIR + "/" + UPLOAD_PATH
DORM_FOLDER = DIR + 'img/dorm/'
ROOM_FOLDER = DIR + 'img/room/'
RECEIPT_FOLDER = DIR + 'docs/'


# works
class RegisterStudentForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    surname = StringField('Surname', [validators.Length(min=1, max=50)])
    dateofbirth = DateTimeField('Date of Birth (Day-Month-Year)', format='%d-%m-%Y')
    phonenum = StringField('Phone Number', [validators.Length(min=10, max=11)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    room_list = []

    room = SelectField('Choose your Room', choices=room_list, validators=[validators.DataRequired()])


# works
class RegisterSupervisorForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    surname = StringField('Surrname', [validators.Length(min=1, max=50)])
    phonenum = StringField('Phone Number', [validators.Length(min=10, max=11)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    dorm_list = []

    dorm = SelectField('Choose your Dorm', choices=dorm_list, validators=[validators.DataRequired()])


# works
class AddDormForm(FlaskForm):
    dormname = StringField('Name of the Building', [validators.Length(min=1, max=50)])
    dormdescription = TextAreaField('Description for building', [validators.Length(min=20, max=1500)])
    picture = FileField('Add picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    room1_count = IntegerField('Number of 1-person Rooms', [validators.NumberRange(min=0, max=10)])
    room2_count = IntegerField('Number of 2-person Rooms', [validators.NumberRange(min=0, max=10)])
    room3_count = IntegerField('Number of 3-person Rooms', [validators.NumberRange(min=0, max=10)])
    room4_count = IntegerField('Number of 4-person Rooms', [validators.NumberRange(min=0, max=10)])
    room5_count = IntegerField('Number of 5-person Rooms', [validators.NumberRange(min=0, max=10)])


# works
class EditDormForm(FlaskForm):
    new_description = TextAreaField('New description for the dorm', [validators.Length(min=20, max=1500)])
    picture = FileField('New picture (optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])


# works
class AddRoomForm(FlaskForm):
    capacity = IntegerField('Room capacity', [validators.NumberRange(min=1, max=5)])
    name = StringField('Room name', [validators.Length(min=1, max=50)])
    picture = FileField('Add picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    description = TextAreaField('Description for the room', [validators.Length(min=20, max=1500)])
    price = IntegerField('Price of the room for 1 student', [validators.NumberRange(min=500)])


# works
class EditRoomForm(FlaskForm):
    new_capacity = IntegerField('New room capacity', [validators.NumberRange(min=1, max=5)])
    new_name = StringField('New room name', [validators.Length(min=1, max=50)])
    picture = FileField('New picture (optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    new_description = TextAreaField('New description for the room', [validators.Length(min=20, max=1500)])
    new_price = IntegerField('New price for 1 student', [validators.NumberRange(min=500)])


class ReceiptForm(FlaskForm):
    receipt = FileField('Upload Receipt (pdf)',
                        validators=[FileAllowed(['pdf'], 'PDF Documents only!'), FileRequired()])


# works
class SearchStudentForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    surname = StringField('Surname', [validators.Length(min=1, max=50)])


# works
class FileComplaintForm(FlaskForm):
    complaint = TextAreaField('Your Complaint', [validators.Length(min=20, max=1500)])


# works
class ReplyComplaintForm(FlaskForm):
    reply = TextAreaField('Your Reply', [validators.Length(min=20, max=1500)])


# works
class EditProfileForm(FlaskForm):
    phonenum = StringField('New Phone Number', [validators.Length(min=10, max=11)])


# works
def parse_tuple(string):
    s = ast.literal_eval(str(string))
    if type(s) == tuple:
        return s


# works
def get_dorm_list():
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor()
        cur.execute("SELECT (id,dormname) FROM building WHERE supervisorid IS NULL ORDER BY id ASC")
        dorms = cur.fetchall()
        cur.close()

    dorm_list = []

    for i in range(0, len(dorms)):
        d_tuple = parse_tuple(dorms[i][0])
        dorm_list.append(d_tuple)

    return dorm_list


# works
def get_room_list():
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor()
        cur.execute("SELECT (id,roomname) FROM room WHERE capacity > allotment ORDER BY id ASC")
        rooms = cur.fetchall()
        cur.close()

    room_list = []

    for i in range(0, len(rooms)):
        r_tuple = parse_tuple(rooms[i][0])
        room_list.append(r_tuple)

    return room_list


# works
def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"


# works
@app.route("/")
def home_page():
    return render_template('home.html')


# works
@app.route("/contact-us")
def contact_us_page():
    return render_template('contact-us.html')


# works
@app.route('/dorms')
def dorms():
    # Create cursor
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM BUILDING ORDER BY id ASC")
        dorms = cur.fetchall()
        cur.close()
    return render_template('dorms.html', dorms=dorms)


# works
@app.route('/dorm/<string:building_id>/')
def dorm(building_id):
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE id = %s", [building_id])
        dorm = cur.fetchone()
        cur.execute("SELECT * FROM room WHERE buildingid = %s ORDER BY id ASC", [building_id])
        rooms = cur.fetchall()
        cur.execute("SELECT * FROM supervisor WHERE id = %s", [dorm['supervisorid']])
        supervisor = cur.fetchone()
        cur.close()
    return render_template('dorm.html', dorm=dorm, supervisor=supervisor, rooms=rooms)


# works
@app.route('/room/<string:room_id>/')
def room(room_id):
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM room WHERE id = %s", [room_id])
        room = cur.fetchone()
        cur.execute("SELECT * FROM student WHERE roomno = %s ORDER BY id ASC", [room_id])
        students = cur.fetchall()
        cur.close()
    return render_template('room.html', room=room, students=students)


# works
@app.route('/register-student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm(request.form)
    form.room.choices = get_room_list()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        surname = form.surname.data
        dateofbirth = form.dateofbirth.data
        phonenum = form.phonenum.data
        email = form.email.data
        roomid = form.room.data
        password = sha256_crypt.hash(str(form.password.data))
        student_tuple = (roomid, name, surname, dateofbirth, phonenum, email, password)

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT email FROM student WHERE email = %s", [email])
            email_unique = cur.fetchone()
            if email_unique:
                flash('This email is already registered', 'danger')
                return redirect(url_for('register_student'))
            cur.close()

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT phonenum FROM student WHERE email = %s", [email])
            phonenum_unique = cur.fetchone()
            if email_unique:
                flash('This phone is already registered', 'danger')
                return redirect(url_for('register_student'))
            cur.close()

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT phonenum FROM student WHERE phonenum = %s", [phonenum])
            phonenum_unique = cur.fetchone()
            cur.close()
            if phonenum_unique:
                flash('This phone is already registered', 'danger')
                return redirect(url_for('register_student'))


        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute(
                "INSERT INTO student(roomno, firstname,surname,date_of_birth,phonenum, email,pword) VALUES (%s,%s,%s,"
                "%s,%s,%s,%s)",
                student_tuple)
            cur.execute("UPDATE room SET allotment = allotment + 1 WHERE id = %s", [roomid])
            cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register-student.html', form=form)


# works
@app.route('/register-supervisor', methods=['GET', 'POST'])
def register_supervisor():
    form = RegisterSupervisorForm(request.form)
    form.dorm.choices = get_dorm_list()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        surname = form.surname.data
        phonenum = form.phonenum.data
        email = form.email.data
        dormid = form.dorm.data
        password = sha256_crypt.hash(str(form.password.data))
        supervisor_tuple = (name, surname, phonenum, email, password)

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT email FROM student WHERE email = %s", [email])
            email_unique = cur.fetchone()
            cur.close()
            if email_unique:
                flash('This email is already registered', 'danger')
                return redirect(url_for('register_supervisor'))


        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT phonenum FROM student WHERE phonenum = %s", [phonenum])
            phonenum_unique = cur.fetchone()
            if phonenum_unique:
                flash('This phone is already registered', 'danger')
                return redirect(url_for('register_supervisor'))
            cur.close()

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO supervisor(firstname,surname,phonenum,email,pword) VALUES (%s,%s,%s,%s,%s)",
                        supervisor_tuple)
            cur.close()

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("SELECT * FROM supervisor WHERE email = %s", [email])
            supervisor = cur.fetchone()
            cur.close()

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("UPDATE building SET supervisorid = %s WHERE id = %s", [int(supervisor['id']), dormid])
            cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register-supervisor.html', form=form)


# works
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']
        usertype = request.form['usertype']

        if usertype == 'student':
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM student WHERE email = %s", [email])
                data = cur.fetchone()

        elif usertype == 'supervisor':
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM supervisor WHERE email = %s", [email])
                data = cur.fetchone()
        else:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM dormadmin WHERE email = %s", [email])
                data = cur.fetchone()
        cur.close()
        if data != None:
            password = data['pword']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email
                session['id'] = data['id']
                if usertype != 'admin':
                    session['firstname'] = data['firstname']
                    session['surname'] = data['surname']
                session['usertype'] = usertype

                flash('You are now logged in', 'success')
                return redirect(url_for('home_page'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection

        else:
            error = 'Record not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# works
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# works
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# works

# admin pages begin
@app.route('/manage-buildings')
@is_logged_in
def manage_buildings():
    if session['usertype'] == 'admin':
        return render_template('manage-dorms.html')
    else:
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))


# works
@app.route('/add-dorm', methods=['GET', 'POST'])
@is_logged_in
def add_dorm():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    form = AddDormForm()
    if form.validate_on_submit():
        name = form.dormname.data
        description = form.dormdescription.data
        room1_count = form.room1_count.data
        room2_count = form.room2_count.data
        room3_count = form.room3_count.data
        room4_count = form.room4_count.data
        room5_count = form.room5_count.data
        f = form.picture
        if f.data != None:
            filename = make_unique(secure_filename(f.data.filename))
            f.data.save(os.path.join(DORM_FOLDER, filename))
            dorm_tuple = (name, description, filename)
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO building(dormname,dormdescription,picture) VALUES (%s,%s,%s)", dorm_tuple)
                cur.close()
        else:
            dorm_tuple = (name, description)
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor()
                cur.execute("INSERT INTO building(dormname,dormdescription) VALUES (%s,%s)", dorm_tuple)
                cur.close()

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("SELECT * FROM building WHERE dormname = %s", [name])
            building = cur.fetchone()
            cur.close()

        for i in range(0, room1_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 1-person room #" + str(i + 1)
                roomdescription = roomname + " is a 1-person room in " + name
                capacity = 1
                default_1_price = 1750
                room_tuple = (building['id'], roomname, capacity, roomdescription, default_1_price)
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO room(buildingid,roomname,capacity,roomdescription, price) VALUES (%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()

        for i in range(0, room2_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 2-person room #" + str(i + 1)
                roomdescription = roomname + " is a 2-person room in " + name
                capacity = 2
                default_2_price = 1250
                room_tuple = (building['id'], roomname, capacity, roomdescription, default_2_price)
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO room(buildingid,roomname,capacity,roomdescription, price) VALUES (%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()

        for i in range(0, room3_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 3-person room #" + str(i + 1)
                roomdescription = roomname + " is a 3-person room in " + name
                capacity = 3
                default_3_price = 1000
                room_tuple = (building['id'], roomname, capacity, roomdescription, default_3_price)
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO room(buildingid,roomname,capacity,roomdescription, price) VALUES (%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()

        for i in range(0, room4_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 4-person room #" + str(i + 1)
                roomdescription = roomname + " is a 4-person room in " + name
                capacity = 4
                default_4_price = 750
                room_tuple = (building['id'], roomname, capacity, roomdescription, default_4_price)
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO room(buildingid,roomname,capacity,roomdescription, price) VALUES (%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()

        for i in range(0, room5_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 5-person room #" + str(i + 1)
                roomdescription = roomname + " is a 5-person room in " + name
                capacity = 5
                default_5_price = 500
                room_tuple = (building['id'], roomname, capacity, roomdescription, default_5_price)
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO room(buildingid,roomname,capacity,roomdescription, price) VALUES (%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()

        flash('Building added', 'success')
        return redirect(url_for('manage_buildings'))

    return render_template('add-dorm.html', form=form)


# works
@app.route('/remove-dorm', methods=['GET', 'POST'])
@is_logged_in
def remove_dorm():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    dormlist = request.form.getlist('dorm-checkbox')
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM BUILDING ORDER BY id ASC")
        dorms = cur.fetchall()
        cur.close()

    for item in dormlist:
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("DELETE FROM building WHERE id = %(id)s", {'id': int(item)})
            cur.close()

    if dormlist != []:
        flash('Dorm deleted', 'success')
        return redirect(url_for('manage_buildings'))

    return render_template('remove-dorm.html', dorms=dorms)


# works
@app.route('/delete-students', methods=['GET', 'POST'])
@is_logged_in
def delete_students():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    studentlist = request.form.getlist('student-checkbox')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM student")
        students = cur.fetchall()
        cur.close()

    if request.method == 'POST':
        for student in studentlist:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM student WHERE id = %(id)s", {'id': int(student)})
                student_row = cur.fetchone()
                if student_row['roomno']:
                    cur.execute("UPDATE ROOM SET allotment = allotment - 1 WHERE id = %(id)s",
                                {'id': int(student_row['roomno'])})
                cur.execute("DELETE FROM student WHERE id = %(id)s", {'id': int(student)})
                cur.close()

        if studentlist != []:
            flash('Student deleted', 'success')
            return redirect(url_for('home_page'))

    return render_template('remove-students.html', students=students)


# works
@app.route('/delete-supervisors', methods=['GET', 'POST'])
@is_logged_in
def delete_supervisors():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    supervisorlist = request.form.getlist('supervisor-checkbox')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM supervisor")
        supervisors = cur.fetchall()
        cur.close()

    for supervisor in supervisorlist:
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("DELETE FROM supervisor WHERE id = %(id)s", {'id': int(supervisor)})
            cur.close()

    if supervisorlist != []:
        flash('Student deleted', 'success')
        return redirect(url_for('home_page'))

    return render_template('remove-supervisors.html', supervisors=supervisors)


# works
@app.route('/process-requests')
@is_logged_in
def process_requests():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM request")
        requests = cur.fetchall()
        cur.close()
    return render_template('process-requests.html', requests=requests)


# works
@app.route('/request/<string:request_id>', methods=['GET', 'POST'])
@is_logged_in
def request_page(request_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM request WHERE request_id = %s", [request_id])
        request_row = cur.fetchone()
        cur.execute("SELECT * FROM student WHERE id = %s", [request_row['studentid']])
        student_row = cur.fetchone()
        cur.execute("SELECT * FROM room WHERE id = %s", [student_row['id']])
        old_room_row = cur.fetchone()
        cur.execute("SELECT * FROM room WHERE id = %s", [request_row['roomno']])
        room_row = cur.fetchone()
        cur.close()
    if request.method == 'POST':
        if request.form['submit_button'] == 'accept':
            if room_row['capacity'] > room_row['allotment']:
                with dbapi2.connect(DATABASE_URI) as connection:
                    cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                    if student_row['roomno']:
                        cur.execute("UPDATE ROOM SET allotment = allotment - 1 WHERE id = %(id)s",
                                    {'id': int(student_row['roomno'])})
                    cur.execute("UPDATE ROOM SET allotment = allotment + 1 WHERE id = %(id)s",
                                {'id': int(room_row['id'])})
                    if room_row['buildingid'] != old_room_row['buildingid']:
                        cur.execute("DELETE FROM complaint WHERE studentid = %s", [int(student_row['id'])])
                    cur.execute("UPDATE student SET roomno = %(roomno)s WHERE id = %(id)s",
                                {'roomno': int(room_row['id']), 'id': int(student_row['id'])})
                    cur.execute("UPDATE request SET is_responded = %s WHERE request_id = %s", [True, request_id])
                    cur.execute("UPDATE request SET is_approved = %s WHERE request_id = %s", [True, request_id])
                    cur.close()
                flash('Request approved', 'success')
                return redirect(url_for('home_page'))
            else:
                with dbapi2.connect(DATABASE_URI) as connection:
                    cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                    cur.execute("UPDATE request SET is_responded = %s WHERE request_id = %s", [True, request_id])
                    cur.close()
                flash('Room is already full! Press Reject Request to continue...', 'danger')
                return redirect(url_for('request_page', request_id=request_id))
        elif request.form['submit_button'] == 'reject':
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("UPDATE request SET is_responded = %s WHERE request_id = %s", [True, request_id])
                cur.execute("UPDATE request SET is_approved = %s WHERE request_id = %s", [False, request_id])
                cur.close()
            flash('Request rejected', 'danger')
            return redirect(url_for('home_page'))

    return render_template('request.html', request=request_row, student=student_row, room=room_row)


# works

# supervisor pages begin
@app.route('/search-students', methods=['GET', 'POST'])
@is_logged_in
def search_students():
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))
    form = SearchStudentForm(request.form)
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
        building = cur.fetchone()
        cur.close()
    if not building:
        flash('You cannot search as you are not assigned to a building', 'danger')
        return redirect(url_for('home_page'))
    if request.method == 'POST':
        student_name = form.name.data
        student_surname = form.surname.data

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute(
                "SELECT student.* FROM building JOIN room ON building.supervisorid = %s JOIN student ON student.roomno = room.id AND student.firstname = %s AND student.surname = %s",
                [building['id'], student_name, student_surname])
            student_row = cur.fetchall()
            cur.close()
        if not student_row:
            flash('No student exists by that name in your dorm!', 'danger')
            return redirect(url_for('home_page'))

        return render_template('search-students.html', students=student_row)

    return render_template('search-students.html')


# works
@app.route('/edit-dorm')
@is_logged_in
def edit_dorm():
    if session['usertype'] == 'supervisor':
        return render_template('edit-dorm.html')
    else:
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))


# works
@app.route('/add-room', methods=['GET', 'POST'])
@is_logged_in
def add_room():
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))
    form = AddRoomForm()
    if form.validate_on_submit():
        capacity = form.capacity.data
        name = form.name.data
        description = form.description.data
        price = form.price.data
        f = form.picture

        if f.data != None:
            filename = make_unique(secure_filename(f.data.filename))
            f.data.save(os.path.join(ROOM_FOLDER, filename))
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
                building = cur.fetchone()
                if not building:
                    flash('You cannot add rooms as you are not assigned to a building!', 'danger')
                    return redirect(url_for('home_page'))
                room_tuple = (building['id'], name, capacity, description, price, filename)
                cur.execute(
                    "INSERT INTO room(buildingid, roomname, capacity, roomdescription, price, picture) VALUES (%s,%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()
        else:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
                building = cur.fetchone()
                if not building:
                    flash('You cannot add rooms as you are not assigned to a building!', 'danger')
                    return redirect(url_for('home_page'))
                room_tuple = (building['id'], name, capacity, description, price)
                cur.execute(
                    "INSERT INTO room(buildingid, roomname, capacity, roomdescription, price) VALUES (%s,%s,%s,%s,%s)",
                    room_tuple)
                cur.close()
        flash('Room added', 'success')
        return redirect(url_for('home_page'))

    return render_template('add-room.html', form=form)


# works
@app.route('/remove-room', methods=['GET', 'POST'])
@is_logged_in
def remove_room():
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))
    roomlist = request.form.getlist('room-checkbox')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
        building = cur.fetchone()
        cur.execute("SELECT * FROM room WHERE room.buildingid = %s", [building['id']])
        rooms = cur.fetchall()
        cur.close()

    if request.method == 'POST':
        for room in roomlist:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("DELETE FROM room WHERE id = %(id)s", {'id': int(room)})
                cur.close()

        if roomlist != []:
            flash('Room(s) deleted', 'success')
            return redirect(url_for('home_page'))

    return render_template('remove-rooms.html', rooms=rooms)


# works
@app.route('/edit-room')
@is_logged_in
def edit_room():
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
        building = cur.fetchone()
        if not building:
            flash('You cannot edit rooms as you are not assigned to a building!', 'danger')
            return redirect(url_for('home_page'))
        cur.execute("SELECT * FROM room WHERE room.buildingid = %s", [building['id']])
        rooms = cur.fetchall()
        cur.close()

    return render_template('edit-rooms.html', rooms=rooms)


# works
@app.route('/edit-room/<string:room_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_room_page(room_id):
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))

    form = EditRoomForm()
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM room WHERE room.id = %s", [room_id])
        room = cur.fetchone()
        cur.close()

    if form.validate_on_submit():
        new_capacity = form.new_capacity.data
        new_name = form.new_name.data
        new_description = form.new_description.data
        new_price = form.new_price.data
        f = form.picture
        if new_capacity < int(room['allotment']):
            flash('New capacity cannot be lower than current occupant count!', 'danger')
            return redirect(url_for('home_page'))
        if f.data != None:
            filename = make_unique(secure_filename(f.data.filename))
            f.data.save(os.path.join(ROOM_FOLDER, filename))
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute(
                    "UPDATE room SET capacity = %s, roomname = %s, roomdescription = %s, price = %s, picture = %s WHERE room.id = %s",
                    [new_capacity, new_name, new_description, new_price, filename, room_id])
                cur.close()
        else:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute(
                    "UPDATE room SET capacity = %s, roomname = %s, roomdescription = %s, price = %s WHERE room.id = %s",
                    [new_capacity, new_name, new_description, new_price, room_id])
                cur.close()
        flash('Room updated', 'success')
        return redirect(url_for('home_page'))

    return render_template('edit-room.html', form=form, room=room)


# works
@app.route('/edit-dorm-descr', methods=['GET', 'POST'])
@is_logged_in
def edit_dorm_description():
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))
    form = EditDormForm()

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
        building = cur.fetchone()
        cur.close()
    if form.validate_on_submit():
        new_description = form.new_description.data
        f = form.picture
        if not building:
            flash('You cannot edit as you are not assigned to a dorm currently!', 'danger')
            return redirect(url_for('home_page'))
        if f.data != None:
            filename = make_unique(secure_filename(f.data.filename))
            f.data.save(os.path.join(DORM_FOLDER, filename))
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("UPDATE building SET dormdescription = %s, picture = %s WHERE building.id = %s",
                            [new_description, filename, building['id']])
                cur.close()
        else:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("UPDATE building SET dormdescription = %s WHERE building.id = %s",
                            [new_description, building['id']])
                cur.close()
        flash('Description updated', 'success')
        return redirect(url_for('home_page'))

    return render_template('edit-dorm-descr.html', dorm=building, form=form)


# works
@app.route('/reply-complaints')
@is_logged_in
def reply_complaints():
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('home_page'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE building.supervisorid = %s", [session['id']])
        building = cur.fetchone()
        cur.close()
    if not building:
        flash('You cannot respond to complaints as you are not assigned to a dorm!', 'danger')
        return redirect(url_for('home_page'))
    else:
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("SELECT * FROM complaint WHERE complaint.buildingid = %s AND complaint.is_responded = FALSE",
                        [building['id']])
            complaints = cur.fetchall()
            cur.close()

    return render_template('reply-complaints.html', complaints=complaints)


# works
@app.route('/complaint/<string:complaint_id>', methods=['GET', 'POST'])
@is_logged_in
def complaint_page(complaint_id):
    form = ReplyComplaintForm(request.form)
    reply = form.reply.data
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM complaint WHERE complaint.id = %s", [complaint_id])
        complaint = cur.fetchone()
        cur.close()

    if bool(session['usertype'] != 'supervisor') ^ bool(
            session['usertype'] == 'student' and session['id'] == int(complaint['studentid'])):
        flash('Complaints are visible to supervisor and the student only!', 'danger')
        return redirect(url_for('home_page'))

    if request.method == 'POST' and form.validate():
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("UPDATE complaint SET response = %s ,is_responded = %s WHERE complaint.id = %s",
                        [reply, True, complaint_id])
            cur.close()

        flash('Complaint Replied', 'success')
        return redirect(url_for('home_page'))

    return render_template('reply-complaint.html', form=form, complaint=complaint)


# works
@app.route('/supervisor-profile/<string:supervisor_id>')
@is_logged_in
def supervisor_profile(supervisor_id):
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM supervisor WHERE id = %s", [supervisor_id])
        supervisor = cur.fetchone()
        cur.execute("SELECT * FROM building WHERE supervisorid = %s", [supervisor_id])
        dorm = cur.fetchone()
        cur.close()
    return render_template('supervisor.html', supervisor=supervisor, dorm=dorm)


# works
@app.route('/edit-supervisor-profile/<string:supervisor_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_supervisor_profile(supervisor_id):
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    form = EditProfileForm()
    phone = form.phonenum.data
    if request.method == 'POST' and form.validate():

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT phonenum FROM supervisor WHERE phonenum = %s", [phone])
            phonenum_unique = cur.fetchone()
            cur.close()
            if phonenum_unique:
                flash('This phone is already registered', 'danger')
                return redirect(url_for('register_student'))
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("UPDATE supervisor SET phonenum = %s WHERE supervisor.id = %s", [phone, supervisor_id])
            cur.close()

        flash('Contact Info Updated', 'success')
        return redirect(url_for('home_page'))

    return render_template('edit-supervisor-profile.html', form=form)


# student pages begin

# works
@app.route('/upload-receipt', methods=['GET', 'POST'])
@is_logged_in
def upload_receipts_page():
    if session['usertype'] != 'student':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    form = ReceiptForm()
    f = form.receipt

    if form.validate_on_submit():
        filename = make_unique(secure_filename(f.data.filename))
        f.data.save(os.path.join(RECEIPT_FOLDER, filename))
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("SELECT * FROM student WHERE id = %s", [session['id']])
            student = cur.fetchone()
            cur.close()
        payment_tuple = (student['id'], student['roomno'], filename)
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO payment (studentid,roomno, receipt_file) VALUES (%s,%s,%s)", payment_tuple)
            cur.close()

        flash('Receipt Uploaded', 'success')
        return redirect(url_for('home_page'))

    return render_template('upload-receipt.html', form=form)


# todo
@app.route('/payment/<string:student_id>$<string:payment_date>', methods=['GET', 'POST'])
@is_logged_in
def payment_page(student_id, payment_date):
    year,month = payment_date.split('-')
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute(
            "SELECT * FROM payment WHERE studentid = %s AND EXTRACT (MONTH FROM payment_date) = %s AND EXTRACT (YEAR FROM payment_date) = %s", [student_id,month,year])
        payment=cur.fetchone()
        cur.close()
    if bool(session['usertype'] != 'supervisor') ^ bool(
            session['usertype'] == 'student' and session['id'] == int(payment['studentid'])):
        flash('Payments are visible to supervisor and the student only!', 'danger')
        return redirect(url_for('home_page'))

    if request.method == 'POST':
        if request.form['submit'] == 'accept':
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("UPDATE payment SET is_approved = %s WHERE studentid = %s AND payment_date = %s", [True, payment['studentid'], payment['payment_date']])
                cur.close()
                flash('Payment approved', 'success')
                return redirect(url_for('home_page'))
        elif request.form['submit'] == 'reject':
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                ur.execute("UPDATE payment SET is_approved = %s WHERE studentid = %s AND payment_date = %s", [False, payment['studentid'], payment['payment_date']])
                cur.close()
            flash('Payment rejected', 'danger')
            return redirect(url_for('home_page'))

    return render_template('payment.html', payment=payment)


# works
@app.route('/make-requests')
@is_logged_in
def make_requests():
    if session['usertype'] == 'student':
        return render_template('make-requests.html')
    else:
        flash('Unauthorized, Please login as student', 'danger')
        return redirect(url_for('home_page'))


# works
@app.route('/room-change-request', methods=['GET', 'POST'])
@is_logged_in
def room_change_requests():
    if session['usertype'] != 'student':
        flash('Unauthorized, Please login as student', 'danger')
        return redirect(url_for('home_page'))
    room_choice = request.form.getlist('room-radio')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM student WHERE id = %s", [session['id']])
        student = cur.fetchone()
        cur.execute("SELECT * FROM room WHERE capacity > allotment AND id != %s", [student['roomno']])
        rooms = cur.fetchall()
        cur.close()

    for room in room_choice:
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO request (studentid,roomno) VALUES (%s,%s)", (session['id'], room))
            cur.close()

    if room_choice != []:
        return redirect(url_for('home_page'))

    return render_template('room-change-request.html', rooms=rooms)


# works
@app.route('/file-complaint', methods=['GET', 'POST'])
@is_logged_in
def file_complaint():
    if session['usertype'] != 'student':
        flash('Unauthorized, Please login as student', 'danger')
        return redirect(url_for('home_page'))
    form = FileComplaintForm(request.form)
    if request.method == 'POST' and form.validate():
        complaint = form.complaint.data
        student_id = session['id']
        # do some sql magic to get building id from student id
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT roomno FROM student WHERE id = %s", (student_id,))
            roomno = cur.fetchone()
            cur.close()
        if roomno == (None,):
            flash('You cannot file a complaint as you are not staying in a room!', 'danger')
            return redirect(url_for('home_page'))

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT buildingid FROM room WHERE id = %s", (roomno,))
            buildingid = cur.fetchone()
            cur.close()

        complaint_tuple = (student_id, buildingid, complaint)
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO complaint(studentid, buildingid, complaint) VALUES (%s,%s,%s)",
                        complaint_tuple)
            cur.close()

        flash('Complaint filed', 'success')
        return redirect(url_for('home_page'))
    return render_template('file-complaint.html', form=form)


# works
@app.route('/student-profile/<string:student_id>')
@is_logged_in
def student_profile(student_id):
    room = None
    building = None
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM student WHERE id = %s", [student_id])
        student = cur.fetchone()
        if student['roomno']:
            cur.execute("SELECT * FROM room WHERE id = %s", [student['roomno']])
            room = cur.fetchone()
            cur.execute("SELECT * FROM building WHERE id = %s", [room['buildingid']])
            building = cur.fetchone()
        cur.execute("SELECT * FROM request WHERE studentid = %s", [student_id])
        requests = cur.fetchall()
        cur.execute("SELECT * FROM payment WHERE studentid = %s", [student_id])
        payments = cur.fetchall()
        cur.execute("SELECT * FROM complaint WHERE studentid = %s ", [student_id])
        complaints = cur.fetchall()
        cur.close()
    return render_template('student.html', student=student, room=room, building=building, requests=requests,
                           payments=payments, complaints=complaints)


# works
@app.route('/edit-student-profile/<string:student_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_student_profile(student_id):
    if session['usertype'] != 'student':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('home_page'))
    form = EditProfileForm()
    phone = form.phonenum.data
    if request.method == 'POST' and form.validate():
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT phonenum FROM student WHERE phonenum = %s", [phone])
            phonenum_unique = cur.fetchone()
            cur.close()
            if phonenum_unique:
                flash('This phone is already registered', 'danger')
                return redirect(url_for('register_student'))
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
            cur.execute("UPDATE student SET phonenum = %s WHERE student.id = %s", [phone, student_id])
            cur.close()

        flash('Contact Info Updated', 'success')
        return redirect(url_for('home_page'))

    return render_template('edit-student-profile.html', form=form)


if __name__ == "__main__":

    DATABASE_URI = os.getenv("DATABASE_URL")
    if ENV == 'PROD':
        app.debug = False
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        app.debug = True
        app.run()
