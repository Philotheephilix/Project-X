import pandas as pd
import os
import csv
from flask import Flask, render_template, request, redirect, url_for, send_file
import pymongo
import xlsxwriter
app = Flask(__name__)
try:
    os.mkdir("report_data")
except:
    pass
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Project-X"]
collection = db["studentDet"]
# Dummy user data for demonstration (replace this with a database in a real application)

@app.route("/")
def index():
    return render_template("login/index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    result = collection.find_one({"key": "value"})
    query={"Roll No":username}
    resultt=collection.find_one(query)
    result=str(resultt["Reg No"])
    if password==result:
        print("done")
        return redirect(url_for("overview",username=username))
    else:
        # Invalid credentials, show an error message
        error = "Invalid username or password. Please try again."
        return render_template("login/index.html", error=error)

@app.route("/overview/<username>" )
def overview(username):
    query={"Roll No":username}
    resultt=collection.find_one(query)
    perc=resultt["attendance"]
    print(perc)
    perc_ring=perc*3.6
    perc="{:.2f}".format(perc)
    atte_per=resultt["atte_per"]
    total_per=resultt["total_per"]
    return(render_template("overview/overview.html",username=username,perc=perc,perc_ring=perc_ring,atte_per=atte_per,total_per=total_per))
@app.route("/profile/<username>")
def profile(username):
    query={"Roll No":username}
    resultt=collection.find_one(query)
    print(resultt)
    name=resultt["name"]
    print(name)
    roll=resultt["Roll No"]
    reg=resultt["Reg No"]
    yr=resultt["Yr"]
    age=resultt["Age"]
    sem=resultt["Sem"]
    dob=resultt["DOB"]
    email=resultt["Email"]
    cls=resultt["Cls"]
    ph=resultt["phone"]
    return render_template("profile/index.html",username=username,result=resultt,name=name,roll=roll,reg=reg,yr=yr,age=age,sem=sem,dob=dob,email=email,cls=cls,ph=ph)
    

@app.route("/report/<username>")
def report(username):
    try:
        os.mkdir("report_data/"+username)
    except:
        pass
    input_excel_file = 'data/attendance.xlsx'
    data = pd.read_excel(input_excel_file)
    data.to_csv('report_data/'+username+'/output.csv', index=False)

    with open('report_data/'+username+"/output.csv", mode='r') as file:
        csv_reader = csv.reader(file)
        list=[]
        for row in csv_reader:
            if "STUDENTS ATTENDANCE" in row:
                i=row.index("STUDENTS ATTENDANCE")
                row[i]=""
            if "DATE" in row:
                list.append(row[4:])
            if "DAY ORDER" in row:
                i=row.index("DAY ORDER")
                row[i]="DAY"
                list.append(row[4:])
            if username in row:
                list.append(row[4:])
    fname="report_data/" + username + "/"+username+".csv"
    with open(fname,"w") as file:
        writer=csv.writer(file)
        for i in list:
            writer.writerow(i)
    data1 = pd.read_csv("report_data/"+username+"/"+username+".csv")
    for i in range(54):
        a="Unnamed: "+str(i)
        data1.rename({a:i}, axis="columns", inplace=True)
    data1 = data1.dropna(axis=1, how='all')
    data1.at[3, data1.columns[1]] = None
    output_excel_file = "report_data/"+username+'/report.xlsx'
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        data1.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        for idx, col in enumerate(data1.columns):
            max_length = max(data1[col].astype(str).apply(len).max(), len(str(col)))
            worksheet.set_column(idx, idx, max_length)
    cleanup=os.listdir("report_data/"+username+"/")
    print(cleanup)
    for i in cleanup:
        if i!="report.xlsx":
            os.remove("report_data/"+username+"/"+i)
    report_path="report_data/"+username+"/report.xlsx"    
    return send_file(report_path, as_attachment=True)

@app.route("/welcome")
def welcome():
    return "Welcome to the protected area!"


if __name__ == "__main__":
    app.run(debug=True)
