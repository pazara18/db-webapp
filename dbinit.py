import psycopg2 as dbapi2
import app
INIT_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS DORMADMIN (
    id SERIAL PRIMARY KEY,
    email VARCHAR(40) UNIQUE NOT NULL,
    pword TEXT NOT NULL
    )""",

    """CREATE TABLE IF NOT EXISTS SUPERVISOR (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(30) NOT NULL,
    surname VARCHAR(30) NOT NULL,
    email VARCHAR(40) UNIQUE NOT NULL,
    pword TEXT NOT NULL,
    phonenum VARCHAR(20) UNIQUE
    )""",

    """CREATE TABLE IF NOT EXISTS BUILDING (
    id SERIAL PRIMARY KEY,
    supervisorid INTEGER REFERENCES SUPERVISOR(id) ON DELETE SET NULL,
    dormname VARCHAR(255) NOT NULL,
    dormdescription VARCHAR(255),
    picture VARCHAR(255)
    )""",

    """CREATE TABLE IF NOT EXISTS ROOM (
    id SERIAL PRIMARY KEY,
    buildingid INTEGER NOT NULL REFERENCES BUILDING(id) ON DELETE CASCADE,
    roomname VARCHAR(255) NOT NULL,
    capacity INTEGER NOT NULL,
    allotment INTEGER DEFAULT 0,
    roomdescription VARCHAR(255),
    picture VARCHAR(255)
    )""",

    """CREATE TABLE IF NOT EXISTS STUDENT (
    id SERIAL PRIMARY KEY,
    roomno INTEGER REFERENCES ROOM(id) ON DELETE SET NULL,
    firstname VARCHAR(30) NOT NULL,
    surname VARCHAR(30) NOT NULL,
    date_of_birth DATE NOT NULL,
    date_of_entrance DATE DEFAULT CURRENT_DATE,
    phonenum VARCHAR(20),
    email VARCHAR(40) UNIQUE NOT NULL,
    pword TEXT NOT NULL
    )""",

    """CREATE TABLE IF NOT EXISTS PAYMENT (
    studentid INTEGER NOT NULL REFERENCES STUDENT(id) ON DELETE CASCADE,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (studentid, payment_date),
    roomno INTEGER NOT NULL REFERENCES room(id) ON DELETE CASCADE,
    receipt_file BYTEA,
    is_approved BOOLEAN DEFAULT 'false'
    )""",

    """CREATE TABLE IF NOT EXISTS COMPLAINT(
    id SERIAL PRIMARY KEY,
    studentid INTEGER NOT NULL REFERENCES STUDENT(id) ON DELETE CASCADE,
    buildingid INTEGER NOT NULL REFERENCES BUILDING(id) ON DELETE CASCADE,
    complaint VARCHAR(255),
    response VARCHAR(255),
    is_responded BOOLEAN DEFAULT 'false'
    )""",

    """CREATE TABLE IF NOT EXISTS REQUEST (
    request_id SERIAL PRIMARY KEY,
    studentid INTEGER NOT NULL REFERENCES STUDENT(id) ON DELETE CASCADE,
    roomno INTEGER NOT NULL REFERENCES ROOM(id) ON DELETE CASCADE,
    is_responded BOOLEAN DEFAULT 'false',
    is_approved BOOLEAN
    )""",

    """INSERT INTO dormadmin(email, pword) VALUES
    ('ituyurtlariyonetici@itu.edu.tr', '$5$rounds=535000$UCLssf.SeAuyWazK$q7qXhMWVFRmmdDby3LurJFllPOMqv6ERkNC.Agfl3e.')"""
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    if app.ENV == 'DEV':
        url = "postgres://postgres:admin@localhost:5432/dorms"
    else:
        url ='postgres://tbplxswrvmlgow:992daea8a1c83983c8259008549cfbf384d58cecea2f13efc68ff4334261061f@ec2-34-192-72-159.compute-1.amazonaws.com:5432/ddtd1uh2u2t31p'
    initialize(url)
