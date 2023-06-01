import os
import glob,subprocess
from flask import Flask, redirect, render_template, request, send_file,flash,session
import hashlib
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
        username TEXT ,
        email TEXT PRIMARY KEY,
        password TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        email TEXT PRIMARY KEY,
        password TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS file (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    original_size REAL,
    compressed_size REAL,
    compression_ratio REAL,
    username TEXT
    )
''')
cursor.execute('SELECT * FROM admin WHERE email = ?', ('asim@gmail.com',))
if cursor.fetchone():
            # Admin already exists, no need to insert
            cursor.close()
            conn.close()
else:
            password = hashlib.md5( '123'.encode()).hexdigest();
            # Admin doesn't exist, insert the new admin
            cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', ('asim@gmail.com', password))
            conn.commit()
            cursor.close()
            conn.close()


@app.route("/", methods=["GET"])
def welcome():
   if request.method == "GET":
       
        return redirect("/login")

    


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "GET":
        return render_template("signup.html", check=0) 

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = hashlib.md5( request.form["password"].encode()).hexdigest()
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()

        # Check if the email already exists
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash("Email already exists. Please choose a different email.")
            return render_template("signup.html", check=1)  # Return error message

        # Insert the new user into the database
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (username, email, password))
        flash("Registration successful! Please log in.")
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/login")  # Redirect to login page

        
    

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('email', None)  # Remove the 'email' key from the session dictionary
    flash("Logged out successfully.")
    return redirect("/login")
 
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        return render_template("admin.html", check=0)
    elif request.method == "POST":
        email = request.form["email"]
        password = hashlib.md5( request.form["password"].encode()).hexdigest()
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM admin WHERE email = ? AND password = ?', (email, password))
        if cursor.fetchone():
            session['email'] = email
            cursor.close()
            conn.close()
            return redirect("/adminhome")
        else:
            cursor.close()
            conn.close()
            flash("Invalid email or password.")
            return redirect("/admin")

   


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", check=0)
    elif request.method == "POST":
        email = request.form["email"]
        password = hashlib.md5( request.form["password"].encode()).hexdigest()
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            session['email'] = email
            return redirect("/home")
        else:
            cursor.close()
            conn.close()
            flash("Invalid email or password.")
            return redirect("/login")


   

@app.route("/userdetails", methods=["GET"])
def userdetails():
    if request.method == "GET":
        if "email" not in session:
            flash("You are not logged in.")
            return redirect("/admin")
       
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
       
        cursor.close()
        conn.close()
        return render_template("userdetails.html", users = users)
    
      
@app.route("/filedetails", methods=["GET"])
def filedetails():
    if request.method == "GET":
        if "email" not in session:
            flash("You are not logged in.")
            return redirect("/admin")
       
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT
    file_id,
    filename,
    CASE
        WHEN original_size < 1024 THEN original_size || ' B'
        WHEN original_size < 1048576 THEN ROUND(original_size / 1024.0, 2) || ' KB'
        WHEN original_size < 1073741824 THEN ROUND(original_size / 1048576.0, 2) || ' MB'
        ELSE ROUND(original_size / 1073741824.0, 2) || ' GB'
    END AS original_size_formatted,
    CASE
        WHEN compressed_size < 1024 THEN compressed_size || ' B'
        WHEN compressed_size < 1048576 THEN ROUND(compressed_size / 1024.0, 2) || ' KB'
        WHEN compressed_size < 1073741824 THEN ROUND(compressed_size / 1048576.0, 2) || ' MB'
        ELSE ROUND(compressed_size / 1073741824.0, 2) || ' GB'
    END AS compressed_size_formatted,
printf("%.2f%%", (compression_ratio)) AS compression_ratio,username
FROM file;
''')
        files = cursor.fetchall()
       
        cursor.close()
        conn.close()
        return render_template("filedetails.html", files = files)
    
        
    


@app.route("/home")
def home():
    if request.method == "GET":
        # Retrieve the logged-in user's email from the session or wherever you store it
        if "email" not in session:
            flash("You are not logged in.")
            return redirect("/login")
        email = session["email"]  # Assuming you store the email in the session
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE email = ?;", (email,))
        users = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return render_template("home.html", users=users)


    # Delete old files
    filelist = glob.glob('uploads/*')
    for f in filelist:
        os.remove(f)
    filelist = glob.glob('downloads/*')
    for f in filelist:
        os.remove(f)
    return render_template("home.html")

app.config["FILE_UPLOADS"] = "./uploads"


@app.route("/adminhome")
def adminhome():
    if "email" not in session:
            flash("You are not logged in.")
            return redirect("/admin")
    
    return render_template("adminhome.html")






@app.route("/compress", methods=["GET", "POST"])
def compress():
    

    if request.method == "GET":
        if "email" not in session :
            flash("You are not logged in.")
            return redirect("/login")
        return render_template("compress.html", check=0)

    else:
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            global filename
            global ftype
            filename = up_file.filename
            if not filename.endswith(".txt"):
                error_message = "Invalid file extension. Only '.txt' files are allowed."
                return render_template("compress.html", check=-1, error=error_message)
            up_file.save(os.path.join(app.config["FILE_UPLOADS"], filename))
            original_file_size = os.path.getsize(os.path.join(app.config["FILE_UPLOADS"], filename))
 
            subprocess.call('c uploads\{}'.format(filename), shell=True)
            filename=filename.split(".")[0] 
            ftype=".compress"
            compressed_file_path = os.path.join(app.config["FILE_UPLOADS"], filename + ftype)
            compressed_file_size = os.path.getsize(compressed_file_path)
            ratio=(((original_file_size-compressed_file_size)/original_file_size)*100)
            print(compressed_file_size,original_file_size)
            email = session.get("email")
            conn = sqlite3.connect('user_database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            username = result[0] if result else None
            cursor.execute('INSERT INTO file(filename,original_size,compressed_size,compression_ratio,username) VALUES (?, ?, ?, ?, ?)', (filename, original_file_size, compressed_file_size,ratio,username))
            
            conn.commit()
            cursor.close()
            conn.close()
            return render_template("compress.html", check=1,osize=original_file_size,csize=compressed_file_size)
            

        else:
            
            return render_template("compress.html", check=-1)


@app.route("/decompress", methods=["GET", "POST"])
def decompress():

    if request.method == "GET":
        if "email" not in session:
            flash("You are not logged in.")
            return redirect("/login")
        return render_template("decompress.html", check=0)

    else:
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            global filename
            global ftype
            filename = up_file.filename
            if not filename.endswith(".compress"):
                error_message = "Invalid file extension. Only '.compress' files are allowed."
                return render_template("decompress.html", check=-1, error=error_message)

            up_file.save(os.path.join(app.config["FILE_UPLOADS"], filename))
            subprocess.call('d.exe .\\uploads\{}'.format(filename), shell=True)
            filename=filename.split(".")[0]
            ftype="_decompressed.txt"     
            shutil.copyfile("_decompressed.txt","./uploads/"+filename+ftype);       
       
            return render_template("decompress.html", check=1)

        else:
           
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