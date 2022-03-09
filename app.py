from flask import Flask,render_template,request,redirect
import pyrebase
app = Flask(__name__)
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
  email = email.replace("~","@").replace("`",".")
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
  email = email.replace("~","@").replace("`",".")
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
  email = email.replace("~", "@").replace("`", ".")
  c = 1
  res = list()
  data_file = db.child("Data").get()
  for details in data_file.each():
    if details.val()["Solver mail"] != "-" and details.val()["Student mail"] != email and details.val()["Solver mail"] != "Test" :
      res.append([details.val(), details.key(), c])
      c += 1
  return res

@app.route("/login/",methods=["POST","GET"])
def login_signup():
    return render_template("login_page.html")

@app.route("/signup/",methods=["POST","GET"])
def signup():
  message=""
  ermessage = ""
  if request.method == "POST":
    try:
      email = request.form["signup_email"]
      password = request.form["signup_password"]
      category = request.form["category"]
      auth.create_user_with_email_and_password(email, password)
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
    try:
      email = request.form["signin_email"]
      password = request.form["signin_password"]
      auth.sign_in_with_email_and_password(email, password)
      sumessage = "Successfully logged in"
      temp = "/"+email.replace("@","~").replace(".","`")+"p="+password+"/"
      print(temp)
      return redirect(temp)
    except:
      message = "Invalid email or password.Try again"
  return render_template("login_page.html",ermessage=message,sumessage = sumessage)

@app.route("/<string:inp>/",methods=["POST","GET"])
def aftersignin(inp):
  initial_list = inp.split("p=")
  email = initial_list[0].replace("~","@").replace("`",".")
  password = initial_list[1]
  try:
    auth.sign_in_with_email_and_password(email,password)
  except:
    return redirect("/login/")
  data_file = db.child("Category").get()
  for details in data_file.each():
    if details.key() == initial_list[0]:
      category = details.val()
  if request.method == "POST":
    if category == "Student":
      info = dict() #must include getting all the info and adding to the database
      info["Student name"] = request.form["Name"]
      info["Subject"] = request.form["Subject"]
      info["Contact details"] = request.form["Contact"]
      info["Question"] = request.form["Question"]
      info["Student mail"] = email
      info["Solver mail"] = "-"
      info["Answer"] = "-"
      db.child("Data").push(info)
    else:
      key = request.form["key"]
      ans = request.form["answer"]
      if check_solved(key) is False:
        db.child("Data").child(key).update({"Solver mail": email,"Answer":ans})
    return redirect("/" + inp + "/")
  if category == "Student":
    individual_student_list = get_individual_student_list(initial_list[0])    # returns a list of dictionary containing the details( argument given is changed email not the real one )
    solved_data = get_solved_questions(initial_list[0])
    return render_template("Student.html",inp="/"+inp+"/",data = individual_student_list , solved_data = solved_data)
  else:
    Student_list = get_complete_student_list()
    Solver_list = get_individual_solver_list(initial_list[0]) # returns a list of dictionary containing the details( argument given is changed email not the real one )
    return render_template("Solver.html",inp="/"+inp+"/",Student_list = Student_list,Solver_list = Solver_list)

@app.route("/")
def redir():
    return redirect("/login/")

app.run()