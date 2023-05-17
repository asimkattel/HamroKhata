import os
import time
import glob,subprocess
from flask import Flask, redirect, render_template, request, send_file,flash
import shutil
# Configure Application
app = Flask(__name__)
app.secret_key = "abc1"
global filename
global ftype


import sqlite3

conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT
    )
''')


cursor.close()
conn.close()


@app.route("/", methods=["GET", "POST"])
def welcome():
    # validation vare
    return redirect("/login")
    


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "GET":
        return render_template("signup.html", check=0) 

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()

        cursor=conn.cursor()

        # Check if the email already exists
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash("Email already exists. Please choose a different email.")
            return render_template("signup.html", check=1)  # Return error message

        # Insert the new user into the database
        cursor.execute('INSERT INTO users VALUES (?, ?)', (email, password))
        flash("Registration successful! Please log in.")
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/login")  # Redirect to login page
    

    


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", check=0)
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return redirect("/home")
        else:
            cursor.close()
            conn.close()
            flash("Invalid email or password.")
            return redirect("/login")

        
    


@app.route("/home")
def home():

    # Delete old files
    filelist = glob.glob('uploads/*')
    for f in filelist:
        os.remove(f)
    filelist = glob.glob('downloads/*')
    for f in filelist:
        os.remove(f)
    return render_template("home.html")

app.config["FILE_UPLOADS"] = "./uploads"




@app.route("/compress", methods=["GET", "POST"])
def compress():

    if request.method == "GET":
        return render_template("compress.html", check=0)

    else:
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            global filename
            global ftype
            filename = up_file.filename
            print(up_file.filename)
            up_file.save(os.path.join(app.config["FILE_UPLOADS"], filename))
            subprocess.call('c uploads\{}'.format(filename), shell=True)
            filename=filename.split(".")[0] 
            ftype=".compress"
            print("DONE COMPRESSION")
            return render_template("compress.html", check=1)

        else:
            print("ERROR")
            return render_template("compress.html", check=-1)

@app.route("/decompress", methods=["GET", "POST"])

def decompress():

    if request.method == "GET":
        return render_template("decompress.html", check=0)

    else:
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            global filename
            global ftype
            filename = up_file.filename
            up_file.save(os.path.join(app.config["FILE_UPLOADS"], filename))
            subprocess.call('d.exe .\\uploads\{}'.format(filename), shell=True)
            filename=filename.split(".")[0]
            ftype="_decompressed.txt"     
            shutil.copyfile("_decompressed.txt","./uploads/"+filename+ftype);       
            print("DONE DECOMPRESSION")
            return render_template("decompress.html", check=1)

        else:
            print("ERROR")
            return render_template("decompress.html", check=-1)





@app.route("/download")
def download_file():
    global filename
    global ftype
    path = "uploads\\" + filename + ftype
    return send_file(path, as_attachment=True)




# Restart application whenever changes are made
if __name__ == "__main__":
    app.run(debug = True)