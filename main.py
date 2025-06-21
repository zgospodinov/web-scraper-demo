import requests
import selectorlib
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_FILE = os.path.join(SCRIPT_DIR, 'data.txt')

url = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def scrape(url):
    '''Scrape the given URL and return the scraped data as a list of dictionaries.'''

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}")
    # extractor = selectorlib.Extractor.from_yaml_file('selectors.yml')
    content = response.text
    return content


def extract_data(content):
    extractor = selectorlib.Extractor.from_yaml_file(f'{SCRIPT_DIR}/extract.yaml')
    value = extractor.extract(content)['tours']
    return value
    

def send_email():
    print("Sending email... (This function is not implemented yet)")
    

def store(data, filename=STORAGE_FILE):
    '''Append the given data to the specified file.'''
    with open(filename, "a", encoding="utf-8") as file:
        file.write(data + "\n")
    print("Data stored successfully.")


def read_stored():
    with open(STORAGE_FILE, 'r') as file:
        return file.read().strip()


if __name__ == "__main__":
    try:
        scraped = scrape(url)
        extracted = extract_data(scraped)
        
        stored_data = read_stored()
        if extracted != 'No upcoming tours' and extracted not in stored_data:
            store(extracted)
            send_email()
        
        print(extracted)
    except Exception as e:
        print(f"An error occurred: {e}")