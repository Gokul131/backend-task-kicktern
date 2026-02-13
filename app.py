from flask import Flask, request, jsonify
from config import Config
from models import db, Contact, ServiceInquiry, Admin
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

# ✅ Create database tables (NEW Flask compatible way)
with app.app_context():
    db.create_all()


# ---------------- Contact API ----------------
@app.route("/api/contact", methods=["POST"])
def create_contact():
    data = request.json

    contact = Contact(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        message=data["message"]
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify({"message": "Contact submitted successfully"}), 201


# ---------------- Service Inquiry API ----------------
@app.route("/api/service-inquiry", methods=["POST"])
def create_service_inquiry():
    data = request.json

    inquiry = ServiceInquiry(
        name=data["name"],
        email=data["email"],
        service_type=data["service_type"],
        requirements=data["requirements"]
    )

    db.session.add(inquiry)
    db.session.commit()

    return jsonify({"message": "Service inquiry submitted"}), 201


# ---------------- Admin Register ----------------
@app.route("/api/admin/register", methods=["POST"])
def register_admin():
    data = request.json

    hashed_password = generate_password_hash(data["password"])
    admin = Admin(username=data["username"], password=hashed_password)

    db.session.add(admin)
    db.session.commit()

    return jsonify({"message": "Admin created"}), 201


# ---------------- Admin Login ----------------
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json

    admin = Admin.query.filter_by(username=data["username"]).first()

    if not admin or not check_password_hash(admin.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=admin.id)
    return jsonify({"access_token": token})


# ---------------- Get Contacts ----------------
@app.route("/api/admin/contacts", methods=["GET"])
@jwt_required()
def get_contacts():
    contacts = Contact.query.all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "message": c.message,
            "created_at": str(c.created_at)
        } for c in contacts
    ])


# ---------------- Get Inquiries ----------------
@app.route("/api/admin/inquiries", methods=["GET"])
@jwt_required()
def get_inquiries():
    inquiries = ServiceInquiry.query.all()

    return jsonify([
        {
            "id": i.id,
            "name": i.name,
            "email": i.email,
            "service_type": i.service_type,
            "requirements": i.requirements,
            "status": i.status,
            "created_at": str(i.created_at)
        } for i in inquiries
    ])


# ---------------- Update Inquiry ----------------
@app.route("/api/admin/inquiry/<int:id>", methods=["PUT"])
@jwt_required()
def update_inquiry(id):
    inquiry = ServiceInquiry.query.get_or_404(id)
    data = request.json

    inquiry.status = data.get("status", inquiry.status)
    db.session.commit()

    return jsonify({"message": "Inquiry updated"})


# ---------------- Delete Inquiry ----------------
@app.route("/api/admin/inquiry/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_inquiry(id):
    inquiry = ServiceInquiry.query.get_or_404(id)

    db.session.delete(inquiry)
    db.session.commit()

    return jsonify({"message": "Inquiry deleted"})


if __name__ == "__main__":
    app.run(debug=True)
