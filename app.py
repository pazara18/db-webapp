from flask import Flask, render_template, request


app = Flask(__name__)

ENV = 'DEV'

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


if __name__ == "__main__":
    app.run()
