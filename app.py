from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import config
from math import ceil
import urllib.parse  # Pour encoder le mot de passe MySQL

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Encodage du mot de passe SQL qui contient des caractères spéciaux
password = urllib.parse.quote_plus('$5KUMKWeD4*h7$d')

# Configuration base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://freedb_freedb_sql7776904:{password}@sql.freedb.tech/freedb_sql7776904'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration Flask-Mail (⚠️ ne jamais exposer les vrais identifiants Gmail en public)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tariq.haoudi@etu.uae.ac.ma'
app.config['MAIL_PASSWORD'] = 'ton_mot_de_passe_application'  # Utilise un mot de passe d’application Gmail
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
    page = request.args.get('page', 1, type=int)
    per_page = 8
    courses = Course.query.paginate(page=page, per_page=per_page, error_out=False)
    offers = Offer.query.all()
    return render_template('index.html', courses=courses, categories=categories, offers=offers)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    categories = db.session.query(Course.categorie).distinct().all()
    page = request.args.get('page', 1, type=int)
    per_page = 6
    courses = Course.query.filter(Course.title.ilike(f'%{query}%')).paginate(page=page, per_page=per_page, error_out=False)
    offers = Offer.query.all()
    return render_template('search.html', courses=courses, categories=categories, offers=offers, query=query)

@app.route('/category/<categorie>')
def category_view(categorie):
    categories = db.session.query(Course.categorie).distinct().all()
    page = request.args.get('page', 1, type=int)
    per_page = 6
    search = request.args.get('search', '').strip()

    query = Course.query.filter_by(categorie=categorie)
    offers = Offer.query.all()

    if search:
        query = query.filter(Course.title.ilike(f'%{search}%'))

    courses = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('category.html', 
                           courses=courses, 
                           categorie=categorie, 
                           categories=categories,
                            offers=offers,
                           search=search)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    categories = db.session.query(Course.categorie).distinct().all()
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html',categories=categories, course=course)

@app.route('/checkout/<int:course_id>', methods=["GET", "POST"])
def checkout(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == "POST":
        full_name = request.form['full_name']
        email = request.form['email']
        stage = request.form.get('stage')  # نضيف هذا السطر للتحقق من المرحلة

        if stage == "before_payment":
            # هنا يمكن حفظ الاسم والإيميل في قاعدة البيانات أو تسجيل الدخول مثلاً
            print(f"✅ البيانات قبل الدفع: {full_name} - {email}")
            return jsonify(success=True)

        # هنا نرسل الرابط بعد الدفع فقط
        msg = Message(subject='🎓 رابط الدورة التعليمية', sender=app.config['MAIL_USERNAME'], recipients=[email])
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

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/jdid')
def jdid():
    return render_template('jdid.html')
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

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
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Définissez le nombre d'éléments par page
    courses = Course.query.paginate(page=page, per_page=per_page, error_out=False)
    offers = Offer.query.paginate(page=page, per_page=per_page, error_out=False)
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
@app.route('/admin/offer/add', methods=['GET', 'POST'])
def add_offer():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        new_offer = Offer(
            title=request.form['title'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            link=request.form['link']
        )
        db.session.add(new_offer)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('offer_form.html', action='Ajouter')

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

@app.route('/admin/offer/delete/<int:id>', methods=['POST'])
def delete_offer(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    offer = Offer.query.get_or_404(id)
    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('admin_panel'))



# إضافة نموذج الدفع:
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), nullable=True)

# نقطة نهاية لإنشاء سجل الدفع عند بداية العملية
@app.route('/init-payment/<int:course_id>', methods=['POST'])
def init_payment(course_id):
    full_name = request.form['full_name']
    email = request.form['email']

    payment = Payment(
        course_id=course_id,
        full_name=full_name,
        email=email,
        method='paypal',
        transaction_id=None
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({'payment_id': payment.id})

# نقطة نهاية لتأكيد الدفع بعد إتمامه
@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    payment_id = request.form['payment_id']
    transaction_id = request.form['transaction_id']

    payment = Payment.query.get(payment_id)
    if payment:
        payment.transaction_id = transaction_id
        db.session.commit()

        # نرسل الإيميل
        course = Course.query.get(payment.course_id)
        msg = Message(subject='🎓 رابط الدورة التعليمية',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[payment.email])
        msg.body = f"""مرحباً {payment.full_name},

✅ شكراً لدفعك لدورة: {course.title}

🔗 هذا هو رابط الدورة الخاص بك:
{course.link}

نتمنى لك تعلماً موفقاً!
"""
        try:
            mail.send(msg)
        except Exception as e:
            print("❌ فشل في إرسال الإيميل:", e)

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)