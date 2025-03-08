Installation

Clonez ce dépôt

bashCopygit clone https://github.com/yourusername/url-shortener-api.git
cd url-shortener-api

Créez un environnement virtuel

bashCopypython -m venv venv

Activez l'environnement virtuel

Sur Windows:
bashCopyvenv\Scripts\activate
Sur macOS/Linux:
bashCopysource venv/bin/activate

Installez les dépendances

bashCopypip install -r requirements.txt
Utilisation
Démarrer le serveur
bashCopypython app.py
Le serveur démarre sur http://127.0.0.1:5000.
Endpoints API
Raccourcir une URL
POST /api/shorten
Corps de la requête (JSON):
jsonCopy{
  "url": "https://example.com/long-url",
  "generate_qr": true
}
Le paramètre generate_qr est optionnel (défaut: false).
Exemple de réponse:
jsonCopy{
  "original_url": "https://example.com/long-url",
  "short_url": "http://127.0.0.1:5000/abc123",
  "qr_code": "data:image/png;base64,..."
}
Obtenir des informations sur une URL raccourcie
GET /api/info/<short_id>
Exemple de réponse:
jsonCopy{
  "short_id": "abc123",
  "original_url": "https://example.com/long-url",
  "created_at": "2025-03-08T12:34:56",
  "last_accessed": "2025-03-08T13:45:12",
  "access_count": 5,
  "qr_code": "data:image/png;base64,..."
}
Redirection
GET /<short_id>
Redirige vers l'URL originale correspondant à l'identifiant court.
Exemples d'utilisation avec cURL
Raccourcir une URL
bashCopycurl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "generate_qr": true}'
Obtenir des informations sur une URL raccourcie
bashCopycurl -X GET http://127.0.0.1:5000/api/info/abc123
Personnalisation
Longueur de l'identifiant court
Vous pouvez modifier la longueur de l'identifiant court en changeant le paramètre num_chars dans la fonction generate_short_id().
Base de données
Par défaut, l'application utilise SQLite. Pour utiliser une autre base de données, modifiez la variable DATABASE_URL
