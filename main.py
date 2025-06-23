import requests
import selectorlib
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import ssl
import sqlite3


load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_FILE = os.path.join(SCRIPT_DIR, 'data.txt')

url = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


connection = sqlite3.connect(f'{SCRIPT_DIR}/web-scraper.db')


def scrape(url):
    '''Scrape the given URL and return the scraped data as a list of dictionaries.'''

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}")
    content = response.text
    return content


def extract_data(content):
    extractor = selectorlib.Extractor.from_yaml_file(f'{SCRIPT_DIR}/extract.yaml')
    value = extractor.extract(content)['tours']
    return value
    

def send_email(tour_info):
    print("Sending email...")

    host = "smtp.gmail.com"
    port = 465  # For SSL

    user_name = os.getenv("EMAIL_USERNAME")
    password = os.getenv("APP_EMAIL_KEY")

    if not user_name or not password:
        raise ValueError("Email credentials not found in .env file. Please check your .env file configuration.")

    context = ssl.create_default_context()

    msg = EmailMessage()
    msg['From'] = user_name
    msg['To'] = user_name
    msg['Subject'] = 'New Tour Available!'
    msg.set_content(tour_info)

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(user_name, password)
        server.send_message(msg)
    

def store(data):
    row = data.split(',')
    row = [item.strip() for item in row]
    band, city, date = row
    currsor = connection.cursor()
    currsor.execute("INSERT INTO events VALUES (?, ?, ?)", (band, city, date))
    connection.commit()
    print("Data stored successfully.")


def read_stored(extracted):
    cursor = connection.cursor()
    row = extracted.split(',')
    row = [item.strip() for item in row]
    band, city, date = row
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    result = cursor.fetchall()
    return result


if __name__ == "__main__":
    try:
        scraped = scrape(url)
        extracted = extract_data(scraped)

        if extracted != 'No upcoming tours' and not read_stored(extracted):
            store(extracted)
            send_email(extracted)
        
        print(extracted)
    except Exception as e:
        print(f"An error occurred: {e}")