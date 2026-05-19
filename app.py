from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


# Create database and table
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
            good_count INTEGER,
            scratch_defects INTEGER,
            crack_defects INTEGER,
            dimension_defects INTEGER,
            porosity_defects INTEGER
        )
    ''')

    conn.commit()
    conn.close()


# Home page
@app.route('/')
def index():
    return render_template('index.html')


# Calculate OEE and Defect Analysis
@app.route('/calculate', methods=['POST'])
def calculate():
    # OEE inputs
    planned_time = float(request.form['planned_time'])
    operating_time = float(request.form['operating_time'])
    ideal_cycle_time = float(request.form['ideal_cycle_time'])
    total_count = int(request.form['total_count'])
    good_count = int(request.form['good_count'])

    # Defect inputs
    scratch_defects = int(request.form['scratch_defects'])
    crack_defects = int(request.form['crack_defects'])
    dimension_defects = int(request.form['dimension_defects'])
    porosity_defects = int(request.form['porosity_defects'])

    # ----------------------------
    # OEE CALCULATION
    # ----------------------------
    availability = operating_time / planned_time if planned_time > 0 else 0
    performance = (ideal_cycle_time * total_count) / operating_time if operating_time > 0 else 0
    quality = good_count / total_count if total_count > 0 else 0

    oee = availability * performance * quality

    # ----------------------------
    # DEFECT ANALYSIS
    # ----------------------------
    defects = {
        "Scratch Defects": scratch_defects,
        "Crack Defects": crack_defects,
        "Dimension Errors": dimension_defects,
        "Porosity Defects": porosity_defects
    }

    total_defects = sum(defects.values())

    if total_defects > 0:
        top_defect = max(defects, key=defects.get)
        top_defect_percentage = round(
            defects[top_defect] / total_defects * 100, 2
        )
    else:
        top_defect = "No Defects"
        top_defect_percentage = 0

    # ----------------------------
    # SAVE TO DATABASE
    # ----------------------------
    conn = sqlite3.connect('oee.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO production (
            planned_time,
            operating_time,
            ideal_cycle_time,
            total_count,
            good_count,
            scratch_defects,
            crack_defects,
            dimension_defects,
            porosity_defects
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        planned_time,
        operating_time,
        ideal_cycle_time,
        total_count,
        good_count,
        scratch_defects,
        crack_defects,
        dimension_defects,
        porosity_defects
    ))

    conn.commit()
    conn.close()

    # ----------------------------
    # SHOW RESULT
    # ----------------------------
    return render_template(
        'result.html',
        availability=round(availability * 100, 2),
        performance=round(performance * 100, 2),
        quality=round(quality * 100, 2),
        oee=round(oee * 100, 2),
        total_defects=total_defects,
        top_defect=top_defect,
        top_defect_percentage=top_defect_percentage
    )


# Run application
if __name__ == '__main__':
    init_db()
    app.run(debug=True)