from flask import Flask,flash,send_from_directory,render_template,request,redirect,session,g,url_for
import pyrebase
app = Flask(__name__)
app.config['SECRET_KEY'] = "c6e803cd18a8c528c161eb9fcf013245248506ffb540ff70"

firebaseConfig = {'apiKey': "AIzaSyAxKltWvPGTWzfL2qax0B8m6xnVcHdIqaM",
  'authDomain': "insight-3000.firebaseapp.com",
  'projectId': "insight-3000",
  'storageBucket': "insight-3000.appspot.com",
  'messagingSenderId': "999303532502",
  'appId': "1:999303532502:web:d9b476d91b69b0ecb0de77",
  'databaseURL' : "https://insight-3000-default-rtdb.asia-southeast1.firebasedatabase.app/"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

def get_individual_student_list(email):
  c=1
  res = list()
  data_file = db.child("Data").get()
  for details in data_file.each():
    if details.val()["Student mail"] == email:
      res.append([details.val(),c])
      c+=1
  return res

def get_complete_student_list():
  c = 1
  res = list()
  data_file = db.child("Data").get()
  for details in data_file.each():
    if details.val()["Solver mail"] == "-":
      res.append([details.val(),details.key(),c])
      c+=1
  return res

def get_individual_solver_list(email):
  c = 1
  res = list()
  data_file = db.child("Data").get()
  for details in data_file.each():
    if details.val()["Solver mail"] == email:
      res.append([details.val(),c])
      c+=1
  return res

def check_solved(key):
  data_file = db.child("Data").child(key).get()
  for details in data_file.each():
    if details.key() == "Solver mail":
      if details.val() == "-":
        return False
      else:
        return True

def get_solved_questions(email):
  c = 1
  res = list()
  data_file = db.child("Data").get()
  for details in data_file.each():
    if details.val()["Solver mail"] != "-" and details.val()["Student mail"] != email and details.val()["Solver mail"] != "Test" :
      res.append([details.val(), details.key(), c])
      c += 1
  return res

@app.route("/signup/",methods=["POST","GET"])
def signup():
  message=""
  ermessage = ""
  session.pop('logged_in', None)
  if request.method == "POST":
    try:
      email = request.form["signup_email"]
      password = request.form["signup_password"]
      category = request.form["category"]
      auth.create_user_with_email_and_password(email, password)
      session['logged_in'] = True
      session['email'] = email
      message = "Successfully Registered"
      username = email.replace("@","~").replace(".","`")
      db.child("Category").update({ username : category })
    except:
      ermessage = "User already registered"
  return render_template("login_page.html",regermessage = ermessage,regmessage = message )

@app.route("/signin/",methods=["POST","GET"])
def signin():
  message=""
  sumessage=""
  if request.method == "POST":
    email = request.form["signin_email"]
    password = request.form["signin_password"]
    session['email'] = email
    session['logged_in'] = True
    try:
      auth.sign_in_with_email_and_password(email, password)
      sumessage = "Successfully logged in"
      return redirect("/account/")
    except:
      message = "Invalid email or password.Try again"
  return render_template("login_page.html",ermessage=message,sumessage = sumessage)

@app.route("/account/",methods=["POST","GET"])
def aftersignin():
  try:
    email = session["email"].replace("@","~").replace(".","`")
  except:
    return redirect("/signin/")
  data_file = db.child("Category").get()
  for details in data_file.each():
    if details.key() == email:
      category = details.val()
  if request.method == "POST":
    if category == "Student":
      info = dict() #must include getting all the info and adding to the database
      info["Student name"] = request.form["Name"]
      info["Subject"] = request.form["Subject"]
      info["Contact details"] = request.form["Contact"]
      info["Question"] = request.form["Question"]
      info["Student mail"] = session["email"]
      info["Solver mail"] = "-"
      info["Answer"] = "-"
      db.child("Data").push(info)
    else:
      key = request.form["key"]
      ans = request.form["answer"]
      if check_solved(key) is False:
        db.child("Data").child(key).update({"Solver mail": session["email"],"Answer":ans})
    return redirect("/account/")
  if category == "Student":
    individual_student_list = get_individual_student_list(session["email"])    # returns a list of dictionary containing the details( argument given is changed email not the real one )
    solved_data = get_solved_questions(session["email"])
    return render_template("Student.html",inp="/account/",data = individual_student_list , solved_data = solved_data)
  else:
    Student_list = get_complete_student_list()
    Solver_list = get_individual_solver_list(session["email"]) # returns a list of dictionary containing the details( argument given is changed email not the real one )
    return render_template("Solver.html",inp="/account/",Student_list = Student_list,Solver_list = Solver_list)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    return redirect("/signin/")

@app.route("/")
def redir():
    return redirect("/signin/")

if __name__ == "__main__":
    app.run()
