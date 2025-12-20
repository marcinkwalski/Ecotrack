import pymysql
pymysql.install_as_MySQLdb()
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

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "mysql+pymysql://host523765_ecotrack:dt65fr6aJj4LMRz99YQZ@localhost/host523765_ecotrack?charset=utf8mb4"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET = "super-strong-secret"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_exception(e):
    # Jeśli to normalny HTTP wyjątek (np. 404 dla static) → Flask powinien go obsłużyć
    if isinstance(e, HTTPException):
        return e

    # Loguj tylko prawdziwe błędy 500
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
    subcategory = db.Column(db.String(100), nullable=True)

    raw_amount = db.Column(db.Float, nullable=True)
    amount_unit = db.Column(db.String(20), nullable=True)

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
# EMISSION FACTORS
# =====================================================

EMISSION_FACTORS = {
    "transport": {
        "walk": 0.0,
        "bike": 0.0,
        "escooter_electric": 0.021,
        "scooter_petrol": 0.072,
        "car_petrol": 0.192,
        "car_diesel": 0.171,
        "car_hybrid": 0.110,
        "car_ev": 0.045,
        "bus": 0.105,
        "train": 0.041,
        "plane_short": 0.254,
        "plane_long": 0.151
    },
    "food": {
        "beef": 27.0,
        "lamb": 24.0,
        "cheese": 13.0,
        "pork": 12.0,
        "poultry": 6.9,
        "eggs": 4.8,
        "fish": 5.4,
        "vegetables": 2.0,
        "fruits": 1.0,
        "grains": 1.4,
        "nuts": 0.3
    },
    "energy": {
        "electricity_pl": 0.724,
        "electricity_green": 0.05,
        "gas": 2.0,
        "lpg": 1.6,
        "coal": 2.42
    },
    "other": {
        "electronics": 200.0,
        "clothing": 10.0,
        "furniture": 150.0
    }
}

POLAND_AVG_CO2 = 8000

# =====================================================
# SUBCATEGORY LABELS (Polskie nazwy)
# =====================================================

SUBCATEGORY_LABELS = {
    # Transport
    "walk": "Spacer",
    "bike": "Rower",
    "escooter_electric": "Hulajnoga elektryczna",
    "scooter_petrol": "Skuter (benzyna)",
    "car_petrol": "Samochód benzynowy",
    "car_diesel": "Samochód diesel",
    "car_hybrid": "Samochód hybrydowy",
    "car_ev": "Samochód elektryczny",
    "bus": "Autobus",
    "train": "Pociąg",
    "plane_short": "Lot krótki",
    "plane_long": "Lot długi",

    # Jedzenie
    "beef": "Wołowina",
    "lamb": "Baranina",
    "cheese": "Ser",
    "pork": "Wieprzowina",
    "poultry": "Drób",
    "eggs": "Jajka",
    "fish": "Ryby",
    "vegetables": "Warzywa",
    "fruits": "Owoce",
    "grains": "Zboża",
    "nuts": "Orzechy",

    # Energia
    "electricity_pl": "Prąd (mix PL)",
    "electricity_green": "Zielona energia",
    "gas": "Gaz ziemny",
    "lpg": "LPG",
    "coal": "Węgiel",

    # Inne
    "electronics": "Elektronika",
    "clothing": "Ubrania",
    "furniture": "Meble"
}


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def compute_emission(category, subcategory, amount):
    try:
        factor = EMISSION_FACTORS.get(category, {}).get(subcategory)
        if factor is None:
            return float(amount)
        return float(amount) * float(factor)
    except:
        return float(amount)

def daily_sums_for_user(uid):
    recs = EmissionRecord.query.filter_by(user_id=uid).all()
    sums = {}
    for r in recs:
        d = r.created_at.date().isoformat()
        sums[d] = sums.get(d, 0) + float(r.value)
    return dict(sorted(sums.items()))

def totals_for_period(uid, days):
    since = datetime.utcnow() - timedelta(days=days - 1)
    recs = EmissionRecord.query.filter(
        EmissionRecord.user_id == uid,
        EmissionRecord.created_at >= since
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

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html", year=datetime.now().year)

@app.route("/register", methods=["GET", "POST"])
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        pwd = request.form["password"]

        u = User.query.filter_by(email=email).first()
        if u and u.check_password(pwd):
            login_user(u)
            token = jwt.encode({"user_id": u.id}, JWT_SECRET, algorithm="HS256")
            flash(f"Twój token JWT: {token}", "info")
            return redirect(url_for("dashboard"))

        flash("Błędne dane logowania", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Wylogowano", "success")
    return redirect(url_for("index"))

@app.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            # tu możesz później dodać wysyłanie maila / token
            flash("Jeśli konto istnieje, wysłaliśmy instrukcję resetu hasła.", "info")
        else:
            flash("Jeśli konto istnieje, wysłaliśmy instrukcję resetu hasła.", "info")

        return redirect(url_for("login"))

    return render_template("reset_request.html")

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
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

    return render_template(
    "dashboard.html",
    records=recs,
    SUBCATEGORY_LABELS=SUBCATEGORY_LABELS,
    records_json=[
        {
            "id": r.id,
            "category": r.category,
            "subcategory": r.subcategory,
            "raw_amount": r.raw_amount,
            "amount_unit": r.amount_unit,
            "value": r.value,
            "note": r.note,
            "created_at": r.created_at.isoformat()
        }
        for r in recs
    ],
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
    subcategory = request.form.get("subcategory") or None
    # surowa ilość podana przez użytkownika
    try:
        raw_amount = float(request.form["amount"])
    except (ValueError, TypeError):
        flash("Nieprawidłowa ilość", "error")
        return redirect(url_for("dashboard"))

    unit = request.form.get("unit") or ""   # np. "km", "kg", "kWh"
    note = request.form.get("note", "")

    co2 = compute_emission(category, subcategory, raw_amount)

    # poprawne złożenie notatki
  
    rec = EmissionRecord(
        user_id=current_user.id,
        category=category,
        subcategory=subcategory,
        raw_amount=raw_amount,
        amount_unit=unit,
        value=co2,
        note=note
    )

    db.session.add(rec)
    db.session.commit()

    flash("Dodano emisję", "success")
    return redirect(url_for("dashboard"))

@app.route("/emission/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_emission(id):
    rec = EmissionRecord.query.get_or_404(id)

    if rec.user_id != current_user.id:
        flash("Brak uprawnień", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        category = request.form["category"]
        subcategory = request.form.get("subcategory")
        raw_amount = float(request.form["amount"])
        unit = request.form.get("unit", "")
        note = request.form.get("note", "")

        co2 = compute_emission(category, subcategory, raw_amount)

        rec.category = category
        rec.subcategory = subcategory
        rec.raw_amount = raw_amount
        rec.amount_unit = unit
        rec.value = co2
        rec.note = note 

        db.session.commit()
        flash("Zaktualizowano rekord", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_emission.html", rec=rec)


@app.route("/emission/delete/<int:id>", methods=["POST"])
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

    category = data.get("category")
    subcategory = data.get("subcategory")
    amount_change = float(data.get("change", 0))  # np. km, kWh, kg

    # Jeśli brak czynności → błąd
    if not category or not subcategory:
        return jsonify({"error": "Brak kategorii lub podkategorii"}), 400

    # Emisja dla danej czynności
    co2_per_unit = EMISSION_FACTORS.get(category, {}).get(subcategory)
    if co2_per_unit is None:
        return jsonify({"error": "Brak danych emisji"}), 400

    # Różnica emisji
    delta_daily = amount_change * co2_per_unit
    delta_monthly = delta_daily * 30
    delta_yearly = delta_daily * 365

    # W tonach
    delta_yearly_tons = delta_yearly / 1000

    # Porównanie do realnych ekwiwalentów
    trees = delta_yearly / 22  # średnio 1 drzewo pochłania ~22 kg CO2/rok
    car_km = delta_yearly / 0.18  # średnio auto emituje 180 g CO₂/km

    result = {
        "category": category,
        "subcategory": subcategory,
        "amount_change": amount_change,

        "daily": round(delta_daily, 3),
        "monthly": round(delta_monthly, 3),
        "yearly": round(delta_yearly, 3),
        "yearly_tons": round(delta_yearly_tons, 3),

        "equivalents": {
            "trees_absorbed": round(trees, 1),
            "car_km": round(car_km, 0)
        }
    }

    return jsonify(result)



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
            "Rozważ rower zamiast samochodu."
        ]
    if dominant == "energy":
        return [
            "Wymień żarówki na LED.",
            "Wyłącz standby w urządzeniach.",
            "Obniż ogrzewanie o 1°C."
        ]
    if dominant == "food":
        return [
            "Dodaj dni bezmięsne.",
            "Kupuj lokalnie i sezonowo.",
            "Ogranicz czerwone mięso."
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



# =====================================================
# INFO PAGE
# =====================================================

@app.route("/info")
def info():
    eco_facts = [
        {
            "title": "Średnia emisja CO₂ w Europie",
            "value": "6,4 t/rok",
        },
        {
            "title": "Średnia emisja CO₂ w Polsce",
            "value": "8,0 t/rok",
        },
        {
            "title": "Globalne emisje CO₂",
            "value": "36,8 gigaton/rok",
        }
    ]
    return render_template("info.html", facts=eco_facts)


# =====================================================
# EXPORT CSV & PDF
# =====================================================

@app.route("/export/csv")
@login_required
def export_csv():
    recs = EmissionRecord.query.filter_by(user_id=current_user.id).all()

    rows = [["data", "kategoria", "podkategoria", "ilość", "jednostka", "co2", "notatka"]]
    for r in recs:
        rows.append([
            r.created_at.strftime("%Y-%m-%d %H:%M"),
            r.category,
            r.subcategory or "",
            r.raw_amount or "",
            r.amount_unit or "",
            r.value,
            r.note or ""
        ])

    content = "\n".join(",".join(map(str, row)) for row in rows)

    out = make_response(content)
    out.headers["Content-Disposition"] = "attachment; filename=emisje.csv"
    out.headers["Content-Type"] = "text/csv"
    return out

def ascii_only(s):
    if not s:
        return ""
    return s.encode("ascii", errors="ignore").decode("ascii")


# zamień istniejącą funkcję export_pdf() tym kodem
@app.route("/export/pdf")
@login_required
def export_pdf():
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        def ascii_only(s):
            if not s:
                return ""
            return s.encode("ascii", errors="ignore").decode("ascii")

        # próba znalezienia DejaVuSans.ttf w kilku miejscach
        font_candidates = [
            os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf"),
            os.path.join(os.path.dirname(__file__), "static", "fonts", "DejaVuSans.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/local/share/fonts/DejaVuSans.ttf"
        ]
        font_path = None
        for p in font_candidates:
            if p and os.path.isfile(p):
                font_path = p
                break

        use_unicode_font = False
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", font_path))
                use_unicode_font = True
            except Exception as fe:
                logging.exception("export_pdf: nie udalo sie zarejestrowac DejaVu: %s", fe)
                use_unicode_font = False

        # przygotowanie stylow
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        if use_unicode_font:
            # override fontName w stylu na zarejestrowana czcionke
            normal_style = styles["Normal"].clone('normal_dejavu')
            normal_style.fontName = "DejaVu"

        # pobierz rekordy
        recs = EmissionRecord.query.filter_by(user_id=current_user.id).order_by(EmissionRecord.created_at.asc()).all()

        # przygotuj dokument w pamieci
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=30)
        story = []

        if not recs:
            story.append(Paragraph("Brak rekordow emisji.", normal_style))
        else:
            # naglowek
            story.append(Paragraph("Raport emisji CO2", normal_style))
            story.append(Spacer(1, 12))

            for r in recs:
                created = r.created_at.strftime('%Y-%m-%d %H:%M')
                cat = r.category or ""
                sub = r.subcategory or ""
                amt = str(r.raw_amount) if r.raw_amount is not None else ""
                unit = r.amount_unit or ""
                val = str(round(r.value, 3))
                note = r.note or ""

                if not use_unicode_font:
                    # jesli brak czcionki unicode - oczyszczamy pola
                    created = ascii_only(created)
                    cat = ascii_only(cat)
                    sub = ascii_only(sub)
                    amt = ascii_only(amt)
                    unit = ascii_only(unit)
                    val = ascii_only(val)
                    note = ascii_only(note)

                line = f"{created} — {cat}/{sub} — {amt} {unit} — {val} kg CO2"
                if note:
                    line += f" — {note}"

                # unikamy bardzo dlugich paragrafow (Platypus lamie tekst)
                story.append(Paragraph(line, normal_style))
                story.append(Spacer(1, 6))

        # zbuduj dokument
        doc.build(story)

        buf.seek(0)
        pdf_bytes = buf.read()

        # Zwracamy surowe bytes jako odpowiedz - unikamy send_file wrapperow
        from flask import Response
        resp = Response(pdf_bytes, mimetype="application/pdf")
        resp.headers["Content-Disposition"] = "attachment; filename=emisje.pdf"
        return resp

    except Exception as e:
        logging.exception("export_pdf: blad podczas generowania PDF: %s", e)
        # zapisz szczegoly do error.log i poinformuj usera
        flash("Wystapil blad podczas generowania PDF. Sprawdz logi serwera.", "error")
        return redirect(url_for("dashboard"))



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
        "subcategory": r.subcategory,
        "raw_amount": r.raw_amount,
        "unit": r.amount_unit,
        "value": r.value,
        "created_at": r.created_at.isoformat()
    } for r in recs])


@app.route("/api/emissions", methods=["POST"])
def api_create():
    u = api_user()
    if not u:
        return jsonify({"error": "unauthorized"}), 401

    d = request.json
    category = d.get("category")
    subcategory = d.get("subcategory")
    amount = float(d.get("amount", 0))
    unit = d.get("unit", "")

    co2 = compute_emission(category, subcategory, amount)

    rec = EmissionRecord(
        user_id=u.id,
        category=category,
        subcategory=subcategory,
        raw_amount=amount,
        amount_unit=unit,
        value=co2,
        note=f"qty:{amount}{unit}"
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

    category = d.get("category", rec.category)
    subcat = d.get("subcategory", rec.subcategory)
    amount = float(d.get("amount", rec.raw_amount))
    unit = d.get("unit", rec.amount_unit)

    co2 = compute_emission(category, subcat, amount)

    rec.category = category
    rec.subcategory = subcat
    rec.raw_amount = amount
    rec.amount_unit = unit
    rec.value = co2

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
    category = d.get("category")
    subcat = d.get("subcategory")
    amount = float(d.get("amount", 0))

    return jsonify({
        "co2": compute_emission(category, subcat, amount)
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
# SWAGGER
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
