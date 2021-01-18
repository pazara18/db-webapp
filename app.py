from flask import Flask, render_template, flash, redirect, url_for, session, request
from wtforms import Form, StringField, TextAreaField, IntegerField, PasswordField, SelectField, DateTimeField, \
    validators
from passlib.hash import sha256_crypt
import psycopg2 as dbapi2
import psycopg2.extras as dbapi2extras
from functools import wraps
import ast

app = Flask(__name__)

ENV = 'DEV'

if ENV == 'DEV':
    app.debug = True
    DATABASE_URI = 'postgres://postgres:admin@localhost:5432/dorms'
else:
    app.debug = False
    DATABASE_URI = 'postgres://xmumbtkwyfnwjw:f6b558df185eb87ebb43097a973d453d72e56112d28431d9867ab967ad686ef9@ec2-34' \
                   '-230-149-169.compute-1.amazonaws.com:5432/d2p706ei2cossa '


def parse_tuple(string):
    s = ast.literal_eval(str(string))
    if type(s) == tuple:
        return s


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
        cur.execute("SELECT * FROM BUILDING")
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
        cur.close()
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM room WHERE buildingid = %s", [building_id])
        rooms = cur.fetchall()
        cur.close()
    return render_template('dorm.html', dorm=dorm, rooms=rooms)


@app.route('/room/<string:room_id>/')
def room(room_id):
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM room WHERE id = %s", [room_id])
        room = cur.fetchone()
        cur.close()
    return render_template('room.html', room=room)


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

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor()
        cur.execute("SELECT (id,roomname) FROM room WHERE capacity > allotment")
        rooms = cur.fetchall()
        cur.close()

    room_list = []

    for i in range(0, len(rooms)):
        tuple = parse_tuple(rooms[i][0])
        room_list.append(tuple)

    room = SelectField('Choose your Room', choices=room_list, validators=[validators.DataRequired()])

    # add dorms as options but how?


# works
class RegisterSupervisorForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    surname = StringField('Surrname', [validators.Length(min=4, max=25)])
    phonenum = StringField('Phone Number', [validators.Length(min=10, max=11)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor()
        cur.execute("SELECT (id,dormname) FROM building WHERE supervisorid IS NULL")
        dorms = cur.fetchall()
        cur.close()

    dorm_list = []

    for i in range(0, len(dorms)):
        tuple = parse_tuple(dorms[i][0])
        dorm_list.append(tuple)

    print(dorm_list)

    dorm = SelectField('Choose your Dorm', choices=dorm_list, validators=[validators.DataRequired()])


# works
class AddDormForm(Form):
    dormname = StringField('Name of the Building', [validators.Length(min=1, max=50)])
    dormdescription = TextAreaField('Description for building', [validators.Length(min=30, max=250)])
    room1_count = IntegerField('Number of 1-person Rooms', [validators.NumberRange(min=0, max=10)])
    room2_count = IntegerField('Number of 2-person Rooms', [validators.NumberRange(min=0, max=10)])
    room3_count = IntegerField('Number of 3-person Rooms', [validators.NumberRange(min=0, max=10)])
    room4_count = IntegerField('Number of 4-person Rooms', [validators.NumberRange(min=0, max=10)])
    room5_count = IntegerField('Number of 5-person Rooms', [validators.NumberRange(min=0, max=10)])


# works
class AddRoomForm(Form):
    capacity = IntegerField('Room Capacity', [validators.NumberRange(min=0, max=5)])
    roomdescription = TextAreaField('Description for the Room', [validators.Length(min=30, max=250)])
    roomname = StringField('Name of the Room', [validators.Length(min=1, max=50)])


class FileComplaintForm(Form):
    complaint = TextAreaField('Your Complaint', [validators.Length(min=30, max=250)])


# works
@app.route('/register-student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        surname = form.surname.data
        dateofbirth = form.dateofbirth.data
        phonenum = form.phonenum.data
        email = form.email.data
        roomid = form.room.data
        password = sha256_crypt.encrypt(str(form.password.data))
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
            cur.execute("SELECT phonenum FROM student WHERE phonenum = %s", [phonenum])
            phonenum_unique = cur.fetchone()
            if phonenum_unique:
                flash('This phone is already registered', 'danger')
                return redirect(url_for('register_student'))
            cur.close()

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

    if request.method == 'POST' and form.validate():
        name = form.name.data
        surname = form.surname.data
        phonenum = form.phonenum.data
        email = form.email.data
        dormid = form.dorm.data
        password = sha256_crypt.encrypt(str(form.password.data))
        supervisor_tuple = (name, surname, phonenum, email, password)

        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("SELECT email FROM student WHERE email = %s", [email])
            email_unique = cur.fetchone()
            if email_unique:
                flash('This email is already registered', 'danger')
                return redirect(url_for('register_supervisor'))
            cur.close()

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

    return render_template('register-supervisor.html', form=form, dorms=dorms)


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
        return redirect(url_for('login'))


# works
@app.route('/add-dorm', methods=['GET', 'POST'])
@is_logged_in
def add_dorm():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('login'))
    form = AddDormForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.dormname.data
        description = form.dormdescription.data
        room1_count = form.room1_count.data
        room2_count = form.room2_count.data
        room3_count = form.room3_count.data
        room4_count = form.room4_count.data
        room5_count = form.room5_count.data

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
                room_tuple = (building['id'], roomname, capacity, roomdescription)
                cur = connection.cursor()
                cur.execute("INSERT INTO room(buildingid,roomname,capacity,roomdescription) VALUES (%s,%s,%s,%s)",
                            room_tuple)
                cur.close()

        for i in range(0, room2_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 2-person room #" + str(i + 1)
                roomdescription = roomname + " is a 2-person room in " + name
                capacity = 2
                room_tuple = (building['id'], roomname, capacity, roomdescription)
                cur = connection.cursor()
                cur.execute("INSERT INTO room(buildingid,roomname,capacity,roomdescription) VALUES (%s,%s,%s,%s)",
                            room_tuple)
                cur.close()

        for i in range(0, room3_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 3-person room #" + str(i + 1)
                roomdescription = roomname + " is a 3-person room in " + name
                capacity = 3
                room_tuple = (building['id'], roomname, capacity, roomdescription)
                cur = connection.cursor()
                cur.execute("INSERT INTO room(buildingid,roomname,capacity,roomdescription) VALUES (%s,%s,%s,%s)",
                            room_tuple)
                cur.close()

        for i in range(0, room4_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 4-person room #" + str(i + 1)
                roomdescription = roomname + " is a 4-person room in " + name
                capacity = 4
                room_tuple = (building['id'], roomname, capacity, roomdescription)
                cur = connection.cursor()
                cur.execute("INSERT INTO room(buildingid,roomname,capacity,roomdescription) VALUES (%s,%s,%s,%s)",
                            room_tuple)
                cur.close()

        for i in range(0, room5_count):
            with dbapi2.connect(DATABASE_URI) as connection:
                roomname = name + " 5-person room #" + str(i + 1)
                roomdescription = roomname + " is a 5-person room in " + name
                capacity = 5
                room_tuple = (building['id'], roomname, capacity, roomdescription)
                cur = connection.cursor()
                cur.execute("INSERT INTO room(buildingid,roomname,capacity,roomdescription) VALUES (%s,%s,%s,%s)",
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
        return redirect(url_for('login'))
    dormlist = request.form.getlist('dorm-checkbox')
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM BUILDING")
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
        return redirect(url_for('login'))
    studentlist = request.form.getlist('student-checkbox')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM student")
        students = cur.fetchall()
        cur.close()

    if request.method == 'POST':  # add allotment decrease via joins preferably
        for student in studentlist:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
                cur.execute("SELECT * FROM student WHERE id = %(id)s", {'id': int(student)})
                student = cur.fetchone()
                cur.execute("UPDATE ROOM SET allotment = allotment - 1 WHERE id = %(id)s", {'roomno': int(student)})
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
        return redirect(url_for('login'))
    supervisorlist = request.form.getlist('supervisor-checkbox')

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM supervisor")
        supervisors = cur.fetchall()
        cur.close()

    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building")
        buildings = cur.fetchall()
        cur.close()

    for building in buildings:
        if str(building['supervisorid']) in supervisorlist:
            with dbapi2.connect(DATABASE_URI) as connection:
                cur = connection.cursor()
                cur.execute("UPDATE building SET supervisorid = %s WHERE supervisorid = %s",
                            (None, building['supervisorid']))
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


# todo
@app.route('/process-requests')
@is_logged_in
def process_requests():
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('login'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM request WHERE is_responded = FALSE")
        requests = cur.fetchall()
        cur.close()
    return render_template('process-requests.html', requests=requests)


@app.route('/request/<string:request_id>', methods=['GET', 'POST'])
@is_logged_in
def request_page(request_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized, Please login as admin', 'danger')
        return redirect(url_for('login'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM request WHERE id = %s", [request_id])
        request = cur.fetchone()
        cur.execute("SELECT * FROM student WHERE id = %s", request['studentid'])
        student = cur.fetchone()
        cur.execute("SELECT * FROM room WHERE id = %s", request['roomno'])
        room = cur.fetchone()
        cur.close()

    return render_template('student.html', student=student)


# todo
# supervisor pages begin
@app.route('/search-students')
@is_logged_in
def search_students():
    # enter student name and surname to textbox
    # if supervisor is assigned to a building, search within that building using joins
    # if supervisor is unemployed print you cant search and return to home_page
    return "TODO"


# todo
@app.route('/edit-dorm')
@is_logged_in
def edit_dorm():
    # if supervisor is assigned to a building collect values from textbox and uploaded image
    # update database with new values
    return "TODO"


# todo
@app.route('/reply-complaints')
@is_logged_in
def reply_complaints():
    # display all complaints made by the students in the building
    # click on individual complaints and write replies to textbox
    return "TODO"


# add edit functionality
@app.route('/supervisor-profile/<string:supervisor_id>')
@is_logged_in
def supervisor_profile(supervisor_id):
    if session['usertype'] != 'supervisor':
        flash('Unauthorized, Please login as supervisor', 'danger')
        return redirect(url_for('login'))
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM supervisor WHERE id = %s", [supervisor_id])
        supervisor = cur.fetchone()
        cur.close()
    return render_template('supervisor.html', supervisor=supervisor)


# todo
@app.route('/upload-receipt')
@is_logged_in
def upload_receipts_page():
    # have filebox that accepts pdf inputs
    # create payment entity in database
    return "TODO"


# works
@app.route('/make-requests')
@is_logged_in
def make_requests():
    if session['usertype'] == 'student':
        return render_template('make-requests.html')
    else:
        flash('Unauthorized, Please login as student', 'danger')
        return redirect(url_for('login'))


@app.route('/room-change-request', methods=['GET', 'POST'])
@is_logged_in
def room_change_requests():
    if session['usertype'] != 'student':
        flash('Unauthorized, Please login as student', 'danger')
        return redirect(url_for('login'))
    room_choice = request.form.getlist('room-radio')
    # display dorms as options
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM room WHERE capacity > allotment")
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


@app.route('/file-complaint', methods=['GET', 'POST'])
@is_logged_in
def file_complaint():
    if session['usertype'] != 'student':
        flash('Unauthorized, Please login as student', 'danger')
        return redirect(url_for('login'))
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

        complaint_tuple = (student_id, buildingid, complaint, is_responded)
        with dbapi2.connect(DATABASE_URI) as connection:
            cur = connection.cursor()
            cur.execute("INSERT INTO complaint(studentid, buildingid, complaint,is_responded) VALUES (%s,%s,%s,%s)",
                        complaint_tuple)
            cur.close()

        flash('Complaint filed', 'success')
        return redirect(url_for('home_page'))
    return render_template('file-complaint.html', form=form)


# add edit profile functionality
@app.route('/student-profile/<string:student_id>')
@is_logged_in
def student_profile(student_id):
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM student WHERE id = %s", [student_id])
        student = cur.fetchone()
        cur.close()
    return render_template('student.html', student=student)


if __name__ == "__main__":
    app.secret_key = '3169420'
    app.run()
