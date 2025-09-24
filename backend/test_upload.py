import requests

# Backend URL
API_URL = "http://127.0.0.1:8000"

def test_upload():
    # First, login to get the auth token
    login_data = {
        "email": "testadmin@gmail.com",  # Replace with your actual email
        "password": "fk9lratv"         # Replace with your actual password
    }
    
    # Login to get token
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        return
    
    token = login_response.json()["access_token"]
    
    # Now upload the PDF
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Replace with path to a test PDF file
    pdf_path = "test.pdf"
    
    with open(pdf_path, "rb") as f:
        files = {
            "file": ("test.pdf", f, "application/pdf")
        }
        response = requests.post(
            f"{API_URL}/upload/waiver",
            headers=headers,
            files=files
        )
    
    print("Status Code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_upload()