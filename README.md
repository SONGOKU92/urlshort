# Raccourcisseur d'URLs & Générateur de QR Code

Ce projet est une application API développée avec Flask qui permet de raccourcir des URL et de générer des QR codes associés. L'application utilise une base de données SQLite pour stocker les URL raccourcies et leurs informations associées.

## Fonctionnalités

- **Raccourcissement d'URL :** Génère un identifiant court unique pour une URL longue.
- **Génération de QR Code :** Optionnellement, crée un QR code pour l'URL raccourcie.
- **Redirection :** Redirige l'utilisateur de l'URL raccourcie vers l'URL d'origine.
- **Statistiques :** Suivi du nombre d'accès, date de création et de dernier accès d'une URL.

## Prérequis

- **Python 3.6** ou version ultérieure
- Les dépendances listées dans le fichier [requirements.txt](requirements.txt) :
  - Flask
  - SQLAlchemy
  - requests
  - qrcode
  - Pillow
  - urllib3

pip install -r requirements.txt

python app.py

L'application sera accessible à l'adresse : http://127.0.0.1:5000
