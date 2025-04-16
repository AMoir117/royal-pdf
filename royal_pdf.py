import requests
from bs4 import BeautifulSoup
import pdfkit
import time
from lxml import html
import re

BASE_URL = "https://www.royalroad.com"
BOOK_URL = "https://www.royalroad.com/fiction/21220/mother-of-learning"
BOOK_NAME = "Mother_of_Learning"
BOOK_FOLDER = "books"

headers = {
	"User-Agent": "Mozilla/5.0"
}




def extract_chapter_slugs_and_ids(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    tree = html.fromstring(response.content)

    # XPath to select all chapter rows in the table of contents
    chapter_rows = tree.xpath('//table[@id="chapters"]/tbody/tr')

    chapters = []

    def chapter_title_to_slug(title):
        # Replace ' - ' or em-dash/en-dash with a hyphen
        title = re.sub(r'\s*[-–—]\s*', '-', title)
        # Remove characters not allowed in slugs (keep alphanumerics and hyphens)
        title = re.sub(r'[^\w\- ]', '', title)
        # Replace all whitespace with hyphens
        title = re.sub(r'\s+', '-', title)
        # Collapse multiple hyphens
        title = re.sub(r'-{2,}', '-', title)
        # Strip leading/trailing hyphens
        return title.strip('-')

    for row in chapter_rows:
        # Extract the chapter name and link
        chapter_name = row.xpath('.//td[1]/a/text()')
        href = row.xpath('.//td[1]/a/@href')

        if chapter_name and href:
            # Extract chapter ID from the href link
            match = re.search(r'/chapter/(\d+)', href[0])
            if match:
                chapter_id = match.group(1)
                # Append the tuple (slug, chapter_id)
                chapter_slug = chapter_title_to_slug(chapter_name[0].strip())
                chapters.append((chapter_slug, chapter_id))

    return chapters




# Function to extract the HTML content of each chapter
def extract_chapter_html(chapter_url):
    print(f"Extracting {chapter_url}")
    res = requests.get(chapter_url, headers=headers)
    res.raise_for_status()  # Ensure we notice bad responses
    soup = BeautifulSoup(res.text, "lxml")

    # Extract chapter content
    content_div = soup.select_one('div.chapter-inner.chapter-content')
    title = soup.select_one('h1')  # Optional, add title per chapter

    html = f"<h1>{title.text.strip()}</h1>\n" if title else ""
    html += str(content_div)

    return html


# Main function to process all chapters and generate a PDF
def main():
    chapters = extract_chapter_slugs_and_ids(BOOK_URL)

    full_html = "<html><head><meta charset='UTF-8'></head><body>"
    
    for slug, chapter_id in chapters:
        chapter_url = f'{BOOK_URL}/chapter/{chapter_id}/{slug}'
        try:
            chapter_html = extract_chapter_html(chapter_url)
            full_html += chapter_html + "<div style='page-break-after: always;'></div>"
        except Exception as e:
            print(f"Failed to extract {chapter_url}: {e}")
        time.sleep(0.5)  # Add delay to prevent overwhelming the server

    full_html += "</body></html>"

    # Save the HTML content to a file
    # with open("book.html", "w", encoding="utf-8") as f:
    #     f.write(full_html)

    # Convert HTML to PDF
    config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")  # Adjust path if needed
    # pdfkit.from_file("book.html", "books/Mother_of_Learning.pdf", configuration=config)
    pdfkit.from_string(full_html, f"{BOOK_FOLDER}/{BOOK_NAME}.pdf", configuration=config)
    print(f"PDF created: {BOOK_NAME}.pdf")


if __name__ == "__main__":
    main()	
