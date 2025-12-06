from app import User

def test_register_login(client):
    # rejestracja
    r = client.post("/register", data={
        "email": "test@test.com",
        "password": "123",
        "confirm": "123"
    }, follow_redirects=True)

    # 1. Sprawdzamy czy użytkownik istnieje w bazie
    with client.application.app_context():
        u = User.query.filter_by(email="test@test.com").first()
        assert u is not None

    # 2. Sprawdzamy czy po rejestracji przenosi na ekran logowania
    assert b"Zaloguj" in r.data or b"login" in r.data.lower()

    # 3. Logowanie użytkownika
    r = client.post("/login", data={
        "email": "test@test.com",
        "password": "123"
    }, follow_redirects=True)

    # 4. Po zalogowaniu musi być dashboard
    assert b"Panel" in r.data
