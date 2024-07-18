from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

app = Flask(__name__)

# MySQL configuration
db_config = {
    'user': 'root',
    'password': 'Rugma@2001',
    'host': 'localhost',
    'database': 'entities_db'
}

# Function to extract data using Selenium
def extract_entities(url):
    driver = webdriver.Chrome()  
    driver.get(url)

    # Example XPaths, modify these based on the actual structure of the target page
    artist_name = driver.find_element(By.XPATH, 'xpath_to_artist_name').text
    program_name = driver.find_element(By.XPATH, 'xpath_to_program_name').text
    artist_role = driver.find_element(By.XPATH, 'xpath_to_artist_role').text
    date = driver.find_element(By.XPATH, 'xpath_to_date').text
    time = driver.find_element(By.XPATH, 'xpath_to_time').text
    auditorium = driver.find_element(By.XPATH, 'xpath_to_auditorium').text

    driver.quit()

    return {
        'artist_name': artist_name,
        'program_name': program_name,
        'artist_role': artist_role,
        'date': date,
        'time': time,
        'auditorium': auditorium,
        'url': url
    }

#  entities to the MySQL database
def save_entities_to_db(entities):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO EntitiesMaster (artist_name, program_name, artist_role, date, time, auditorium, url)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (entities['artist_name'], entities['program_name'], entities['artist_role'], entities['date'], entities['time'], entities['auditorium'], entities['url']))
    conn.commit()

    cursor.close()
    conn.close()

# Root route for testing
@app.route('/')
def home():
    return 'Flask app is running!'

# save entities
@app.route('/api/save-entity', methods=['GET'])
def save_entity():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    entities = extract_entities(url)
    save_entities_to_db(entities)

    return jsonify({'message': 'Entities saved successfully'})

# entities from the MySQL database
def get_entities_from_db(url):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    select_query = """
    SELECT * FROM EntitiesMaster WHERE url = %s
    """
    cursor.execute(select_query, (url,))
    entities = cursor.fetchall()

    cursor.close()
    conn.close()

    return entities

# route to retrieve entities
@app.route('/api/get-entity', methods=['GET'])
def get_entity():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    entities = get_entities_from_db(url)
    return jsonify(entities)

if __name__ == '__main__':
    app.run(debug=True)
