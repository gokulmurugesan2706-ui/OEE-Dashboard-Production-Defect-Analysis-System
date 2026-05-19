from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('oee.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planned_time REAL,
            operating_time REAL,
            ideal_cycle_time REAL,
            total_count INTEGER,
            good_count INTEGER
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    planned_time = float(request.form['planned_time'])
    operating_time = float(request.form['operating_time'])
    ideal_cycle_time = float(request.form['ideal_cycle_time'])
    total_count = int(request.form['total_count'])
    good_count = int(request.form['good_count'])

    availability = operating_time / planned_time if planned_time > 0 else 0
    performance = (ideal_cycle_time * total_count) / operating_time if operating_time > 0 else 0
    quality = good_count / total_count if total_count > 0 else 0
    oee = availability * performance * quality

    conn = sqlite3.connect('oee.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO production
        (planned_time, operating_time, ideal_cycle_time, total_count, good_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        planned_time,
        operating_time,
        ideal_cycle_time,
        total_count,
        good_count
    ))
    conn.commit()
    conn.close()

    return render_template(
        'result.html',
        availability=round(availability * 100, 2),
        performance=round(performance * 100, 2),
        quality=round(quality * 100, 2),
        oee=round(oee * 100, 2)
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)