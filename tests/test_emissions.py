def login(client):
    client.post("/register", data={
        "email": "x@x.com",
        "password": "123",
        "confirm": "123"
    })
    client.post("/login", data={
        "email": "x@x.com",
        "password": "123"
    })

def test_add_emission(client):
    login(client)
    r = client.post("/emission/add", data={
        "category": "transport",
        "amount": "10",
        "note": "test"
    }, follow_redirects=True)
    assert b"Dodano emisj" in r.data

def test_delete_emission(client):
    login(client)
    client.post("/emission/add", data={
        "category": "transport",
        "amount": "10"
    })
    r = client.post("/emission/delete/1", follow_redirects=True)
    assert b"Usuni" in r.data
