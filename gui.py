import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import threading
import os
import requests
from bs4 import BeautifulSoup
from lxml import html
import re
import pdfkit
from tqdm import tqdm
from PyPDF2 import PdfMerger
import time

# --- Config ---
WKHTMLTOPDF_PATH = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
BOOK_FOLDER = "books"
TEMP_HTML_FILE = "temp_book.html"
TIME_DELAY = 0.1

headers = {
    "User-Agent": "Mozilla/5.0"
}

toc = {
    'toc-header-text': 'Table of Contents',
}

options = {
    'page-width': '6in',
    'page-height': '9in',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'disable-smart-shrinking': ''
}

def extract_chapter_slugs_and_ids(url):
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    chapter_rows = tree.xpath('//table[@id="chapters"]/tbody/tr')
    chapters = []
    def chapter_title_to_slug(title):
        title = re.sub(r'\s*[-–—]\s*', '-', title)
        title = re.sub(r'[^\w\- ]', '', title)
        title = re.sub(r'\s+', '-', title)
        title = re.sub(r'-{2,}', '-', title)
        return title.strip('-')
    for row in chapter_rows:
        chapter_name = row.xpath('.//td[1]/a/text()')
        href = row.xpath('.//td[1]/a/@href')
        if chapter_name and href:
            match = re.search(r'/chapter/(\d+)', href[0])
            if match:
                chapter_id = match.group(1)
                chapter_slug = chapter_title_to_slug(chapter_name[0].strip())
                chapters.append((chapter_name[0].strip(), chapter_slug, chapter_id))
    return chapters

def extract_chapter_html(chapter_url):
    res = requests.get(chapter_url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")
    content_div = soup.select_one('div.chapter-inner.chapter-content')
    title = soup.select_one('h1')
    html_content = f"<h1>{title.text.strip()}</h1>\n" if title else ""
    html_content += str(content_div)
    return html_content

def save_chapters_to_pdf(book_url, book_name, selected_chapters, append_pdf_path=None, progress_callback=None):
    os.makedirs(BOOK_FOLDER, exist_ok=True)
    full_html = "<html><head><meta charset='UTF-8'></head><body>"
    for idx, (chapter_name, slug, chapter_id) in enumerate(selected_chapters):
        chapter_url = f'{book_url}/chapter/{chapter_id}/{slug}'
        try:
            chapter_html = extract_chapter_html(chapter_url)
            full_html += chapter_html + "<div style='page-break-after: always;'></div>"
        except Exception as e:
            if progress_callback:
                progress_callback(f"Failed to extract {chapter_url}: {e}")
        if progress_callback:
            progress_callback(f"Processed: {chapter_name}")
        time.sleep(TIME_DELAY)
    full_html += "</body></html>"
    temp_html_path = TEMP_HTML_FILE
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    output_pdf_path = os.path.join(BOOK_FOLDER, f"{book_name}.pdf")
    pdfkit.from_file(
        temp_html_path,
        output_pdf_path,
        configuration=config,
        options=options,
        toc=toc
    )
    os.remove(temp_html_path)
    if append_pdf_path:
        merger = PdfMerger()
        merger.append(append_pdf_path)
        merger.append(output_pdf_path)
        merged_path = os.path.join(BOOK_FOLDER, f"{book_name}_appended.pdf")
        merger.write(merged_path)
        merger.close()
        os.remove(output_pdf_path)
        os.rename(merged_path, output_pdf_path)
    return output_pdf_path

class RoyalPDFGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RoyalRoad PDF Downloader")
        # Set window and taskbar icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon-rr-downloader.png")
            icon_img = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon_img)
        except Exception as e:
            pass  # If icon fails to load, continue without it
        self.book_url_var = tk.StringVar()
        self.book_name_var = tk.StringVar()
        self.chapters = []
        self.selected_chapters = []
        self.append_pdf_path = None
        self.create_widgets()

    def create_widgets(self):
        # Set dark color scheme
        bg_color = "#222"
        fg_color = "#eee"
        entry_bg = "#333"
        entry_fg = "#fff"
        listbox_bg = "#222"
        listbox_fg = "#fff"
        text_bg = "#222"
        text_fg = "#fff"
        self.root.configure(bg=bg_color)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        frm = ttk.Frame(self.root, padding=10, style="Dark.TFrame")
        frm.grid(row=0, column=0, sticky="nsew")
        # Configure grid weights for scaling
        for i in range(6):
            frm.rowconfigure(i, weight=1 if i in (2, 5) else 0)
        for i in range(3):
            frm.columnconfigure(i, weight=3 if i == 1 else 1 if i == 0 else 0)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Dark.TFrame", background=bg_color)
        style.configure("Dark.TLabel", background=bg_color, foreground=fg_color)
        style.configure("Dark.TButton", background="#444", foreground=fg_color)
        ttk.Label(frm, text="Book URL:", style="Dark.TLabel").grid(row=0, column=0, sticky="w")
        url_entry = tk.Entry(frm, textvariable=self.book_url_var, width=60, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg, relief="sunken")
        url_entry.grid(row=0, column=1, sticky="ew")
        fetch_btn = tk.Button(frm, text="Fetch Chapters", command=self.fetch_chapters, bg="#d32f2f", fg="white", activebackground="#a62828", activeforeground="#fff")
        fetch_btn.grid(row=0, column=2, padx=5, sticky="ew")
        ttk.Label(frm, text="Book Name/PDF Name:", style="Dark.TLabel").grid(row=1, column=0, sticky="w")
        name_entry = tk.Entry(frm, textvariable=self.book_name_var, width=40, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg, relief="sunken")
        name_entry.grid(row=1, column=1, sticky="w")
        self.chapter_listbox = tk.Listbox(frm, selectmode=tk.MULTIPLE, width=60, height=20, bg=listbox_bg, fg=listbox_fg, selectbackground="#444", selectforeground="#fff", highlightbackground="#444", relief="sunken")
        self.chapter_listbox.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")
        btn_frame = ttk.Frame(frm, style="Dark.TFrame")
        btn_frame.grid(row=2, column=2, sticky="ns", pady=10)
        ttk.Button(btn_frame, text="Select All", command=self.select_all_chapters, style="Dark.TButton").pack(fill="x", pady=(0,2))
        ttk.Button(btn_frame, text="Deselect All", command=self.deselect_all_chapters, style="Dark.TButton").pack(fill="x")
        ttk.Button(frm, text="Append to Existing PDF", command=self.select_append_pdf, style="Dark.TButton").grid(row=3, column=0, pady=5)
        self.append_label = ttk.Label(frm, text="No PDF selected to append.", style="Dark.TLabel")
        self.append_label.grid(row=3, column=1, sticky="w")
        ttk.Button(frm, text="Download Selected Chapters", command=self.download_selected, style="Dark.TButton").grid(row=4, column=0, columnspan=3, pady=10)
        self.progress_text = tk.Text(frm, height=6, width=80, state='disabled', bg=text_bg, fg=text_fg, insertbackground=text_fg, relief="sunken")
        self.progress_text.grid(row=5, column=0, columnspan=3, pady=5, sticky="nsew")

    def fetch_chapters(self):
        url = self.book_url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a Book URL.")
            return
        self.chapter_listbox.delete(0, tk.END)
        self.chapters = []
        try:
            chapters = extract_chapter_slugs_and_ids(url)
            self.chapters = chapters
            for idx, (chapter_name, slug, chapter_id) in enumerate(chapters):
                self.chapter_listbox.insert(tk.END, f"{idx+1}. {chapter_name}")
            self.progress_message(f"Fetched {len(chapters)} chapters.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch chapters: {e}")

    def select_all_chapters(self):
        self.chapter_listbox.select_set(0, tk.END)

    def deselect_all_chapters(self):
        self.chapter_listbox.selection_clear(0, tk.END)

    def select_append_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF to append to",
            filetypes=[("PDF files", "*.pdf")]
        )
        if path:
            self.append_pdf_path = path
            self.append_label.config(text=f"Appending to: {os.path.basename(path)}")
        else:
            self.append_pdf_path = None
            self.append_label.config(text="No PDF selected to append.")

    def download_selected(self):
        selected_indices = self.chapter_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one chapter.")
            return
        book_url = self.book_url_var.get().strip()
        book_name = self.book_name_var.get().strip()
        if not book_url or not book_name:
            messagebox.showerror("Error", "Please enter both Book URL and Book Name.")
            return
        selected_chapters = [self.chapters[i] for i in selected_indices]
        threading.Thread(target=self._download_thread, args=(book_url, book_name, selected_chapters, self.append_pdf_path)).start()

    def _download_thread(self, book_url, book_name, selected_chapters, append_pdf_path):
        def progress_callback(msg):
            self.progress_message(msg)
        try:
            output_pdf = save_chapters_to_pdf(book_url, book_name, selected_chapters, append_pdf_path, progress_callback)
            self.progress_message(f"PDF created: {output_pdf}")
            messagebox.showinfo("Done", f"PDF created: {output_pdf}")
        except Exception as e:
            self.progress_message(f"Error: {e}")
            messagebox.showerror("Error", str(e))

    def progress_message(self, msg):
        self.progress_text.config(state='normal')
        self.progress_text.insert(tk.END, msg + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = RoyalPDFGUI(root)
    root.mainloop() 