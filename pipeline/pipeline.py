import requests
import time
import os
import logging
from etl import etl

API_URL = "http://telebot:8001/etl/"
GITHUB_REPO = "MoH-Malaysia/data-darah-public"
LAST_SEEN_COMMIT = "last_seen_commit.txt"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_commit():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"
    try:
        response = requests.get(url)
        commits = response.json()
        return commits[0]['sha'] if commits else None
    except requests.RequestException as e:
        logging.error(f"Error fetching latest commit: {e}")
        return None

def has_new_commit(latest_commit):
    if not os.path.exists(LAST_SEEN_COMMIT):
        return True

    with open(LAST_SEEN_COMMIT, 'r') as file:
        last_seen = file.read().strip()
        return last_seen != latest_commit

def update_last_seen_commit(commit):
    with open(LAST_SEEN_COMMIT, 'w') as file:
        file.write(commit)

def collect_data():
    while True:
        latest_commit = get_latest_commit()
        if latest_commit and has_new_commit(latest_commit):
            update_last_seen_commit(latest_commit)
            donate_fac, donate_state, new_donors_fac, new_donors_state = etl()
            message = "New commit found. Triggering ETL process."
            return message, donate_fac, donate_state, new_donors_fac, new_donors_state
        else:
            return "No new commits. Checking again later.", None, None, None, None 

def send_data_to_bot(message, donate_fac, donate_state, new_donors_fac, new_donors_state, max_retries=5, delay=5):
    for attempt in range(max_retries):
        try:
            payload = {
                "message": message,
                "donate_fac": donate_fac,
                "donate_state": donate_state,
                "new_donors_fac": new_donors_fac,
                "new_donors_state": new_donors_state}
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                logging.info("Message from pipeline sent successfully")
                return
            else:
                logging.error(f"Failed to send message, status code {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds...")

        time.sleep(delay)

    logging.error("Failed to connect to the Telegram bot service.")

if __name__ == "__main__":
    message, donate_fac, donate_state, new_donors_fac, new_donors_state = collect_data()
    send_data_to_bot(message, donate_fac, donate_state, new_donors_fac, new_donors_state)
