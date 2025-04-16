# Royal Road to PDF

This script allows you to scrape chapters from a Royal Road story and convert them into a single PDF. The script fetches the chapter content, formats it into HTML, and then uses the `wkhtmltopdf` tool to convert the HTML into a PDF document.

## Requirements

Before you can use this script, you'll need to install the necessary dependencies and set up the `wkhtmltopdf` tool for the HTML to PDF conversion.

### 1. Python 3.6+ and Pip
Make sure you have Python 3.6 or higher installed. You can check your version with:

```bash
python --version
```

You can download Python from [python.org](https://www.python.org/downloads/).

### 2. Install Python Dependencies
You can install the required Python dependencies by using `pip`. First, create and activate a virtual environment (optional but recommended):

```bash
# Create a virtual environment (optional)
python -m venv royalvenv

# Activate the virtual environment
# On Windows:
royalvenv\Scriptsctivate
# On macOS/Linux:
source royalvenv/bin/activate
```

Now install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Install `wkhtmltopdf`

The script uses `wkhtmltopdf` to convert the HTML content to PDF. You can download it from the official website:

- [Download wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

Make sure to download the version compatible with your operating system.

#### Windows:
For Windows, you can download the installer and install it. After installation, ensure the path to `wkhtmltopdf` is added to your system's environment variables. Alternatively, you can specify the path to the executable in the script:

```python
config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
```

#### macOS:
You can install `wkhtmltopdf` using Homebrew:

```bash
brew install wkhtmltopdf
```

#### Linux:
You can install it via your package manager, for example on Ubuntu:

```bash
sudo apt install wkhtmltopdf
```

### 4. Set Up the Script

1. Clone the repository or download the script files.
2. Edit the script to specify the URL of the Royal Road story you want to convert.

```python
BOOK_URL = "https://www.royalroad.com/fiction/21220/mother-of-learning"
```

3. Run the script using the command:

```bash
python royal-pdf.py
```

The script will fetch the chapters from the specified URL, extract the chapter names and content, and generate a PDF named `Mother_of_Learning.pdf`.

## Usage

1. **Run the Script:**

   To generate the PDF for a Royal Road story, simply run the script:

   ```bash
   python royal-pdf.py
   ```

2. **Error Handling:**
   The script will log any errors it encounters during the scraping or conversion process. If a chapter fails to download, the script will continue with the next chapter.

3. **Output:**
   After the script runs, you should have a file named `Mother_of_Learning.pdf` in your directory. This is the compiled PDF of the entire story.

## Notes

- Ensure that your network connection is stable as the script will need to download the HTML content for each chapter.
- You can modify the script to change the output PDF name or add additional formatting to the HTML before conversion.
- The script uses a `time.sleep(0.5)` to avoid hitting the server too quickly, but you can adjust this interval if necessary.

## License

This script is open-source and free to use for personal projects. Please ensure you comply with Royal Road's terms of service when scraping their content.

---

Happy reading! Enjoy the Royal Road to PDF script. Let me know if you encounter any issues or have suggestions for improvements.

