from flask import Flask, request, redirect, jsonify, url_for, render_template_string, flash
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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

DATABASE_URL = 'sqlite:///urls.db'  
engine = create_engine(DATABASE_URL)

metadata = MetaData()

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
    metadata.create_all(engine)

with app.app_context():
    init_db()

def generate_short_id(num_chars=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))

def is_url_accessible(url):
    try:
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
    with engine.connect() as conn:
        conn.execute(
            urls.update()
            .where(urls.c.short_id == short_id)
            .values(
                access_count=urls.c.access_count + 1,
                last_accessed=datetime.now()
            )
        )
        conn.commit()
        
        result = conn.execute(
            urls.select().where(urls.c.short_id == short_id)
        ).first()
        return result.long_url if result else None

def get_recent_urls(limit=5):
    with engine.connect() as conn:
        result = conn.execute(
            urls.select().order_by(urls.c.created_at.desc()).limit(limit)
        ).fetchall()
        return result

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        input[type="url"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }
        .checkbox {
            display: flex;
            align-items: center;
        }
        .checkbox label {
            margin-left: 10px;
            margin-bottom: 0;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result-group {
            margin-bottom: 15px;
        }
        .result-value {
            word-break: break-all;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .flash-messages {
            margin-bottom: 20px;
        }
        .flash-message {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .recent-urls {
            margin-top: 30px;
        }
        .url-item {
            display: flex;
            flex-direction: column;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .url-item:last-child {
            border-bottom: none;
        }
        .url-item-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .qr-code {
            text-align: center;
            margin-top: 20px;
        }
        .qr-code img {
            max-width: 200px;
        }
        .mini-qr-code {
            text-align: center;
            margin-top: 10px;
        }
        .mini-qr-code img {
            max-width: 100px;
        }
        .copy-btn {
            background-color: #6c757d;
            font-size: 0.8rem;
            padding: 5px 10px;
            margin-left: 10px;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .toggle-qr {
            background-color: #28a745;
            font-size: 0.8rem;
            padding: 5px 10px;
            cursor: pointer;
        }
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>URL Shortener</h1>
            <p>Raccourcissez vos URLs en quelques clics</p>
        </header>

        <main>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="flash-messages">
                        {% for category, message in messages %}
                            <div class="flash-message {{ category }}">{{ message }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <div class="card">
                <h2>Raccourcir une URL</h2>
                <form method="POST" action="{{ url_for('index') }}">
                    <div class="form-group">
                        <label for="url">URL à raccourcir :</label>
                        <input type="url" id="url" name="url" placeholder="https://exemple.com" required>
                    </div>
                    <div class="form-group checkbox">
                        <input type="checkbox" id="generate_qr" name="generate_qr">
                        <label for="generate_qr">Générer un QR code</label>
                    </div>
                    <div class="form-group">
                        <button type="submit">Raccourcir</button>
                    </div>
                </form>
            </div>

            {% if result %}
            <div class="card result">
                <h2>URL Raccourcie</h2>
                <div class="result-group">
                    <label>URL originale :</label>
                    <p class="result-value"><a href="{{ result.original_url }}" target="_blank">{{ result.original_url }}</a></p>
                </div>
                <div class="result-group">
                    <label>URL raccourcie :</label>
                    <p class="result-value">
                        <a href="{{ result.short_url }}" target="_blank">{{ result.short_url }}</a>
                        <button class="copy-btn" onclick="copyToClipboard('{{ result.short_url }}')">Copier</button>
                    </p>
                </div>
                {% if result.qr_code %}
                <div class="qr-code">
                    <h3>QR Code</h3>
                    <img src="{{ result.qr_code }}" alt="QR Code">
                </div>
                {% endif %}
            </div>
            {% endif %}

            {% if recent_urls %}
            <div class="card recent-urls">
                <h2>URLs récentes</h2>
                {% for url in recent_urls %}
                <div class="url-item">
                    <div class="url-item-header">
                        <div>
                            <a href="{{ url_for('redirect_to_long_url', short_id=url.short_id) }}" target="_blank">
                                {{ url_for('redirect_to_long_url', short_id=url.short_id, _external=True) }}
                            </a>
                        </div>
                        <div>
                            Accès: {{ url.access_count }}
                            {% if url.qr_code %}
                            <button class="toggle-qr" onclick="toggleQR('qr-{{ url.short_id }}')">QR Code</button>
                            {% endif %}
                        </div>
                    </div>
                    {% if url.qr_code %}
                    <div id="qr-{{ url.short_id }}" class="mini-qr-code hidden">
                        <img src="{{ url.qr_code }}" alt="QR Code">
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </main>
    </div>

    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('URL copiée dans le presse-papier');
            }, function(err) {
                console.error('Erreur lors de la copie :', err);
            });
        }
        
        function toggleQR(id) {
            const qrElement = document.getElementById(id);
            if (qrElement.classList.contains('hidden')) {
                qrElement.classList.remove('hidden');
            } else {
                qrElement.classList.add('hidden');
            }
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    recent_urls = get_recent_urls()
    
    if request.method == 'POST':
        long_url = request.form.get('url')
        generate_qr = 'generate_qr' in request.form
        
        if not long_url:
            flash('Veuillez entrer une URL', 'error')
            return render_template_string(HTML_TEMPLATE, recent_urls=recent_urls)
            
        if not is_url_accessible(long_url):
            flash('L\'URL fournie est inaccessible', 'error')
            return render_template_string(HTML_TEMPLATE, recent_urls=recent_urls)
            
        short_id = generate_short_id()
        while True:
            with engine.connect() as conn:
                check = conn.execute(
                    urls.select().where(urls.c.short_id == short_id)
                ).first()
                if not check:
                    break
            short_id = generate_short_id()
            
        short_url = url_for('redirect_to_long_url', short_id=short_id, _external=True)
        
        qr_code_img = None
        if generate_qr:
            qr_code_img = generate_qr_code(short_url)
            
        try:
            store_url(short_id, long_url, qr_code_img)
            
            result = {
                'short_url': short_url,
                'original_url': long_url,
                'qr_code': qr_code_img if generate_qr else None
            }
            
        except Exception as e:
            flash(f'Erreur lors de l\'enregistrement: {str(e)}', 'error')
            
        recent_urls = get_recent_urls()
        
    return render_template_string(HTML_TEMPLATE, result=result, recent_urls=recent_urls)

@app.route('/api/shorten', methods=['POST'])
def api_shorten_url():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "URL non fournie"}), 400
    
    long_url = data['url']
    generate_qr = data.get('generate_qr', False)
    
    if not is_url_accessible(long_url):
        return jsonify({"error": "L'URL fournie est inaccessible"}), 400

    short_id = generate_short_id()
    while True:
        with engine.connect() as conn:
            result = conn.execute(
                urls.select().where(urls.c.short_id == short_id)
            ).first()
            if not result:
                break
        short_id = generate_short_id()

    short_url = url_for('redirect_to_long_url', short_id=short_id, _external=True)

    qr_code_img = None
    if generate_qr:
        qr_code_img = generate_qr_code(short_url)

    try:
        store_url(short_id, long_url, qr_code_img)
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'enregistrement: {str(e)}"}), 500

    response = {
        "short_url": short_url,
        "original_url": long_url
    }
    
    if generate_qr:
        response["qr_code"] = qr_code_img
    
    return jsonify(response), 201

@app.route('/api/info/<short_id>', methods=['GET'])
def api_url_info(short_id):
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
    long_url = get_url(short_id)
    if long_url:
        return redirect(long_url)
    else:
        flash('URL non trouvée', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
