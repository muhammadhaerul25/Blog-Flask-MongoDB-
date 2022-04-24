from flask import Flask, render_template, url_for, request, redirect, g, current_app, request, session
from flask_paginate import Pagination
from flask_session import Session
from pymongo import MongoClient
from bson import ObjectId
import bcrypt


try:
    #connect to mongodb using cluster in Atlas
    client = MongoClient(
        "mongodb://muhammadhaerul:haerul25@cluster0-shard-00-00.3zwlb.mongodb.net:27017,cluster0-shard-00-01.3zwlb.mongodb.net:27017,cluster0-shard-00-02.3zwlb.mongodb.net:27017/blogDB?ssl=true&replicaSet=atlas-17dvo6-shard-0&authSource=admin&retryWrites=true&w=majority")
    db = client.blogDB
    client.server_info() #trigger exception if can't connect to db
except Exception as e:
    print("Error - App can't connect to db:", e)


#start the app
app = Flask(__name__)
#######################################################
#check configuration section for more details
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

#Blog
#######################################################
@app.route("/")
@app.route("/home")
@app.route("/home/<index>")
def home(index='0'):
    #get data from DB
    trending = db.news.find({"tag": "Trending"}).sort("date", -1).limit(1)
    recommended = db.news.find({"tag": "Recommended"}).sort("date", -1).limit(2)
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, { "$sort": { "_id": 1 }}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, { "$sort": { "_id": -1 }}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, { "$sort": { "_id": 1 }}])
    popular = db.news.find({}).sort("read", -1).limit(5)
    tags2 = db.news.aggregate([{"$group": {"_id": "$tag", "myCount": {"$sum": 1}}},
                               {"$sort": {"myCount": -1}}, {"$limit": 10}])
    dates2 = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    categories2 = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    news = db.news.find({}).sort("date", -1)

    #pagination
    tNews = 0
    for n in news:
        tNews = tNews + 1
    offset = 0 + int(index)
    limit = 5
    news = db.news
    starting_id = news.find().sort('_id', -1)
    last_id = starting_id[offset]['_id']
    news = news.find({'_id': {'$lte': last_id}}).sort('_id', -1).limit(limit)
    prev = offset - limit
    if (prev < 0):
        prev = 0
    next = offset + limit
    n = next
    if (next >= tNews):
        n = tNews
        next = tNews - 1
    prev_url = '/home/' + str(prev)
    next_url = '/home/' + str(next)

    return render_template("home.html", news=news, trn=trending, rcmnd=recommended, pop=popular, ctgr=categories,
                           ctgr2=categories2, dt=dates, dt2=dates2, tg=tags, tg2=tags2,
                           prev=prev_url, next=next_url, n=n, t=tNews)


@app.route("/category/<category>")
@app.route("/category/<category>/<index>")
def category(category, index='0'):
    #get data
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])
    news = db.news.find({"category": category}).sort("date", -1)

    #pagination
    tNews = 0
    for n in news:
        tNews = tNews + 1
    offset = 0 + int(index)
    limit = 5
    news = db.news
    starting_id = news.find().sort('_id', -1)
    last_id = starting_id[offset]['_id']
    news = news.find({'_id': {'$lte': last_id}, "category": category}).sort('_id', -1).limit(limit)
    prev = offset - limit
    if (prev < 0):
        prev = 0
    next = offset + limit
    n = next
    if (next >= tNews):
        n = tNews
        next = tNews - 1
    prev_url = '/category/' + category + "/" + str(prev)
    next_url = '/category/' + category + "/" + str(next)

    return render_template("category.html", news=news, ctgr=categories, dt=dates, tg=tags, str=category,
                           prev=prev_url, next=next_url, n=n, t=tNews)


@app.route("/date/<date>")
@app.route("/date/<date>/<index>")
def date(date, index='0'):
    #getdata
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])
    news = db.news.find({"date": date}).sort("date", -1)

    #pagination
    tNews = 0
    for n in news:
        tNews = tNews + 1
    offset = 0 + int(index)
    limit = 5
    news = db.news
    starting_id = news.find().sort('_id', -1)
    last_id = starting_id[offset]['_id']
    news = news.find({'_id': {'$lte': last_id}, "date": date}).sort('_id', -1).limit(limit)
    prev = offset - limit
    if (prev < 0):
        prev = 0
    next = offset + limit
    n = next
    if (next >= tNews):
        n = tNews
        next = tNews - 1
    prev_url = '/date/' + date + "/" + str(prev)
    next_url = '/date/' + date + "/" + str(next)

    return render_template("date.html", news=news, ctgr=categories, dt=dates, tg=tags, str=date,
                           prev=prev_url, next=next_url, n=n, t=tNews)


@app.route("/tag/<tag>")
@app.route("/tag/<tag>/<index>")
def tag(tag, index='0'):
    #get data
    news = db.news.find({"tag": tag}).sort("date", -1).limit(5)
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])
    news = db.news.find({"tag": tag}).sort("date", -1)

    #pagination
    tNews = 0
    for n in news:
        tNews = tNews + 1
    offset = 0 + int(index)
    limit = 5
    news = db.news
    starting_id = news.find().sort('_id', -1)
    last_id = starting_id[offset]['_id']
    news = news.find({'_id': {'$lte': last_id}, "tag": tag}).sort('_id', -1).limit(limit)
    prev = offset - limit
    if (prev < 0):
        prev = 0
    next = offset + limit
    n = next
    if (next >= tNews):
        n = tNews
        next = tNews - 1
    prev_url = '/tag/' + tag + "/" + str(prev)
    next_url = '/tag/' + tag + "/" + str(next)

    return render_template("tag.html", news=news, ctgr=categories, dt=dates, tg=tags, str=tag,
                           prev=prev_url, next=next_url, n=n, t=tNews)


@app.route("/news/<id>")
def news(id):
    #get data
    news = db.news.find({"_id": ObjectId(id)})
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])
    data = db.news.find_one({"_id": ObjectId(id)})
    read = data["read"] + 1
    update = {"_id": ObjectId(id)}
    value = {"$set": {"read": read}}
    db.news.update_one(update, value)

    return render_template("news.html", news=news, ctgr=categories, dt=dates, tg=tags, rd=read)


@app.route("/contact")
def contact():
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])

    return render_template("contact.html", ctgr=categories, dt=dates, tg=tags)

@app.route("/about")
def about():
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])

    return render_template("about.html", ctgr=categories, dt=dates, tg=tags)



@app.route("/login", methods=["POST", "GET"])
def login():
    #get data from DB
    categories = db.news.aggregate([{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}])
    dates = db.news.aggregate([{"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}])
    tags = db.news.aggregate([{"$group": {"_id": "$tag"}}, {"$sort": {"_id": 1}}])

    #check session
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("admin"))

    #get data from form and match in DB
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = db.user.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for("admin"))
            else:
                if "email" in session:
                    return redirect(url_for("admin"))
                message = 'Wrong password'
                return render_template('login.html', ctgr=categories, dt=dates, tg=tags, message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', ctgr=categories, dt=dates, tg=tags, message=message)

    return render_template("login.html", ctgr=categories, dt=dates, tg=tags, message=message)



#Admin
#######################################################
@app.route("/admin")
def admin():
    #check session
    if "email" in session:
        email = session.get("email")
    else:
        return redirect(url_for("login"))

    return render_template("admin.html", email=email)


@app.route("/user", methods=['POST', 'GET'])
def user():
    message = ''
    #check session
    if "email" in session:
        pass
    else:
        return redirect(url_for("login"))

    #get data from form and add to DB
    if request.method == "POST":
        user = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        passwordConfir = request.form.get("passwordConfir")
        user_found = db.user.find_one({"name": user})
        email_found = db.user.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('user.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('user.html', message=message)
        if password != passwordConfir:
            message = 'Passwords should match!'
            return render_template('user.html', message=message)
        else:
            hashed = bcrypt.hashpw(passwordConfir.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            db.user.insert_one(user_input)
            user_data = db.user.find_one({"email": email})
            new_email = user_data['email']
            message = "User created successfully"

            return render_template('user.html', email=new_email, message=message)

    return render_template('user.html')


@app.route("/content")
def content():
    #check session
    if "email" in session:
        email = session.get("email")
    else:
        return redirect(url_for("login"))

    #get total news and total read
    news = db.news.find({}).sort("date", -1)
    tNews = 0
    for n in news:
         tNews = tNews + 1
    news = db.news.find({}).sort("date", -1)
    tRead = 0
    for n in news:
         tRead = tRead + n["read"]
    news = db.news.find({}).sort("date", -1)

    return render_template("content.html", news=news, tRead=tRead, tNews=tNews)


@app.route("/postNews", methods=['POST', 'GET'])
def postNews():
    message = ''
    #check session
    if "email" in session:
        pass
    else:
        return redirect(url_for("login"))

    #get data from form and add to DB
    if request.method == "POST":
        title = request.form.get("title")
        title_idn = request.form.get("title_idn")
        author = request.form.get("author")
        category = request.form.get("category")
        date = request.form.get("date")
        tag = request.form.get("tag")
        content = request.form.get("content")
        content_idn = request.form.get("content_idn")
        read = 0
        news_input = {'title': title, 'title_idn': title_idn, 'author': author, 'category': category,
                      "date": date, "tag": tag, "content": content, "content_idn": content_idn, "read": 0}
        db.news.insert_one(news_input)
        message = "News posted successfully"
        news = db.news.find({}).sort("date", -1)
        tNews = 0
        for n in news:
            tNews = tNews + 1
        news = db.news.find({}).sort("date", -1)
        tRead = 0
        for n in news:
            tRead = tRead + n["read"]
        news = db.news.find({}).sort("date", -1)

        return render_template("content.html", news=news, message=message, tRead=tRead, tNews=tNews)

    return render_template("postNews.html")


@app.route("/editNews/<id>", methods=['POST', 'GET'])
def editNews(id):
    message = ''
    #check session
    if "email" in session:
        pass
    else:
        return redirect(url_for("login"))

    news = db.news.find_one({"_id": ObjectId(id)})

    #get data from DB and put in form to edit content
    if request.method == "POST":
        title = request.form.get("title")
        title_idn = request.form.get("title_idn")
        author = request.form.get("author")
        category = request.form.get("category")
        date = request.form.get("date")
        tag = request.form.get("tag")
        content = request.form.get("content")
        content_idn = request.form.get("content_idn")
        news_old = {"_id": ObjectId(id)}
        news_update = { "$set": {'title': title, 'title_idn': title_idn, 'author': author, 'category': category,
                                 "date": date, "tag": tag, "content": content, "content_idn": content_idn}}
        db.news.update_one(news_old, news_update)
        message = "News edited successfully"
        news = db.news.find({}).sort("date", -1)
        tNews = 0
        for n in news:
            tNews = tNews + 1
        news = db.news.find({}).sort("date", -1)
        tRead = 0
        for n in news:
            tRead = tRead + n["read"]
        news = db.news.find({}).sort("date", -1)

        return render_template("content.html", news=news, message=message, tRead=tRead, tNews=tNews)

    return render_template("editNews.html", news=news)


@app.route("/deleteNews/<id>", methods=['POST', 'GET'])
def deleteNews(id):
    message = ''
    #check session
    if "email" in session:
        pass
    else:
        return redirect(url_for("login"))

    #delete spesific data in DB
    news = {"_id": ObjectId(id)}
    db.news.delete_one(news)
    message = "News deleted successfully"
    news = db.news.find({}).sort("date", -1)
    tNews = 0
    for n in news:
        tNews = tNews + 1
    news = db.news.find({}).sort("date", -1)
    tRead = 0
    for n in news:
        tRead = tRead + n["read"]
    news = db.news.find({}).sort("date", -1)

    return render_template("content.html", news=news, message=message, tRead=tRead, tNews=tNews)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    #check session
    if "email" in session:
        session.pop("email", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


#######################################################
if __name__ == "__main__":
    app.run(debug=True)