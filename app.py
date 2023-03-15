# save this as app.py
from flask import Flask, request,render_template, make_response, redirect

import pickle
import numpy as np
import sqlite3

app = Flask(__name__,template_folder='templates') 
model = pickle.load(open('model.pkl', 'rb'))
connection = sqlite3.connect("util.db", check_same_thread=False)

connection.execute("create table if not exists users(email text primary key, password text)")

@app.route('/')
def home():
    return render_template('index.html')

def is_leapyear(year):
    return (year % 400 == 0) and (year % 100 == 0)

@app.route('/predict',methods=['GET','POST'])
def predict():
    # Check if user is logged in
    email = request.cookies.get("email")

    if not email:
        return redirect("/login")

    if request.method == "GET":
        return render_template('prediction.html')
    
    if request.method ==  'POST':
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        education = request.form['education']
        employed = request.form['employed']
        credit = float(request.form['credit'])
        area = request.form['area']
        ApplicantIncome = float(request.form['ApplicantIncome'])
        CoapplicantIncome = float(request.form['CoapplicantIncome'])
        LoanAmount = float(request.form['LoanAmount'])
        Loan_Amount_Term = float(request.form['Loan_Amount_Term'])

        Loan_Amount_Term = Loan_Amount_Term * 365
        print(Loan_Amount_Term)
        # gender
        if (gender == "Male"):
            male=1
        else:
            male=0
        
        # married
        if(married=="Yes"):
            married_yes = 1
        else:
            married_yes=0

        # dependents
        if(dependents=='1'):
            dependents_1 = 1
            dependents_2 = 0
            dependents_3 = 0
        elif(dependents == '2'):
            dependents_1 = 0
            dependents_2 = 1
            dependents_3 = 0
        elif(dependents=="3+"):
            dependents_1 = 0
            dependents_2 = 0
            dependents_3 = 1
        else:
            dependents_1 = 0
            dependents_2 = 0
            dependents_3 = 0  

        # education
        if (education=="Not Graduate"):
            not_graduate=1
        else:
            not_graduate=0

        # employed
        if (employed == "Yes"):
            employed_yes=1
        else:
            employed_yes=0

        # property area

        if(area=="Semiurban"):
            semiurban=1
            urban=0
        elif(area=="Urban"):
            semiurban=0
            urban=1
        else:
            semiurban=0
            urban=0


        ApplicantIncomelog = np.log(ApplicantIncome)
        totalincomelog = np.log(ApplicantIncome+CoapplicantIncome)
        LoanAmountlog = np.log(LoanAmount)
        Loan_Amount_Termlog = np.log(Loan_Amount_Term)

        prediction = model.predict([[credit, ApplicantIncomelog,LoanAmountlog, Loan_Amount_Termlog, totalincomelog, male, married_yes, dependents_1, dependents_2, dependents_3, not_graduate, employed_yes,semiurban, urban ]])

        # print(prediction)

        if(prediction=="N"):
            prediction="No"
        else:
            prediction="Yes"

        return render_template("prediction.html", prediction_text="loan status is {}".format(prediction))



    else:
        return render_template("prediction.html")


@app.route("/login", methods=['GET','POST'])
def login():
    # check if logged in
    email = request.cookies.get("email")
    if email:
        return redirect("/predict")
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == "POST":
        type, message = "", ""
        email, password = request.form['email'], request.form['password']

        cursor = connection.cursor()

        query = "SELECT password FROM users where email = ?"

        cursor.execute(query,(email,))

        result = cursor.fetchone()

        if not result:
            type = "error"
            message = "No user found with that email!"
        else:
            real_pass = result[0]

            if real_pass != password:
                type = "error"
                message = "Invalid credentials"
            else:
                type = "success"
                message = "Logged in successfully! Redirecting..."
        cursor.close()
        response = make_response(render_template("login.html",type=type,message=message))
        if type=="success":
            response.set_cookie("email", email)
        return response
        

@app.route("/register", methods=['GET','POST'])
def register():
    email = request.cookies.get("email")
    if email:
        return redirect("/predict")
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == "POST":
        type, message = "", ""
        email, password = request.form['email'], request.form['password']

        cursor = connection.cursor()
        try:
            query = "insert into users(email, password) values(?,?)"
            cursor.execute(query,(email,password))
            connection.commit()
            cursor.close()
            type = "success"
            message = "User registered successfully! Redirecting..."
        except Exception as e:
            print(e)
            type = "error"
            message = "Unable to register user!"
        return render_template("register.html",type=type,message=message)
        




if __name__ == "__main__":
    app.run(debug=True)