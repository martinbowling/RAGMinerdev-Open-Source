import requests

# Define the URL to scrape
url = "https://www.amazon.com/Recreational-Trampolines-Trampoline-Guaranteed-Galvanized/dp/B08X2R2CLH/?_encoding=UTF8&pd_rd_w=n7OJK&content-id=amzn1.sym.a725c7b8-b047-4210-9584-5391d2d91b93%3Aamzn1.symc.d10b1e54-47e4-4b2a-b42d-92fe6ebbe579&pf_rd_p=a725c7b8-b047-4210-9584-5391d2d91b93&pf_rd_r=20KXDTW6RAQSW6JPEFG8&pd_rd_wg=pu8MP&pd_rd_r=ccb404aa-c58d-405e-9eac-3c6631bf8a29&ref_=pd_hp_d_atf_ci_mcx_mr_hp_atf_m&th=1"

# Define the JSON object for extraction
json_data = {
    "product_name": "Product Name",
    "price": "Price",
    "ratings": "Ratings",
    "sentiment": "The overall sentiment of the product based on user reviews",
    "synopsis": "A brief summary of the product"
}

# Define the endpoint
endpoint = f"http://0.0.0.0:8000/extract/{url}"

# Execute the POST request
response = requests.post(endpoint,
                         json=json_data,
                         headers={"Content-Type": "application/json"})

# Print the response
print(response.status_code)
print(response.json())
