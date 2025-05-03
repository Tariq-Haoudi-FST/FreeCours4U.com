from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# إعدادات الإيميل (غيّر المعلومات الخاصة بك)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# الدورات
courses = [
    {"id": 1, "title": "دورة تعلم بايثون", "description": "من المبتدئ إلى المتقدم", "price": 10, "link": "https://drive.google.com/xyz"},
    {"id": 2, "title": "دورة تصميم واجهات", "description": "UI/UX", "price": 15, "link": "https://drive.google.com/abc"},
]

@app.route('/')
def index():
    return render_template('index.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = next((c for c in courses if c["id"] == course_id), None)
    return render_template('course_detail.html', course=course)

@app.route('/checkout/<int:course_id>', methods=["GET", "POST"])
def checkout(course_id):
    course = next((c for c in courses if c["id"] == course_id), None)

    if request.method == "POST":
        full_name = request.form['full_name']
        email = request.form['email']

        msg = Message('رابط الدورة التعليمية',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"مرحبًا {full_name},\n\nتم الدفع بنجاح! إليك رابط الدورة:\n{course['link']}"

        try:
            mail.send(msg)
            return render_template('checkout.html', course=course, success=True)
        except Exception as e:
            return render_template('checkout.html', course=course, success=False, error=str(e))

    return render_template('checkout.html', course=course)

if __name__ == '__main__':
    app.run(debug=True)
