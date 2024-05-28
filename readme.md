### README.md for RAGMiner.dev Open Source Version on Replit

# RAGMiner.dev - Open Source Version

Welcome to the open-source version of RAGMiner.dev! This project provides a FastAPI-based service that scrapes web pages, extracts relevant information, and formats the extracted content in various formats such as JSON, Markdown, CSV, XML, and TSV. The service also integrates with the Groq API to process and refine the extracted data.

## Features

- **Web Scraping:** Uses Selenium to scrape web pages.
- **Content Extraction:** Extracts information such as title, publication date, and content from web pages.
- **Content Formatting:** Formats the extracted content in JSON, Markdown, CSV, XML, and TSV.
- **Content Processing:** Integrates with the Groq API to refine and validate the extracted content.
- **Concurrency Support:** Supports multiple concurrent instances of Selenium.

## How to Use

### Step 1: Fork the Replit Project

1. Click the "Fork" button on the Replit project page to create your own copy of the project.

### Step 2: Set Up Environment Variables

1. In your Replit project, go to the "Secrets" tab (Environment Variables).
2. Add the following environment variables:

   - `GROQ_API_KEY`: Your Groq API key.
   - `SCRAPER_API_KEY`: Your Scraper API key.
   - `PROXY_HOST`: The proxy host address (e.g., `proxy-server.scraperapi.com`).
   - `PROXY_PORT`: The proxy port (e.g., `8001`).
   - `PROXY_USER`: The proxy username (e.g., `scraperapi`).
   - `PROXY_PASS`: The proxy password (e.g., your Scraper API key).
   - `USE_PROXY`: Set to `True` to use the proxy settings.

### Step 3: Run the Project

1. Click the "Run" button in Replit to start the FastAPI server.
2. The server will be accessible at `http://0.0.0.0:8000`.

## API Endpoints

### `/scrape/{format}/{url:path}`

- **Method:** `GET`
- **Description:** Scrapes the specified URL and returns the content in the specified format.
- **Parameters:**
  - `format`: The format of the output (json, markdown, csv, xml, tsv).
  - `url`: The URL of the web page to scrape.
- **Response:** The extracted content in the specified format.

### `/extract/{url:path}`

- **Method:** `POST`
- **Description:** Scrapes the specified URL, extracts the specified information, processes the content using the Groq API, and returns the refined content.
- **Request Body:** A JSON object specifying the information to extract.
- **Parameters:**
  - `url`: The URL of the web page to scrape.
- **Response:** The refined content in JSON format.

## Example Usage

### `/scrape` Endpoint

```sh
curl -X GET "http://0.0.0.0:8000/scrape/json/https://example.com"
```

### `/extract` Endpoint

```sh
curl -X POST "http://0.0.0.0:8000/extract/https://example.com" \
     -H "Content-Type: application/json" \
     -d '{
           "product_name": "Product Name",
           "price": "Price",
           "ratings": "Ratings"
         }'
```

## Example Python Test Script

Save the following script as `test_extract.py` and run it to test the `/extract` endpoint:

```python
import requests

# Define the URL to scrape
url = "https://www.amazon.com/Recreational-Trampolines-Trampoline-Guaranteed-Galvanized/dp/B08X2R2CLH"

# Define the JSON object for extraction
json_data = {
    "product_name": "Product Name",
    "price": "Price",
    "ratings": "Ratings"
}

# Define the endpoint
endpoint = f"http://0.0.0.0:8000/extract/{url}"

# Execute the POST request
response = requests.post(endpoint, json=json_data, headers={"Content-Type": "application/json"})

# Print the response
print(response.status_code)
print(response.json())
```

Run the script using the following command:

```sh
python test_extract.py
```

This script sends a POST request to the `/extract` endpoint with the specified URL and JSON object in the request body, then prints the response from the server.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Feel free to reach out if you have any questions or need further assistance! Enjoy using RAGMiner.dev Open Source Version!