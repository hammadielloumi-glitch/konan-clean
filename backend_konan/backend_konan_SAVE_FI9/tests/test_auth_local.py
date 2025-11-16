import requests

BASE_URL = "http://127.0.0.1:8000"


def test_login_and_me():
    """Teste la connexion et la récupération du profil utilisateur."""

    login_url = f"{BASE_URL}/api/auth/login"
    me_url = f"{BASE_URL}/api/auth/me"

    payload = {
        "email": "test@konan.ai",
        "password": "KING",  # mot de passe défini par /api/auth/seed-test-user
    }

    print("🔹 Tentative de connexion…")
    res = requests.post(login_url, json=payload)
    assert res.status_code == 200, f"Erreur login: {res.text}"

    data = res.json()
    token = data.get("access_token")
    assert token, "Aucun token retourné"

    print(f"✅ Connexion réussie → token généré: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}"}
    res_me = requests.get(me_url, headers=headers)
    assert res_me.status_code == 200, f"Erreur /me: {res_me.text}"

    user_data = res_me.json()
    print(f"👤 Profil utilisateur: {user_data}")
    assert user_data["email"] == "test@konan.ai"
    print("✅ Authentification et profil validés avec succès")


if __name__ == "__main__":
    test_login_and_me()

