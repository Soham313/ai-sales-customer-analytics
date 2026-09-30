from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    # 1. Register new user
    email = "testuser_analytics@example.com"
    pwd = "securepassword123"
    
    reg_resp = client.post("/api/auth/register", json={
        "email": email,
        "password": pwd
    })
    
    # 201 Created or 400 if already exists from prior test runs
    assert reg_resp.status_code in [201, 400]
    
    if reg_resp.status_code == 201:
        data = reg_resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
    # 2. Login user
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": pwd
    })
    
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    
    # 3. Test Protected Me Endpoint
    me_resp = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == email
