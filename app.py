from flask import Flask, request, redirect, flash, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin, login_required
import re
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

#---------------- Initializing Flask Instance
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///libdb8.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config['SECRET_KEY'] = 'Mera_Bharat_Mahan'
app.secret_key = 'Mera_Bharat_Mahan'
db = SQLAlchemy()
migrate = Migrate(app, db)
login_manager = LoginManager(app)

    
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    u_name = db.Column(db.String(20), nullable = False)
    u_uname = db.Column(db.String(20), nullable = False, unique = True)
    u_email = db.Column(db.String(40), unique = True)
    u_password = db.Column(db.String(20), nullable = False)
    is_admin = db.Column(db.Boolean, default=False)
    accessed = db.relationship('Book', secondary="access", backref=db.backref('users',lazy=True))
    requested = db.relationship('Book', secondary="requests", backref=db.backref('requested_by_users',lazy=True))
    requestsss = db.relationship("Requests",back_populates="requesTer",cascade="all, delete",lazy=True,overlaps="requested,requested_by_users")
    
class Book(db.Model):
    __tablename__ ='book'
    b_id =  db.Column(db.Integer, primary_key = True)
    b_title = db.Column(db.String(20), nullable = False)
    b_author = db.Column(db.String(20), nullable = False)
    b_content = db.Column(db.String(500), nullable = False)
    sec_id = db.Column(db.Integer, db.ForeignKey('section.s_id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('book', lazy=True))
    requestss = db.relationship("Requests",back_populates="requestedBook",cascade="all, delete",lazy=True,overlaps="requested,requested_by_users")
    # acc = db.relationship('Access', backref=db.backref('book', lazy=True))
    
class Section(db.Model):
    __tablename__ ='section'
    s_id =  db.Column(db.Integer, primary_key = True)
    s_title = db.Column(db.String(20), nullable = False)
    s_content = db.Column(db.String(100), nullable = False)
    s_created_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

class Access(db.Model):
    __tablename__ ='access'
    a_id =  db.Column(db.Integer, primary_key = True)
    book_id =  db.Column(db.Integer,db.ForeignKey("book.b_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    b_issued_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    b_return_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
     
   
class Requests(db.Model):
    __tablename__ ='requests'
    r_id =  db.Column(db.Integer, primary_key = True)
    book_id =  db.Column(db.Integer,db.ForeignKey("book.b_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    duration = db.Column(db.String(30))
    requesTer = db.relationship("User",back_populates="requestsss",overlaps="requested,requested_by_users")
    requestedBook = db.relationship("Book",back_populates="requestss",overlaps="requested,requested_by_users")
    
# #----------------- Creating DataBase
db.init_app(app)
# app.app_context().push()
# db.create_all()

#------------------ login validator

def unameval(a):
    if len(a) < 6 or len(a) > 20:
        return "Length Error."
    if not a.isalnum():
        return "User Name should be alfanumeric."
    else:
        return a
    
def passwordval(pas):
    if len(pas)<6 or len(pas)>12:
        return "Password should be between 6 to 12 characters."
    else:
        return pas
    
def emailval(email):
    pattern = r'[a-zA-Z0-9]+@[a-zA-Z]+\.[a-z]{2,}$'
    if re.match(pattern, email):
        return True
    return False

          
class Config:
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()
@scheduler.task('interval', id='do_job_1', seconds=10)
def job1():
    with app.app_context():
        all_access = Access.query.all()
        for access in all_access:
            if access.b_return_date < datetime.now():
                db.session.delete(access)
                db.session.commit()
scheduler.init_app(app)
scheduler.start()

app.config.from_object(Config())     

#--------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




#----------------- Routing for pages
@app.route('/')
def home():
    return render_template("home_nav.html")

#------------------ Admin login
@app.route('/admin_login', methods = ['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        admin_username = request.form['username']
        admin_password = request.form['password']
        if unameval(admin_username) != admin_username:
            flash('Length of username should be between 6 to 20')
            return render_template('admin_login.html', admin_username = admin_username)
        adusername = User.query.filter_by(u_uname = admin_username).first()
        print(adusername,admin_username)
        if adusername:
            admin_uname = User.query.filter_by(u_uname = admin_username).first()
            pwd = admin_uname.u_password
            if pwd  == admin_password and admin_uname.is_admin:
                flash("Logged in successfully! Welcome to your dashboard", "success")
                login_user(admin_uname)
                return redirect(url_for("admin", admin_id = admin_uname.id))
            if passwordval(admin_password) != admin_password:
                flash("Length of password should be at least 8 and at max 20 characters", "pwd_error")
                return render_template("admin_login.html", admin_uname=admin_username)
            flash("Wrong password!", "error")
            return render_template("admin_login.html", admin_uname=admin_username , password = admin_password)


#------------------ User login
@app.route('/user_login', methods = ['GET','POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    if request.method == 'POST':
        user_username = request.form['username']
        user_password = request.form['password']
        if unameval(user_username) != user_username:
            flash('Length of username should be between 6 to 20')
            return render_template('admn_login.html', user_username = user_username)
        uusername = User.query.filter_by(u_uname = user_username).first()
        if uusername:
            user_uname = User.query.filter_by(u_uname = user_username).first()
            pwd = user_uname.u_password
            if pwd  == user_password:
                flash("Logged in successfully! Welcome to your dashboard", "success")
                login_user(user_uname)
                return redirect(url_for("user", user_id = uusername.id))
            if passwordval(user_password) != user_password:
                flash("Length of password should be at least 8 and at max 20 characters", "pwd_error")
                return render_template("user_login.html", user_username=user_username)
            flash("Wrong password!", "error")
            return render_template("user_login.html", user_username=user_username , user_password = user_password)

#---------- User Registration
@app.route('/user_registration', methods = ['GET','POST'])
def user_register():
    if request.method == 'GET':
        return render_template('user_reg.html')
    if request.method == 'POST':
        user_name = request.form["name"]
        
        user_uname = request.form["username"]
        if unameval(user_uname) != user_uname:
            flash('Length of username should be between 6 to 20')
            return render_template('user_reg.html', user_name = user_name)
        
        user_email = request.form["user_email"]
        if not emailval(user_email):
            flash('Enter a valid Email', 'email_error')
            return render_template('user_reg.html', user_name = user_name , user_uname = user_uname)
                
        admin_password = request.form["password"]
        if passwordval(admin_password) != admin_password:
            flash("Length of password should be at least 6 and at max 20 characters", "pwd_error")
            return render_template('user_reg.html', user_name = user_name, user_email= user_email, user_uname=user_uname)
        uusername = User.query.filter_by(u_uname = user_uname).all()
        if len(uusername) != 0:
            flash("Username already exists! Try some other username.","usrname_exist")
            return render_template('user_reg.html',user_name = user_name, user_email= user_email, user_uname=user_uname)
        user_data = User(u_name = user_name, u_email= user_email, u_uname=user_uname, u_password = admin_password)
        db.session.add(user_data)
        db.session.commit()
        flash("Registered as User successfully", "success")
        return redirect("/user_login")
    
    
#---------------- Admin Logout
@app.route('/admin_logout', methods = ["GET","POST"])
@login_required
def admin_logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect("/admin_login")


#---------------- User Logout
@app.route('/user_logout', methods = ["GET","POST"])
@login_required
def user_logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect("/user_login")

#------------------ Admin DashBoard
@app.route('/admin', methods = ["GET","POST"])
@login_required
def admin():
    if request.method == 'GET':
        sec_data = Section.query.all()
        return render_template('admin_dash.html',sections = sec_data)

#------------------ Add Section
@app.route('/admin/add_sec', methods = ['GET','POST'])
@login_required
def add_sec():
    if request.method == 'GET':
        return render_template("add_sect.html")
    if request.method == 'POST':
        sec_title = request.form["title"]
        sec_des = request.form["description"]
        print(sec_title, sec_des)
        sec_data = Section(s_title = sec_title, s_content = sec_des)
        db.session.add(sec_data)
        db.session.commit()
        flash("Section created successfully!","sec_success")
        return redirect(url_for("admin"))
        
#------------------ View the Section
@app.route('/admin/<s_id>/view_sect', methods = ["GET","POST"])
@login_required
def view_sect(s_id):
    if request.method == 'GET':
        show_book = Book.query.filter_by(sec_id = s_id).all()
        return render_template("book_page.html",s_books = show_book, s_id = s_id)


#------------------ Add Book to a Section
@app.route('/admin/<s_id>/add_book', methods=["GET", "POST"])
@login_required
def add_book(s_id):
    if request.method == 'GET':
        section = Section.query.filter_by(s_id = s_id).first()
        if section:
           return render_template("add_book.html", section = section)
    
    if request.method == "POST":
        # Assuming you have a form with input fields like "title", "author", "content"
        book_title = request.form["title"]
        book_author = request.form["author"]
        book_content = request.form["content"]
        book_data = Book(b_title=book_title, b_author=book_author, b_content=book_content, sec_id=s_id)
        db.session.add(book_data)
        db.session.commit()
        flash("Book added successfully!", "success")
        return redirect(url_for("view_sect" , s_id = s_id))

#------------------ Delete Section

@app.route('/admin/<s_id>/delete_sect' , methods = ["GET","POST"])
@login_required
def delete_sect(s_id):
    sect = Section.query.filter_by(s_id = s_id).first()
    show_book = Book.query.filter_by(sec_id = s_id).all()
    if request.method == 'GET':
        db.session.delete(sect)
        for book in show_book:
            db.session.delete(book)
        db.session.commit()
        flash("Section deleted successfully!","success")
        return redirect('/admin')
    return redirect("/admin_login")


#------------------ Delete Book
@app.route('/admin/<s_id>/<b_id>/delete_book' , methods = ["GET","POST"])
@login_required
def delete_book(s_id,b_id):
    book = Book.query.filter_by(sec_id = s_id, b_id = b_id).first()
    print(book)
    if request.method == 'GET':
        db.session.delete(book)
        db.session.commit()
        flash("Book deleted successfully!","success")
        return redirect(url_for("view_sect" , s_id = s_id))
    return redirect("/admin_login")

#------------------ User DashBoard
@app.route('/user/<user_id>', methods = ["GET","POST"])
@login_required
def user(user_id):
    if request.method == 'GET':
        books_list = Book.query.all()
        print(books_list)
        return render_template('user_dash.html',books_list = books_list, user_id = user_id)

#------------------ Book_Request
@app.route('/user/<int:u_id>/<int:b_id>/request_book', methods=['POST', 'GET'])
@login_required
def request_book(u_id,b_id):
    user = User.query.filter_by(id=u_id).first()
    book = Book.query.filter_by(b_id=b_id).first()
    if request.method == 'POST':
        duration = request.form["duration"]
        new_request = Requests(book_id=b_id, user_id=u_id, duration = duration)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for("user",user_id = current_user.id))
    
    return render_template('user_request.html', book = book, user = user)

#------------------- Admin Grant Access --------------------------------
@app.route('/grant/<int:request_id>')
@login_required
def grant_access(request_id):
    req = Requests.query.get(request_id)
    user = User.query.filter_by(id=req.user_id).first()
    book = Book.query.filter_by(b_id=req.book_id).first()
    s_time  = datetime.now()
    # e_time  = None
    if req.duration == "2 days":
        e_time = s_time + timedelta(days=2)
    if req.duration == "3 days":
        e_time = s_time + timedelta(days=3)
    if req.duration == "4 days":
        e_time = s_time + timedelta(days=4)
        
    new_access = Access(user_id = req.user_id , book_id = req.book_id, b_issued_date = s_time, b_return_date = e_time)
    db.session.add(new_access)
    db.session.delete(req)
    db.session.commit()
    return redirect(url_for("requests"))

@app.route('/reject/<int:request_id>')
@login_required
def reject_request(request_id):
    req = Requests.query.get(request_id)
    user = User.query.filter_by(id=req.user_id).first()
    book = Book.query.filter_by(b_id=req.book_id).first()
    db.session.delete(req)
    db.session.commit()
    return redirect(url_for("requests"))



@app.route("/requests")
@login_required
def requests():
    request = Requests.query.all()
    return render_template("admin_req.html", requests = request)




#---------------- Search Bar ------------------------
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        books = Book.query.filter(Book.b_title.ilike(f'%{search_term}%')).all()
        sections = Section.query.filter(Section.s_title.ilike(f'%{search_term}%')).all()
        return render_template('search_results.html', books=books, sections=sections)
    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
    
    
    @app.teardown_appcontext
    def teardown_appcontext(exception=None):
        scheduler.shutdown()