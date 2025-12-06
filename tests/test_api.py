import jwt
from app import JWT_SECRET, User, db

def setup_user(client):
    with client.application.app_context():
        u = User(email="api@x.com")
        u.set_password("123")
        db.session.add(u)
        db.session.commit()
        token = jwt.encode({"user_id": u.id}, JWT_SECRET, algorithm="HS256")
        return token

def test_api_emissions(client):
    token = setup_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    # POST
    r = client.post("/api/emissions", json={
        "category": "transport",
        "amount": 10
    }, headers=headers)
    assert r.status_code == 200

    # GET
    r = client.get("/api/emissions", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json, list)
