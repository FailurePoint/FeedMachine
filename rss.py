import requests
import re
import os
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.firefox.options import Options  # Use headless browsing
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# OpenRouter API setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=open("configs/openrouter.key", 'r').read()
)

def fetch_full_page_html(url, use_selenium=False, retries=3, timeout=10):
    """Fetch the HTML source code of a web page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Use Selenium for JavaScript-rendered pages
    if use_selenium:
        options = Options()
        options.headless = True  
        driver = webdriver.Firefox(options=options)

        attempt = 0
        while attempt < retries:
            try:
                driver.get(url)
                # Wait for the page to load completely (adjust to your need)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                html_source = driver.page_source 
                driver.quit()
                return html_source
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                attempt += 1
                time.sleep(2)  # Wait before retrying
        driver.quit()
        print("Failed to fetch the page after multiple retries.")
        return None
    else:
        # Use requests for non-JavaScript pages
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        html_source = response.text
        return html_source

def query_openrouter(prompt, html_content):
    """Send the HTML content and prompt to OpenRouter."""
    try:
        completion = client.chat.completions.create(
            extra_headers={
            # None
            },
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {"role": "system", "content": "You are an AI that processes web page content."},
                {"role": "user", "content": f"Here is the entire HTML of a web page:\n\n{html_content}\n\n{prompt}"}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    

def update_xml(response, file_path="output.xml"):
    """
    Extracts the content between ```xml and ``` from the response and saves it to a specified file path.
    
    Args:
        response (str): The response text from OpenRouter.
        file_path (str): The absolute path where the extracted XML should be saved.
    
    Returns:
        bool: True if XML was successfully extracted and saved, False otherwise.
    """
    match = re.search(r"```xml\n(.*?)\n```", response, re.DOTALL)
    
    if match:
        xml_content = match.group(1)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(xml_content)
        
        print(f" XML content saved to {file_path}")
        return True
    else:
        print(f"No XML content found in the response: {response}")
        return False

