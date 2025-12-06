from flask import Flask, render_template, request, redirect, url_for, flash, make_response, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import numpy as np
import secrets
import jwt
import logging
import os
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise RuntimeError("Brak FERNET_KEY w pliku .env")

f = Fernet(FERNET_KEY.encode())
# =====================================================
# APP CONFIG
# =====================================================

app = Flask(__name__)
app.secret_key = "change-me-secure"

DB_PATH = "ecotrack.db"

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://ecotrack_user:haslo123@localhost:3307/ecotrack"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

JWT_SECRET = "super-strong-secret"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error("Unhandled exception:", exc_info=e)
    return "Wystąpił błąd. Szczegóły zapisane w error.log", 500


# =====================================================
# MODELS
# =====================================================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)


class EmissionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="emissions")


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    token = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User")


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))


# =====================================================
# CONSTANTS & HELPERS
# =====================================================

FACTORS = {
    "transport": 0.21,
    "energy": 0.233,
    "food": 2.5,
    "other": 1.0
}

POLAND_AVG_CO2 = 8000  # kg rocznie

def compute_emission(cat, amount):
    return float(amount) * FACTORS.get(cat, 1.0)


def daily_sums_for_user(uid):
    recs = EmissionRecord.query.filter_by(user_id=uid).all()
    out = {}
    for r in recs:
        d = r.created_at.date().isoformat()
        out[d] = out.get(d, 0) + float(r.value)
    return dict(sorted(out.items()))


def totals_for_period(uid, days):
    since = datetime.utcnow() - timedelta(days=days - 1)
    recs = EmissionRecord.query.filter(
        EmissionRecord.user_id == uid,
        EmissionRecord.created_at >= since,
    ).all()
    return sum(float(r.value) for r in recs)


def predict_annual_from_daily_sums(sums):
    if not sums:
        return 0
    vals = list(sums.values())
    avg = float(np.mean(vals))
    if len(vals) < 2:
        return avg * 365
    x = np.arange(len(vals))
    y = np.array(vals)
    try:
        a, b = np.polyfit(x, y, 1)
        next_val = max(a * len(vals) + b, avg)
        return next_val * 365
    except:
        return avg * 365


# =====================================================
# AUTH ROUTES
# =====================================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pwd = request.form["password"]
        confirm = request.form["confirm"]

        if pwd != confirm:
            flash("Hasła nie pasują", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email już istnieje", "error")
            return redirect(url_for("register"))

        u = User(email=email)
        u.set_password(pwd)
        db.session.add(u)
        db.session.commit()

        flash("Konto utworzone!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pwd = request.form["password"]

        u = User.query.filter_by(email=email).first()
        if u and u.check_password(pwd):
            login_user(u)

            # Show JWT token
            token = jwt.encode({"user_id": u.id}, JWT_SECRET, algorithm="HS256")
            flash(f"Twój token JWT: {token}", "info")

            return redirect(url_for("dashboard"))

        flash("Błędne dane logowania", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Wylogowano", "success")
    return redirect(url_for("index"))


# =====================================================
# PASSWORD RESET
# =====================================================

@app.route("/reset-request", methods=["GET","POST"])
def reset_request():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            token = secrets.token_urlsafe(32)
            entry = PasswordResetToken(user_id=user.id, token=token)
            db.session.add(entry)
            db.session.commit()
            print("RESET LINK:", f"http://localhost:5000/reset/{token}")

        flash("Jeśli email istnieje, link został wysłany.", "info")
        return redirect(url_for("login"))

    return render_template("reset_request.html")


@app.route("/reset/<token>", methods=["GET","POST"])
def reset_password(token):
    entry = PasswordResetToken.query.filter_by(token=token).first()
    if not entry:
        flash("Nieprawidłowy token", "error")
        return redirect(url_for("login"))

    if (datetime.utcnow() - entry.created_at).total_seconds() > 86400:
        flash("Token wygasł", "error")
        return redirect(url_for("login"))

    user = entry.user

    if request.method == "POST":
        pwd = request.form["password"]
        conf = request.form["confirm"]

        if pwd != conf:
            flash("Hasła nie pasują", "error")
            return redirect(url_for("reset_password", token=token))

        user.set_password(pwd)
        db.session.delete(entry)
        db.session.commit()

        flash("Hasło zmienione!", "success")
        return redirect(url_for("login"))

    return render_template("reset_form.html")


# =====================================================
# DASHBOARD
# =====================================================

@app.route('/dashboard')
@login_required
def dashboard():
    recs = EmissionRecord.query.filter_by(user_id=current_user.id).order_by(
        EmissionRecord.created_at.asc()
    ).all()

    totals = {}
    for r in recs:
        totals[r.category] = totals.get(r.category, 0) + float(r.value)

    daily = daily_sums_for_user(current_user.id)
    predicted = predict_annual_from_daily_sums(daily)
    compare_percent = (predicted / POLAND_AVG_CO2) * 100

    records_json = [{
        "id": r.id,
        "category": r.category,
        "value": r.value,
        "note": r.note,
        "created_at": r.created_at.isoformat(),
    } for r in recs]

    return render_template(
        "dashboard.html",
        records=recs,
        records_json=records_json,
        totals=totals,
        total_sum=sum(totals.values()) if totals else 0,
        predicted_annual=predicted,
        poland_avg=POLAND_AVG_CO2,
        compare_percent=compare_percent,
        last_7=totals_for_period(current_user.id, 7),
        last_30=totals_for_period(current_user.id, 30),
        last_365=totals_for_period(current_user.id, 365),
    )


# =====================================================
# EMISSION CRUD
# =====================================================

@app.route('/emission/add', methods=["POST"])
@login_required
def add_emission():
    category = request.form["category"]
    amount = float(request.form["amount"])
    note = request.form.get("note", "")

    co2 = compute_emission(category, amount)

    if note:
        note += f" (qty:{amount})"
    else:
        note = f"qty:{amount}"

    rec = EmissionRecord(
        user_id=current_user.id,
        category=category,
        value=co2,
        note=note
    )
    db.session.add(rec)
    db.session.commit()

    flash("Dodano emisję", "success")
    return redirect(url_for("dashboard"))


@app.route('/emission/edit/<int:id>', methods=["GET","POST"])
@login_required
def edit_emission(id):
    rec = EmissionRecord.query.get_or_404(id)
    if rec.user_id != current_user.id:
        flash("Brak uprawnień", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        note = request.form.get("note", "")

        rec.value = compute_emission(category, amount)
        rec.category = category
        rec.note = f"{note} (qty:{amount})"

        db.session.commit()
        flash("Zaktualizowano rekord", "success")
        return redirect(url_for("dashboard"))

    raw_amount = rec.value / FACTORS.get(rec.category, 1)
    return render_template("edit_emission.html", rec=rec, raw_amount=raw_amount)


@app.route('/emission/delete/<int:id>', methods=["POST"])
@login_required
def delete_emission(id):
    rec = EmissionRecord.query.get_or_404(id)

    if rec.user_id != current_user.id:
        flash("Brak uprawnień", "error")
        return redirect(url_for("dashboard"))

    db.session.delete(rec)
    db.session.commit()

    flash("Usunięto", "success")
    return redirect(url_for("dashboard"))


# =====================================================
# SIMULATION ("WHAT IF?")
# =====================================================

@app.route("/simulate", methods=["POST"])
@login_required
def simulate():
    data = request.json
    category = data["category"]
    change = float(data["change"])

    delta = compute_emission(category, change)

    yearly = delta * (52 if category in ["transport", "food"] else 12)

    return jsonify({"change_kg_year": yearly})


# =====================================================
# RECOMMENDATIONS
# =====================================================

def generate_recommendations(totals):
    if not totals:
        return ["Dodaj dane, aby zobaczyć wskazówki."]

    dominant = max(totals, key=lambda k: totals[k])

    if dominant == "transport":
        return [
            "Korzystaj częściej z komunikacji miejskiej.",
            "Łącz wiele celów w jedną trasę.",
            "Rozważ rower na krótkie odcinki."
        ]
    if dominant == "energy":
        return [
            "Wymień żarówki na LED.",
            "Wyłącz standby.",
            "Obniż ogrzewanie o 1°C."
        ]
    if dominant == "food":
        return [
            "Dodaj dni bezmięsne.",
            "Kupuj lokalnie.",
            "Planuj posiłki."
        ]
    return [
        "Kupuj produkty wielorazowe.",
        "Naprawiaj zamiast wyrzucać.",
        "Kupuj używane rzeczy."
    ]


@app.route("/tips")
@login_required
def tips():
    recs = EmissionRecord.query.filter_by(user_id=current_user.id).all()
    totals = {}
    for r in recs:
        totals[r.category] = totals.get(r.category, 0) + float(r.value)

    return render_template("tips.html", tips=generate_recommendations(totals))

@app.route("/info")
def info():
    eco_facts = [
        {
            "title": "Średnia emisja CO₂ na osobę (Europa)",
            "value": "6,4 t/rok",
            "desc": "W Europie przeciętna osoba generuje około 6,4 tony CO₂ rocznie."
        },
        {
            "title": "Średnia emisja CO₂ w Polsce",
            "value": "8,0 t/rok",
            "desc": "Polska ma jedną z najwyższych emisji CO₂ per capita w UE."
        },
        {
            "title": "Globalne emisje CO₂",
            "value": "36,8 gigaton/rok",
            "desc": "Cały świat generuje prawie 37 miliardów ton CO₂ rocznie."
        },
        {
            "title": "Transport",
            "value": "24% globalnych emisji",
            "desc": "Pojazdy spalinowe stanowią niemal 1/4 wszystkich emisji."
        },
        {
            "title": "Energia",
            "value": "40% globalnych emisji",
            "desc": "Produkcja prądu i ogrzewanie to największe źródło emisji CO₂."
        },
        {
            "title": "Rolnictwo i żywność",
            "value": "14% globalnych emisji",
            "desc": "Hodowla zwierząt i produkcja żywności znacząco wpływa na klimat."
        }
    ]

    return render_template("info.html", facts=eco_facts)

# =====================================================
# EXPORT CSV & PDF
# =====================================================

@app.route('/export/csv')
@login_required
def export_csv():
    recs = EmissionRecord.query.filter_by(user_id=current_user.id).all()

    rows = [["data","kategoria","co2","notatka"]]
    for r in recs:
        rows.append([
            r.created_at.strftime("%Y-%m-%d %H:%M"),
            r.category,
            r.value,
            r.note
        ])

    out = make_response("\n".join(",".join(map(str, row)) for row in rows))
    out.headers["Content-Disposition"] = "attachment; filename=emisje.csv"
    out.headers["Content-Type"] = "text/csv"
    return out


@app.route('/export/pdf')
@login_required
def export_pdf():
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50,800,"Raport emisji CO₂")
    pdf.setFont("Helvetica", 12)
    y=770

    recs = EmissionRecord.query.filter_by(user_id=current_user.id).all()

    for r in recs:
        pdf.drawString(50,y, f"{r.created_at} | {r.category} | {r.value} | {r.note}")
        y -= 20
        if y < 40:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 800

    pdf.save()
    buf.seek(0)

    return send_file(buf, as_attachment=True, download_name="emisje.pdf")


# =====================================================
# API + JWT
# =====================================================

def api_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split()[1]
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return User.query.get(data["user_id"])
    except:
        return None


@app.route("/api/emissions", methods=["GET"])
def api_list():
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    recs = EmissionRecord.query.filter_by(user_id=u.id).all()
    return jsonify([{
        "id": r.id,
        "category": r.category,
        "value": r.value,
        "note": r.note,
        "created_at": r.created_at.isoformat()
    } for r in recs])


@app.route("/api/emissions", methods=["POST"])
def api_create():
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    d = request.json
    category = d["category"]
    amount = float(d["amount"])

    co2 = compute_emission(category, amount)

    rec = EmissionRecord(
        user_id=u.id,
        category=category,
        value=co2,
        note=f"qty:{amount}"
    )

    db.session.add(rec)
    db.session.commit()

    return jsonify({"id": rec.id, "co2": co2})


@app.route("/api/emissions/<int:id>", methods=["PUT"])
def api_update(id):
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    rec = EmissionRecord.query.get_or_404(id)
    if rec.user_id != u.id:
        return jsonify({"error": "forbidden"}), 403

    d = request.json
    cat = d.get("category", rec.category)
    amount = d.get("amount")

    if amount is not None:
        amount = float(amount)
        rec.value = compute_emission(cat, amount)
        rec.note = f"qty:{amount}"

    rec.category = cat
    db.session.commit()

    return jsonify({"status": "updated"})


@app.route("/api/emissions/<int:id>", methods=["DELETE"])
def api_delete(id):
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    rec = EmissionRecord.query.get_or_404(id)
    if rec.user_id != u.id:
        return jsonify({"error": "forbidden"}), 403

    db.session.delete(rec)
    db.session.commit()

    return jsonify({"status": "deleted"})


@app.route("/api/calc", methods=["POST"])
def api_calc():
    d = request.json
    return jsonify({
        "co2": compute_emission(d["category"], float(d["amount"]))
    })


@app.route("/api/stats/category")
def api_category_stats():
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    recs = EmissionRecord.query.filter_by(user_id=u.id).all()
    sums = {}
    for r in recs:
        sums[r.category] = sums.get(r.category, 0) + r.value

    return jsonify(sums)


@app.route("/api/predict")
def api_predict():
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    daily = daily_sums_for_user(u.id)
    return jsonify({
        "daily": daily,
        "predicted_annual": predict_annual_from_daily_sums(daily)
    })


# =====================================================
# OPENAPI + SWAGGER UI
# =====================================================

@app.route("/api/openapi.json")
def openapi_json():
    return jsonify({
        "openapi": "3.0.0",
        "info": {"title": "Ecotrack API", "version": "1.0"},
        "paths": {
            "/api/emissions": {"get": {}, "post": {}},
            "/api/emissions/{id}": {"put": {}, "delete": {}},
            "/api/calc": {"post": {}},
            "/api/stats/category": {"get": {}},
            "/api/predict": {"get": {}}
        }
    })


@app.route("/api/docs")
def swagger_ui():
    return """
    <html>
    <head>
      <link rel="stylesheet" href="/static/swagger/swagger-ui.css">
    </head>
    <body style="margin:0">
        <div id="swagger-ui"></div>

        <script src="/static/swagger/swagger-ui-bundle.js"></script>
        <script src="/static/swagger/swagger-ui-standalone-preset.js"></script>

        <script>
        window.onload = () => {
            SwaggerUIBundle({
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset]
            })
        }
        </script>
    </body>
    </html>
    """


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
