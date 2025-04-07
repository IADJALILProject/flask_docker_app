from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import User
import csv
from io import StringIO
from flask import Response

from app.models import db
from sqlalchemy import text

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/init-db")
def check_users_csv():
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM users_csv"))
        count = result.scalar()
        return jsonify({"status": "ok", "message": f"Table users_csv contient {count} lignes."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@main.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@main.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User added"}), 201

@main.route("/export-csv")
def export_csv():
    # Exécution brute SQL (ou use ORM si besoin)
    query = text("SELECT * FROM users_csv")
    result = db.session.execute(query)

    # Préparation CSV dans une string
    si = StringIO()
    writer = csv.writer(si)
    
    # En-têtes dynamiques
    writer.writerow(result.keys())

    for row in result:
        writer.writerow(row)

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=export_users.csv"}
    )




