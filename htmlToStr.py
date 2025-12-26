import requests
from bs4 import BeautifulSoup

def dump_url_content(url):
    try:
        # Fetch the content of the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)

        return response.text
        #return text_content

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"

if __name__ == "__main__":
    url = input("Enter a URL: ")
    content = dump_url_content(url)
    p = open("cont.txt", 'w+')
    print("\n--- Dumped Content ---\n")
    print(content)
    p.write(content)
    p.close
