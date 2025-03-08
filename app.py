from flask import Flask, request, redirect, jsonify, url_for
import random
import string
import os
import qrcode
from io import BytesIO
import base64
from urllib.parse import urlparse
import requests
import urllib3
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.sql import func

# Désactiver les avertissements SSL pour les requêtes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Configuration de la base de données (SQLite en local)
DATABASE_URL = 'sqlite:///urls.db'  
engine = create_engine(DATABASE_URL)

metadata = MetaData()

# Définition du modèle de la table urls
urls = Table(
    'urls',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('short_id', String, unique=True, nullable=False),
    Column('long_url', String, nullable=False),
    Column('qr_code', String),
    Column('created_at', DateTime, server_default=func.now()),
    Column('last_accessed', DateTime),
    Column('access_count', Integer, default=0)
)

def init_db():
    """Initialisation de la base de données"""
    metadata.create_all(engine)

# Initialisation de la base de données au démarrage
with app.app_context():
    init_db()

def generate_short_id(num_chars=6):
    """Génère un identifiant court aléatoire"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))

def is_url_accessible(url):
    """Vérifie si une URL est accessible"""
    try:
        # Assure que l'URL commence par http:// ou https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return False

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
            return response.status_code < 500
        except:
            # Tentative avec http:// si https:// échoue
            if url.startswith('https://'):
                try:
                    response = requests.get(url.replace('https://', 'http://'), headers=headers, timeout=10, verify=False)
                    return response.status_code < 500
                except:
                    pass
            return False

    except Exception as e:
        print(f"Erreur lors de la vérification de l'URL : {str(e)}")
        return False

def generate_qr_code(url):
    """Génère un QR code à partir d'une URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def store_url(short_id, long_url, qr_code=None):
    """Enregistre une URL raccourcie dans la base de données"""
    with engine.connect() as conn:
        conn.execute(
            urls.insert().values(
                short_id=short_id,
                long_url=long_url,
                qr_code=qr_code,
                created_at=datetime.now()
            )
        )
        conn.commit()

def get_url(short_id):
    """Récupère une URL longue à partir d'un identifiant court"""
    with engine.connect() as conn:
        # Mise à jour du compteur d'accès
        conn.execute(
            urls.update()
            .where(urls.c.short_id == short_id)
            .values(
                access_count=urls.c.access_count + 1,
                last_accessed=datetime.now()
            )
        )
        conn.commit()
        
        # Récupération de l'URL
        result = conn.execute(
            urls.select().where(urls.c.short_id == short_id)
        ).first()
        return result.long_url if result else None

# Routes API
@app.route('/api/shorten', methods=['POST'])
def api_shorten_url():
    """API endpoint pour raccourcir une URL"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL non fournie"}), 400
    
    long_url = data['url']
    generate_qr = data.get('generate_qr', False)
    
    if not is_url_accessible(long_url):
        return jsonify({"error": "L'URL fournie est inaccessible"}), 400

    # Générer un identifiant court unique
    short_id = generate_short_id()
    while True:
        with engine.connect() as conn:
            result = conn.execute(
                urls.select().where(urls.c.short_id == short_id)
            ).first()
            if not result:
                break
        short_id = generate_short_id()

    # Créer l'URL courte
    short_url = url_for('redirect_to_long_url', short_id=short_id, _external=True)

    # Générer le QR code si demandé
    qr_code_img = None
    if generate_qr:
        qr_code_img = generate_qr_code(short_url)

    # Enregistrer dans la base de données
    try:
        store_url(short_id, long_url, qr_code_img)
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'enregistrement: {str(e)}"}), 500

    # Préparer la réponse
    response = {
        "short_url": short_url,
        "original_url": long_url
    }
    
    if generate_qr:
        response["qr_code"] = qr_code_img
    
    return jsonify(response), 201

@app.route('/api/info/<short_id>', methods=['GET'])
def api_url_info(short_id):
    """API endpoint pour obtenir des informations sur une URL raccourcie"""
    with engine.connect() as conn:
        result = conn.execute(
            urls.select().where(urls.c.short_id == short_id)
        ).first()
        
        if not result:
            return jsonify({"error": "URL non trouvée"}), 404
        
        url_info = {
            "short_id": result.short_id,
            "original_url": result.long_url,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "last_accessed": result.last_accessed.isoformat() if result.last_accessed else None,
            "access_count": result.access_count
        }
        
        if result.qr_code:
            url_info["qr_code"] = result.qr_code
            
        return jsonify(url_info), 200

@app.route('/<short_id>')
def redirect_to_long_url(short_id):
    """Redirige vers l'URL longue correspondant à l'identifiant court"""
    long_url = get_url(short_id)
    if long_url:
        return redirect(long_url)
    else:
        return jsonify({"error": "URL non trouvée"}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)