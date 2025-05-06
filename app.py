from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import config

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Remplace par une clé plus sécurisée

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql7776904:25FjtMPp8T@sql7.freesqldatabase.com:3306/sql7776904'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tariq.haoudi@etu.uae.ac.ma'
app.config['MAIL_PASSWORD'] = 'cjgf gmzu mbef lwlh'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
db = SQLAlchemy(app)

# Modèles de base de données
class Course(db.Model):
    __tablename__ = 'textes_complets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    link = db.Column(db.Text)
    categorie = db.Column(db.String(100))
    image_url = db.Column(db.Text)

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    link = db.Column(db.Text)

# Import de config.py
ADMIN_USERNAME = config.ADMIN_USERNAME
ADMIN_PASSWORD = config.ADMIN_PASSWORD

@app.route('/')
def index():
    categories = db.session.query(Course.categorie).distinct().all()
    courses = Course.query.all()
    offers = Offer.query.all()
    return render_template('index.html', courses=courses, categories=categories, offers=offers)

@app.route('/category/<categorie>')
def category_view(categorie):
    categories = db.session.query(Course.categorie).distinct().all()
    courses = Course.query.filter_by(categorie=categorie).all()
    return render_template('category.html', courses=courses, categorie=categorie, categories=categories)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)

@app.route('/checkout/<int:course_id>', methods=["GET", "POST"])
def checkout(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == "POST":
        full_name = request.form['full_name']
        email = request.form['email']
        msg = Message(subject='🎓 رابط الدورة التعليمية',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"""مرحباً {full_name},

✅ شكراً لدفعك لدورة: {course.title}

🔗 هذا هو رابط الدورة الخاص بك:
{course.link}

نتمنى لك تعلماً موفقاً!
"""
        try:
            mail.send(msg)
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))
    return render_template('checkout.html', course=course)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Identifiants incorrects.')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    courses = Course.query.all()
    offers = Offer.query.all()
    return render_template('admin_panel.html', courses=courses, offers=offers)

@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        new_course = Course(
            title=request.form['title'],
            description=request.form['description'],
            price=request.form['price'],
            link=request.form['link'],
            categorie=request.form['categorie'],
            image_url=request.form['image_url']
        )
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('admin_form.html', action='Ajouter')

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        course.price = request.form['price']
        course.link = request.form['link']
        course.categorie = request.form['categorie']
        course.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('admin_form.html', course=course, action='Modifier')

@app.route('/admin/delete/<int:id>', methods=['POST'])
def admin_delete(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin_panel'))

# CRUD pour offres spéciales
@app.route('/admin/offer/add', methods=['POST'])
def add_offer():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    new_offer = Offer(
        title=request.form['title'],
        description=request.form['description'],
        image_url=request.form['image_url'],
        link=request.form['link']
    )
    db.session.add(new_offer)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/offer/delete/<int:id>', methods=['POST'])
def delete_offer(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    offer = Offer.query.get_or_404(id)
    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/offer/edit/<int:id>', methods=['GET', 'POST'])
def edit_offer(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    offer = Offer.query.get_or_404(id)
    if request.method == 'POST':
        offer.title = request.form['title']
        offer.description = request.form['description']
        offer.image_url = request.form['image_url']
        offer.link = request.form['link']
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('offer_form.html', offer=offer, action='Modifier')

if __name__ == '__main__':
    app.run(debug=True)
