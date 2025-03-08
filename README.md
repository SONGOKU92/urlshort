LinkMinimizer API
Un service API léger et performant pour raccourcir vos URLs et générer des QR codes instantanément. Développé avec Flask et SQLAlchemy, il offre une solution autonome, sans dépendances externes complexes.
🚀 Pourquoi LinkMinimizer?

Simple mais puissant - Une API REST minimaliste pour intégrer la fonctionnalité de raccourcissement d'URL dans n'importe quelle application
QR Codes intégrés - Générez automatiquement des codes QR pour chaque lien raccourci
Statistiques de suivi - Suivez le nombre d'accès à chaque lien et leur dernière utilisation
Installation locale facile - Base de données SQLite intégrée, aucune configuration complexe requise
Vérification d'URL - Validation automatique des URLs pour garantir qu'elles sont accessibles

🛠️ Technologies

Flask - Framework web léger
SQLAlchemy - ORM pour la gestion de base de données
QRCode - Génération de codes QR
Requests - Vérification d'accessibilité des URLs

💻 Installation
1. Clonez ce dépôt
bashCopygit clone https://github.com/yourusername/LinkMinimizer.git
cd LinkMinimizer
2. Créez un environnement virtuel
bashCopypython -m venv venv
3. Activez l'environnement virtuel
Windows:
bashCopyvenv\Scripts\activate
macOS/Linux:
bashCopysource venv/bin/activate
4. Installez les dépendances
bashCopypip install -r requirements.txt
🚀 Démarrage rapide
Lancer le serveur
bashCopypython app.py
Le serveur démarre sur http://127.0.0.1:5000.
📝 Utilisation de l'API
1. Raccourcir une URL
Requête:
bashCopycurl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very-long-url-that-needs-shortening", "generate_qr": true}'
Réponse:
jsonCopy{
  "original_url": "https://example.com/very-long-url-that-needs-shortening",
  "short_url": "http://127.0.0.1:5000/abc123",
  "qr_code": "data:image/png;base64,..."
}
2. Obtenir des informations sur une URL raccourcie
Requête:
bashCopycurl -X GET http://127.0.0.1:5000/api/info/abc123
Réponse:
jsonCopy{
  "short_id": "abc123",
  "original_url": "https://example.com/very-long-url-that-needs-shortening",
  "created_at": "2025-03-08T12:34:56",
  "last_accessed": "2025-03-08T13:45:12",
  "access_count": 5,
  "qr_code": "data:image/png;base64,..."
}
3. Rediriger vers l'URL originale
Il suffit d'accéder à l'URL courte dans un navigateur ou avec curl:
bashCopycurl -L http://127.0.0.1:5000/abc123
🧪 Tester l'API
Utilisez le script de test fourni:
bashCopypython test_api.py
🔧 Code d'intégration
Exemple Python pour raccourcir une URL
pythonCopyimport requests
import json

def shorten_url(long_url, generate_qr=False):
    url = "http://127.0.0.1:5000/api/shorten"
    payload = {
        "url": long_url,
        "generate_qr": generate_qr
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Erreur: {response.text}")

# Exemple d'utilisation
result = shorten_url("https://example.com/long-url", True)
print(f"URL courte: {result['short_url']}")
if 'qr_code' in result:
    # Sauvegarder le QR code
    qr_data = result['qr_code'].split(',')[1]
    with open("qrcode.png", "wb") as f:
        import base64
        f.write(base64.b64decode(qr_data))
    print("QR code sauvegardé dans qrcode.png")
Exemple JavaScript pour raccourcir une URL
javascriptCopyasync function shortenUrl(longUrl, generateQr = false) {
  const response = await fetch('http://127.0.0.1:5000/api/shorten', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url: longUrl,
      generate_qr: generateQr
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Erreur: ${response.statusText}`);
  }
  
  return response.json();
}

// Exemple d'utilisation
shortenUrl('https://example.com/long-url', true)
  .then(data => {
    console.log(`URL courte: ${data.short_url}`);
    
    if (data.qr_code) {
      // Afficher le QR code dans une image
      const img = document.createElement('img');
      img.src = data.qr_code;
      document.body.appendChild(img);
    }
  })
  .catch(error => console.error('Erreur:', error));
⚙️ Personnalisation
Modifier la longueur de l'identifiant court
Dans app.py, modifiez la fonction generate_short_id():
pythonCopydef generate_short_id(num_chars=8):  # Changez 6 par 8 pour des identifiants plus longs
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))
Utiliser une autre base de données
Modifiez la variable DATABASE_URL dans app.py:
pythonCopy# Pour PostgreSQL
DATABASE_URL = 'postgresql://username:password@localhost/dbname'

# Pour MySQL
DATABASE_URL = 'mysql://username:password@localhost/dbname'
N'oubliez pas d'installer les pilotes correspondants:
bashCopypip install psycopg2-binary  # Pour PostgreSQL
pip install pymysql  # Pour MySQL
