from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Boolean

app = Flask(__name__)

engine = create_engine("sqlite:///needyPeople.db",echo=True)
meta = MetaData()

needy = Table("n_people", meta, 
Column("id", Integer, primary_key=True),
Column("name", String),
Column("age", Integer),
Column("sex", String),
Column("bg", String),
Column("disability", String),
Column("loc", String)
)

ngos = Table("ngos", meta, 
Column("id", Integer, primary_key=True),
Column("name", String),
Column("loc", String),
Column("dons_rcv", Integer),
Column("hlpd", Integer)
)

@app.route("/",methods=["GET","POST"])
def home() :
        return render_template("index.html")

@app.route("/success", methods=["GET","POST"])
def success_page() :
    if request.method == "POST":
        return redirect(f"{url_for('home')}")
    else :
        return render_template("success.html")

@app.route("/createneedyprofile", methods=["GET", "POST"])
def create_needy_profile() :
    if request.method == "POST" :
        profile = [ request.form["name"],
        request.form["age"],
        request.form["gender"],
        request.form["bldgrp"],
        request.form["phydis"],
        request.form["loc"] ]
        add_to_needy_database(profile)
        return redirect(f"{url_for('success_page')}")
    else :
         return render_template("needy_profile.html")

@app.route("/registerngo", methods=["GET", "POST"])
def register_ngo() :
    if request.method == "POST" :
        data = [ request.form["name"],
        request.form["loc"],
        request.form["don"],
        request.form["nop"]
        ]
        add_to_ngo_database(data)
        return redirect("/")
    else :
        return render_template("RegisterNgo.html")

@app.route("/ngolist")
def ngo_list() :
    conn = engine.connect()

    command = f"""SELECT * FROM ngos"""

    res = conn.execute(command)

    lst = []
    for e in res :
        lst.append(list(e)[1])

    return render_template("ngo_list.html", ngos=lst)

@app.route("/searchbyloc", methods=["GET", "POST"])
def search_by_loc() :
    if request.method == "POST" :
        url = f"/ngoprofile/" + str(request.form["ngo"])
        return redirect(url)
    else :
        conn = engine.connect()

        locs = []
        ngos_lst = []
        
        ngos_select = conn.execute("SELECT * FROM ngos")

        for ngo in ngos_select :
            if(ngo[2] in locs) :
                ngos_lst[locs.index(ngo[2])].append(ngo[1])
            else :
                locs.append(ngo[2])
                ngos_lst.append([])
                ngos_lst[-1].append(ngo[1])

        return render_template("search.html", locs=locs, ngos_lst=ngos_lst)

@app.route("/needylist")
def needy_list() :
    conn = engine.connect()

    command = f"""SELECT * FROM n_people"""

    res = conn.execute(command)

    lst = []
    for e in res :
        lst.append(list(e)[1])

    return render_template("needy_list.html", names=lst)

@app.route("/needyprofile/<name>")
def needy_profile(name) :
    conn = engine.connect()

    command = f"""SELECT * FROM n_people WHERE name = '{name}'"""

    prof = list(conn.execute(command))  

    return render_template("needy_profile_display.html", name=prof[0][1], age=prof[0][2], sex=prof[0][3], bg=prof[0][4], disability=prof[0][5], loc=prof[0][6])

@app.route("/ngoprofile/<name>", methods=["GET", "POST"])
def ngo_profile(name):
    conn = engine.connect()

    command = f"""SELECT * FROM ngos WHERE name = '{name}'"""

    prof = list(conn.execute(command))
    
    if request.method == "GET" :
        return render_template("ngo_profile.html", name = prof[0][1], loc=prof[0][2], dons=prof[0][3], hlpd=prof[0][4])
    else :
        return redirect(f"/donate/{prof[0][1]}")


@app.route("/donate/<name>", methods=["GET","POST"])
def donate(name) :
    conn = engine.connect()

    command = f"""SELECT * FROM ngos WHERE name = '{name}'"""

    prof = list(conn.execute(command))
    
    if request.method == "POST" :
        upd = ngos.update().where(ngos.c.name == name).values(dons_rcv=int(prof[0][3]) + int(request.form["mtrans"]))
        conn.execute(upd)
        return redirect("/")
    else :
        return render_template("payment_details.html", ngo=name)


def add_to_needy_database(data) :
    conn = engine.connect()
    command = f"""INSERT INTO n_people(name, age, sex, bg, disability, loc) 
    VALUES ('{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}', '{data[4]}', '{data[5]}')"""
    
    res = conn.execute(command) 

def add_to_ngo_database(data) :
    conn = engine.connect()

    command = f"""INSERT INTO ngos(name, loc, dons_rcv, hlpd) 
    VALUES ('{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}')"""

    res = conn.execute(command) 


if(__name__ == "__main__") :
    app.run(debug=False)
