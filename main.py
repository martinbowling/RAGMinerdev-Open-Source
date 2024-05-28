from fastapi import FastAPI, Response, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import asyncio
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import html2text
import csv
import xml.etree.ElementTree as ET
import uvicorn
import os
from bs4 import BeautifulSoup
import json
import io
from readability import Document
from groq import AsyncGroq
from typing import List
import re

app = FastAPI()

client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

# Scraper API Settings
SCRAPER_API_KEY = os.environ['SCRAPER_API_KEY']

# Read proxy settings from environment variables
PROXY_HOST = os.getenv('PROXY_HOST', 'proxy-server.scraperapi.com')
PROXY_PORT = os.getenv('PROXY_PORT', '8001')
PROXY_USER = os.getenv('PROXY_USER', 'scraperapi')
PROXY_PASS = os.getenv('PROXY_PASS', os.getenv('SCRAPER_API_KEY'))
USE_PROXY = os.getenv('USE_PROXY', 'True').lower() in ['true', '1', 't', 'yes']


def selenium_task(url: str) -> str:
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if USE_PROXY:
        proxy = f"{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        options.add_argument(f'--proxy-server=http://{proxy}')

    try:
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        page_source = driver.page_source

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        driver.quit()

    return page_source


def extract_information(html_content: str,
                        url: str,
                        send_full_content: bool = False) -> dict:
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title
    title = soup.title.string if soup.title else "No title found"

    # Extract publication date
    publication_date = "No publication date found"
    date_meta = soup.find('meta', {'property': 'article:published_time'})
    if date_meta and 'content' in date_meta.attrs:
        publication_date = date_meta['content']
    else:
        date_meta = soup.find('meta', {'name': 'pubdate'})
        if date_meta and 'content' in date_meta.attrs:
            publication_date = date_meta['content']

    # Convert full HTML to Markdown
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    full_markdown_content = markdown_converter.handle(html_content)

    # Extract readable content using readability
    document = Document(html_content)
    readable_html = document.summary()

    # Convert readable HTML to Markdown
    readable_markdown_content = markdown_converter.handle(readable_html)

    result = {}

    if send_full_content:

        # Create the result JSON object
        result = {
            "url": url,
            "title": title,
            "publication_date": publication_date,
            "content": full_markdown_content,
        }
    else:
        # Create the result JSON object
        result = {
            "url": url,
            "title": title,
            "publication_date": publication_date,
            "content": readable_markdown_content,
        }

    return result


# Utility functions for conversion
def parse_string_to_json(data: dict) -> dict:
    return data


def parse_string_to_csv(data: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(data.keys())
    writer.writerow(data.values())
    return output.getvalue()


def parse_string_to_xml(data: dict) -> str:
    root = ET.Element('ragData')
    for key, value in data.items():
        child = ET.SubElement(root, key)
        child.text = str(value)
    return ET.tostring(root, encoding='unicode')


def parse_string_to_tsv(data: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(data.keys())
    writer.writerow(data.values())
    return output.getvalue()


def parse_string_to_markdown(data: dict) -> str:
    markdown_content = ""
    for key, value in data.items():
        markdown_content += f"{key}: {value}\n\n"
    return markdown_content


@app.get("/scrape/{format}/{url:path}")
async def process_webpage_scrape(format: str, url: str):

    if format not in ["json", "markdown", "csv", "xml", "tsv"]:
        return JSONResponse(status_code=400,
                            content={"message": "Invalid format"})

    try:
        page_source = await asyncio.to_thread(selenium_task, url)
        extracted_info = extract_information(page_source, url)

        if format == "json":
            result = parse_string_to_json(extracted_info)
            return JSONResponse(content=result)
        elif format == "markdown":
            result = parse_string_to_markdown(extracted_info)
            return PlainTextResponse(content=result)
        elif format == "csv":
            result = parse_string_to_csv(extracted_info)
            return PlainTextResponse(content=result)
        elif format == "xml":
            result = parse_string_to_xml(extracted_info)
            return PlainTextResponse(content=result)
        elif format == "tsv":
            result = parse_string_to_tsv(extracted_info)
            return PlainTextResponse(content=result)

    except Exception as e:
        print(f"Error processing scrape: {e}")
        return JSONResponse(status_code=500,
                            content={"message": "Error processing scrape"})


def split_markdown_content(markdown_content: str,
                           chunk_size: int = 20000) -> List[str]:
    return [
        markdown_content[i:i + chunk_size]
        for i in range(0, len(markdown_content), chunk_size)
    ]


async def process_chunk(chunk: str, json_string: str, previous_response: str):
    previous_prompt = ""
    if previous_response:
        previous_prompt = f"""You have previously given me the following information: 
        <previous_information>
        {previous_response}
        </previous_information>
        you only need to extract information that is missing from the original information. Do not change any of the information that you have already given, only add new information that is missing."""

    prompt_template = f"""You will be given some content to extract information from, as well as a JSON object specifying what information needs to be extracted from that content. Your task is to extract the requested information and return it in JSON format.

    Here is the content to extract information from:
    <content>
    {chunk}
    </content>

    Here is the JSON object specifying what information to extract:
    <json_object>
    {json_string}
    </json_object>

    {previous_prompt}
    
    Please carefully study the provided JSON object to understand exactly what pieces of information need to be extracted. The JSON object will contain keys specifying the desired information, and the values will indicate what that information should be called in the output.

    Once you have a clear understanding of what needs to be extracted, carefully go through the provided content and pull out all of the requested information. Pay close attention to the content to make sure you are extracting the information accurately and completely.

    After you have finished extracting all of the necessary information from the content, please return the extracted data in valid JSON format inside a code block with ```json tags like this:

    ```json
    {{
      "key1": "value1",
      "key2": "value2"
    }}
    Do not include any text before or after the code block, and make sure the JSON is properly formatted with quoted keys and values. Please return ONLY the JSON code block, without any additional explanation or commentary."""

    response = await client.chat.completions.create(model="llama3-70b-8192",
                                                    messages=[{
                                                        "role":
                                                        "user",
                                                        "content":
                                                        prompt_template
                                                    }],
                                                    max_tokens=1000,
                                                    temperature=1.2)
    groq_json = response.choices[0].message.content
    return groq_json


async def process_markdown_content(markdown_content: str, json_string: str):
    chunks = split_markdown_content(markdown_content)

    response = ""
    for chunk in chunks:
        response = await process_chunk(chunk, json_string, response)
        print(response)
        prompt = f"Given this response: {response},does it contain all the infomation requested in the JSON object? {json_string}. Respond simply with yes or no"
        complete_check = await client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=1000,
            temperature=0)
        is_complete = complete_check.choices[0].message.content.strip().lower()
        if is_complete == "yes":
            return extract_json_from_response(response)


def extract_json_from_response(response: str) -> str:
    match = re.search(r'```json(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response


@app.post("/extract/{url:path}")
async def scrape_and_extract(url: str, request: Request):
    try:
        json_object = await request.json()
        json_string = json.dumps(json_object)
        page_source = await asyncio.to_thread(selenium_task, url)
        extracted_info = extract_information(page_source, url, True)
        markdown_content = parse_string_to_markdown(extracted_info)

        combined_response = await process_markdown_content(
            markdown_content, json_string)

        groq_json = combined_response
        return JSONResponse(content=groq_json)
    except Exception as e:
        print(f"Error processing scrape and extract: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Error processing scrape and extract"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
