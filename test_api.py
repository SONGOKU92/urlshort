import requests
import json

# Assurez-vous que le serveur Flask est en cours d'exécution
BASE_URL = "http://127.0.0.1:5000"

def test_shorten_url():
    """Test de raccourcissement d'URL"""
    url = f"{BASE_URL}/api/shorten"
    data = {
        "url": "https://www.example.com",
        "generate_qr": True
    }
    
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"URL raccourcie: {result['short_url']}")
        print(f"URL originale: {result['original_url']}")
        print(f"QR Code généré: {'Oui' if 'qr_code' in result else 'Non'}")
        
        # Récupérer les informations sur le lien raccourci
        short_id = result['short_url'].split('/')[-1]
        test_url_info(short_id)
    else:
        print(f"Erreur: {response.text}")

def test_url_info(short_id):
    """Test de récupération d'informations sur une URL raccourcie"""
    url = f"{BASE_URL}/api/info/{short_id}"
    
    response = requests.get(url)
    
    print("\nInformations sur l'URL raccourcie:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"ID court: {result['short_id']}")
        print(f"URL originale: {result['original_url']}")
        print(f"Créé le: {result['created_at']}")
        print(f"Dernier accès: {result['last_accessed']}")
        print(f"Nombre d'accès: {result['access_count']}")
    else:
        print(f"Erreur: {response.text}")

if __name__ == "__main__":
    print("Test de l'API URL Shortener")
    print("--------------------------")
    test_shorten_url()