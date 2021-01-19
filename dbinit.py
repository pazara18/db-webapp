import psycopg2 as dbapi2
import os

INIT_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS DORMADMIN (
    id SERIAL PRIMARY KEY,
    email VARCHAR(40) UNIQUE NOT NULL,
    pword TEXT NOT NULL
    )""",

    """CREATE TABLE IF NOT EXISTS SUPERVISOR (
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    pword TEXT NOT NULL,
    phonenum VARCHAR(20) UNIQUE
    )""",

    """CREATE TABLE IF NOT EXISTS BUILDING (
    id SERIAL PRIMARY KEY,
    supervisorid INTEGER REFERENCES SUPERVISOR(id) ON DELETE SET NULL,
    dormname VARCHAR(255) NOT NULL,
    dormdescription VARCHAR(4095),
    picture text
    )""",

    """CREATE TABLE IF NOT EXISTS ROOM (
    id SERIAL PRIMARY KEY,
    buildingid INTEGER NOT NULL REFERENCES BUILDING(id) ON DELETE CASCADE,
    roomname VARCHAR(255) NOT NULL,
    capacity INTEGER NOT NULL,
    allotment INTEGER DEFAULT 0,
    roomdescription VARCHAR(4095),
    price INTEGER NOT NULL,
    picture text
    )""",

    """CREATE TABLE IF NOT EXISTS STUDENT (
    id SERIAL PRIMARY KEY,
    roomno INTEGER REFERENCES ROOM(id) ON DELETE SET NULL,
    firstname VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    date_of_entrance DATE DEFAULT CURRENT_DATE,
    phonenum VARCHAR(50) UNIQUE,
    email VARCHAR(50) UNIQUE NOT NULL,
    pword TEXT NOT NULL
    )""",

    """CREATE TABLE IF NOT EXISTS PAYMENT (
    studentid INTEGER NOT NULL REFERENCES STUDENT(id) ON DELETE CASCADE,
    payment_date DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (studentid, payment_date),
    roomno INTEGER NOT NULL REFERENCES room(id) ON DELETE CASCADE,
    receipt_file text,
    is_approved BOOLEAN DEFAULT 'false'
    )""",

    """CREATE TABLE IF NOT EXISTS COMPLAINT(
    id SERIAL PRIMARY KEY,
    studentid INTEGER NOT NULL REFERENCES STUDENT(id) ON DELETE CASCADE,
    buildingid INTEGER NOT NULL REFERENCES BUILDING(id) ON DELETE CASCADE,
    complaint VARCHAR(4095),
    response VARCHAR(4095),
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
    url = 'postgres://postgres:admin@localhost:5432/dorms'
    # url = os.getenv("DATABASE_URL")
    initialize(url)
