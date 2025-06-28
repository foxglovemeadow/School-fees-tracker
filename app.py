from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-secret-key'

def init_db():
    conn = sqlite3.connect('school_fees.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    student_class TEXT NOT NULL,
                    total_fees REAL NOT NULL,
                    amount_paid REAL NOT NULL DEFAULT 0
                )""")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    conn = sqlite3.connect('school_fees.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()

    c.execute("SELECT SUM(amount_paid) FROM students")
    total_paid = c.fetchone()[0] or 0

    c.execute("SELECT SUM(total_fees - amount_paid) FROM students")
    total_balance = c.fetchone()[0] or 0

    c.execute("SELECT SUM(total_fees) FROM students")
    total_fees = c.fetchone()[0] or 0

    conn.close()
    return render_template('dashboard.html', students=students,
                           total_paid=total_paid,
                           total_balance=total_balance,
                           total_fees=total_fees)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    student_class = request.form['class']
    total_fees = float(request.form['total_fees'])
    amount_paid = float(request.form['amount_paid'])

    conn = sqlite3.connect('school_fees.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, student_class, total_fees, amount_paid) VALUES (?, ?, ?, ?)",
              (name, student_class, total_fees, amount_paid))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/update/<int:id>', methods=['POST'])
def update_payment(id):
    new_payment = float(request.form['payment'])
    conn = sqlite3.connect('school_fees.db')
    c = conn.cursor()
    c.execute("UPDATE students SET amount_paid = amount_paid + ? WHERE id = ?", (new_payment, id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.before_request
def require_login():
    protected = ['dashboard', 'add_student', 'update_payment']
    if request.endpoint in protected and 'user' not in session:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
