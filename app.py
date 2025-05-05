from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql7776904:25FjtMPp8T@sql7.freesqldatabase.com:3306/sql7776904'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج الجدول الجديد
class Course(db.Model):
    __tablename__ = 'textes_complets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    link = db.Column(db.Text)
    categorie = db.Column(db.String(100))
    image_url = db.Column(db.Text)

# إعدادات البريد
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tariq.haoudi@etu.uae.ac.ma'
app.config['MAIL_PASSWORD'] = 'cjgf gmzu mbef lwlh'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# الصفحة الرئيسية تعرض كل الدورات وجميع التصنيفات في القائمة
@app.route('/')
def index():
    categories = db.session.query(Course.categorie).distinct().all()
    courses = Course.query.all()
    return render_template('index.html', courses=courses, categories=categories)

# صفحة لعرض الدورات حسب التصنيف
@app.route('/category/<categorie>')
def category_view(categorie):
    categories = db.session.query(Course.categorie).distinct().all()
    courses = Course.query.filter_by(categorie=categorie).all()
    return render_template('category.html', courses=courses, categorie=categorie, categories=categories)

# صفحة تفاصيل الدورة
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)

# صفحة الدفع
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

if __name__ == '__main__':
    app.run(debug=True)
