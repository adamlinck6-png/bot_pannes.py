import os
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# --- CONFIGURATION (Identique à ton premier bot) ---
TOKEN_TELEGRAM = "8775180472:AAFqnrb-F7N69pz88xqV8OsELj1xN4Rs8oA"  # Remets le token de ton bot Telegram
CHAT_ID = "7518104464"            # Ton ID personnel

def envoyer_message_telegram(texte):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texte, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erreur envoi Telegram : {e}")

# --- DÉTECTEUR DE PANNES ---
def verifier_pannes():
    alertes = []
    
    # 1. Check Discord
    try:
        url_discord = "https://discordstatus.com/api/v2/summary.json"
        data_discord = requests.get(url_discord, timeout=5).json()
        statut_discord = data_discord["status"]["description"]
        if "All Systems Operational" not in statut_discord:
            alertes.append(f"🔴 **Discord est ralenti ou en panne !**\nStatut : {statut_discord}")
    except:
        print("Impossible de joindre le statut de Discord")

    # 2. Check YouTube
    try:
        url_youtube = "https://www.google.com/appsstatus/dashboard/summary.json"
        data_youtube = requests.get(url_youtube, timeout=5).json()
        for service in data_youtube.get("services", []):
            if service["name"] == "YouTube":
                if service["status"] != "AVAILABLE":
                    alertes.append("🔴 **YouTube rencontre des perturbations mondiales !**")
    except:
        print("Impossible de joindre le statut de YouTube")
        
    return alertes

# --- BOUCLE PRINCIPALE ---
def boucle_du_bot():
    print("🤖 Bot Tracker de Pannes démarré...")
    # Petit message au lancement pour être sûr que ça marche
    envoyer_message_telegram("🚀 **Le Bot Tracker de Pannes est actif et surveille le web !**")
    
    while True:
        try:
            print("Vérification de Discord et YouTube...")
            pannes = verifier_pannes()
            for alerte in pannes:
                envoyer_message_telegram(alerte)
        except Exception as e:
            print(f"Erreur boucle : {e}")
            
        # On vérifie toutes les 10 minutes (600 secondes) pour être réactif !
        time.sleep(600)

# --- SERVEUR WEB POUR RENDER ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot Pannes en ligne !")
        
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

def lancer_serveur_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServerHandler)
    print(f"🌍 Serveur web actif sur le port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Lancement du serveur web sur le thread principal
    t = Thread(target=boucle_du_bot)
    t.daemon = True
    t.start()
    
    lancer_serveur_web()