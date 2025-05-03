# --- app.py ---
from flask import Flask, render_template

app = Flask(__name__)

# صفحة البداية
@app.route('/')
def index():
    courses = [
        {'id': 1, 'title': 'دورة بايثون', 'description': 'تعلم أساسيات بايثون من الصفر', 'price': '20$'},
        {'id': 2, 'title': 'دورة HTML/CSS', 'description': 'بناء صفحات الويب بواجهة احترافية', 'price': '15$'},
    ]
    return render_template('index.html', courses=courses)

# صفحة تفاصيل الدورة
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    courses = [
        {'id': 1, 'title': 'دورة بايثون', 'description': 'تعلم أساسيات بايثون من الصفر', 'price': '20$'},
        {'id': 2, 'title': 'دورة HTML/CSS', 'description': 'بناء صفحات الويب بواجهة احترافية', 'price': '15$'},
    ]
    course = next((c for c in courses if c['id'] == course_id), None)
    return render_template('course_detail.html', course=course)

# صفحة الدفع
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)