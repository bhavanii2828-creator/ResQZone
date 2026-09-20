from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "resqzone.db"


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            emergency_type TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route('/')
def home():
    return 'ResQZone Backend is Running!'


# ---------------- API STATUS ----------------

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'success',
        'message': 'ResQZone API is working'
    })


# ---------------- CREATE REPORT ----------------

@app.route('/api/report', methods=['POST'])
def report():

    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400

    name = data.get('name')
    location = data.get('location')
    emergency_type = data.get('emergency_type')
    description = data.get('description')

    if not name or not location or not emergency_type or not description:
        return jsonify({
            'status': 'error',
            'message': 'All fields are required'
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports
        (name, location, emergency_type, description)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        location,
        emergency_type,
        description
    ))

    conn.commit()

    report_id = cursor.lastrowid

    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Report submitted successfully',
        'report_id': report_id
    }), 201


# ---------------- GET ALL REPORTS ----------------

@app.route('/api/reports', methods=['GET'])
def get_reports():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, location, emergency_type,
               description, status
        FROM reports
    """)

    rows = cursor.fetchall()

    conn.close()

    reports = []

    for row in rows:
        reports.append({
            'id': row[0],
            'name': row[1],
            'location': row[2],
            'emergency_type': row[3],
            'description': row[4],
            'status': row[5]
        })

    return jsonify({
        'status': 'success',
        'reports': reports
    })


# ---------------- GET ONE REPORT ----------------

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, location, emergency_type,
               description, status
        FROM reports
        WHERE id = ?
    """, (report_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return jsonify({
            'status': 'error',
            'message': 'Report not found'
        }), 404

    return jsonify({
        'status': 'success',
        'report': {
            'id': row[0],
            'name': row[1],
            'location': row[2],
            'emergency_type': row[3],
            'description': row[4],
            'status': row[5]
        }
    })


# ---------------- UPDATE REPORT STATUS ----------------

@app.route('/api/reports/<int:report_id>/status', methods=['PUT'])
def update_status(report_id):

    data = request.get_json()

    if not data or not data.get('status'):
        return jsonify({
            'status': 'error',
            'message': 'Status is required'
        }), 400

    new_status = data.get('status')

    allowed_statuses = [
        'Pending',
        'Accepted',
        'In Progress',
        'Resolved'
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            'status': 'error',
            'message': 'Invalid status'
        }), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reports
        SET status = ?
        WHERE id = ?
    """, (new_status, report_id))

    if cursor.rowcount == 0:
        conn.close()

        return jsonify({
            'status': 'error',
            'message': 'Report not found'
        }), 404

    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Report status updated successfully'
    })


# ---------------- DELETE REPORT ----------------

@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM reports
        WHERE id = ?
    """, (report_id,))

    if cursor.rowcount == 0:
        conn.close()

        return jsonify({
            'status': 'error',
            'message': 'Report not found'
        }), 404

    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Report deleted successfully'
    })


# ---------------- START SERVER ----------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)