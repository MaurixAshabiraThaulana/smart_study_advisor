from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'


# ===== DATABASE =====
def get_db():
    return sqlite3.connect('database.db')


# ===== SISTEM CERDAS =====
def rekomendasi_belajar(gaya, waktu, stres, nilai):
    hasil = []

    if stres == 'tinggi':
        hasil.append('Gunakan teknik Pomodoro')

    if gaya == 'visual':
        hasil.append('Belajar dengan video & mind map')
    elif gaya == 'audio':
        hasil.append('Belajar dengan podcast')
    elif gaya == 'praktik':
        hasil.append('Perbanyak latihan soal')

    if waktu == 'sedikit' and nilai < 70:
        hasil.append('Fokus materi inti')
    if nilai >= 85:
        hasil.append('Pertahankan metode belajar')

    return hasil


# ===== REGISTER =====
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (request.form['username'],
             generate_password_hash(request.form['password']))
        )
        db.commit()
        db.close()
        return redirect('/login')
    return render_template('register.html')


# ===== LOGIN =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username=?',
            (request.form['username'],)
        ).fetchone()
        db.close()

        if user and check_password_hash(user[2], request.form['password']):
            session['user_id'] = user[0]
            return redirect('/')
    return render_template('login.html')


# ===== DASHBOARD =====
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect('/login')

    rekomendasi = None
    if request.method == 'POST':
        rekomendasi = rekomendasi_belajar(
            request.form['gaya'],
            request.form['waktu'],
            request.form['stres'],
            int(request.form['nilai'])
        )

        db = get_db()
        db.execute(
            'INSERT INTO history (user_id, rekomendasi, created_at) VALUES (?, ?, ?)',
            (session['user_id'], ', '.join(rekomendasi), datetime.now())
        )
        db.commit()
        db.close()

    return render_template('index.html', rekomendasi=rekomendasi)


# ===== RIWAYAT =====
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    data = db.execute(
        'SELECT rekomendasi, created_at FROM history WHERE user_id=? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    db.close()

    return render_template('history.html', data=data)


# ===== LOGOUT =====
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
