from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import psycopg2 as dbapi2
import psycopg2.extras as dbapi2extras
from functools import wraps


app = Flask(__name__)

ENV = 'PROD'

if ENV == 'DEV':
    app.debug = True
    DATABASE_URI = 'postgres://postgres:admin@localhost:5432/dorms'
else:
    app.debug = False
    DATABASE_URI = 'postgres://xmumbtkwyfnwjw:f6b558df185eb87ebb43097a973d453d72e56112d28431d9867ab967ad686ef9@ec2-34-230-149-169.compute-1.amazonaws.com:5432/d2p706ei2cossa'

@app.route("/")
def home_page():
    return render_template('home.html')

@app.route("/contact-us")
def contact_us_page():
    return render_template('contact-us.html')

@app.route('/dorms')
def articles():
    # Create cursor
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM BUILDING")
        dorms = cur.fetchall()
        return render_template('dorms.html', dorms=dorms)
        # Close connection
        cur.close()

@app.route('/dorm/<string:building_id>/')
def dorm(building_id):
    with dbapi2.connect(DATABASE_URI) as connection:
        cur = connection.cursor(cursor_factory=dbapi2extras.RealDictCursor)
        cur.execute("SELECT * FROM building WHERE id = %s", [building_id])
        dorm = cur.fetchone()
        return render_template('dorm.html', dorm=dorm)
        # Close connection
        cur.close()

if __name__ == "__main__":
    app.run()
