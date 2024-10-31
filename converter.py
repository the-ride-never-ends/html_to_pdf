
import base64
import os
import tempfile

from bs4 import BeautifulSoup
from playwright.async_api import (
    async_playwright,
    Browser,
    Error as AsyncPlaywrightError,
    TimeoutError as AsyncPlaywrightTimeoutError
)

from utils.shared.decorators.try_except import try_except
from config.config import OUTPUT_FOLDER
from logger.logger import Logger
logger = Logger(logger_name=__name__)


class HTMLToPDFConverter:
    def __init__(self, docs_list_of_dicts):
        """
        Initialize the converter with directories and stylesheet paths.
        
        Args:
            input_dir (str): Directory containing HTML files
            pdf_filepath (str): Path for output PDF file
            stylesheet_paths (list): List of paths to CSS stylesheets
        """
        self.input_dir: str = docs_list_of_dicts['input_dir']
        self.html_filepaths: list[str] = docs_list_of_dicts["html_filepaths"]
        self.css_filepaths: list[str] = docs_list_of_dicts["css_filepaths"]
        self.pdf_filepath: str = docs_list_of_dicts["pdf_filepath"]
        self.final_soup = BeautifulSoup('<!DOCTYPE html><html><head></head><body></body></html>', 'html.parser')
        self.combined_html: list[BeautifulSoup] = []
        self.pdf_name = os.path.basename(self.pdf_filepath)
        self.scripts = []
        logger.debug("HTMLToPDFConverter class instantiated successfully.")

        # Add metadata to the final_soup attribute.
        self.add_metadata()

    def convert_html_to_pdf(self) -> None:
        """
        Orchestration function.
        """
        self.combine_html_files()
        self.combine_css_files()
        self.add_combined_html_to_final_soup()
        self.convert_final_soup_to_pdf()


    def process_svg_images(self, soup):
        """
        Process SVG images and convert them to data URLs.
        """
        for svg_img in soup.find_all('img', src=True):
            src: str = svg_img['src']
            if src.endswith('.svg'):
                try:
                    # Get the full path of the SVG file
                    svg_path = os.path.join(self.input_dir, src)
                    if os.path.exists(svg_path):
                        with open(svg_path, 'r', encoding='utf-8') as f:
                            svg_content = f.read()
                            # Convert SVG to data URL
                            svg_data = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                            svg_img['src'] = f'data:image/svg+xml;base64,{svg_data}'
                except Exception as e:
                    print(f"Error processing SVG {src}: {str(e)}")
        return soup

    def find_scripts(self, soup):
        """
        Collect MathJax and other scripts
        """
        scripts = soup.find_all('script')
        for script in scripts:
            script_str = str(script)
            if 'mathjax' in script_str.lower() or 'tex' in script_str.lower():
                if script_str not in self.scripts:
                    self.scripts.append(script_str)


    def add_metadata(self):
        """
        Add meta charset to final soup attribute.
        """
        meta_tag = self.final_soup.new_tag('meta')
        meta_tag['charset'] = 'UTF-8'
        self.final_soup.head.append(meta_tag)


    @try_except(exception=[FileNotFoundError, PermissionError], logger=logger, raise_exception=True)
    def combine_html_files(self) -> None:
        """
        Concatenate the contents of all HTML files into a single BeautifulSoup object with page breaks between files.
        """
        # Process each HTML file
        for html_filepath in self.html_filepaths:
            logger.debug(f"Reading in HTML from '{html_filepath}'...")
            with open(html_filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse HTML
            logger.debug("Parsing...")
            soup = BeautifulSoup(content, 'html.parser')

            # Get any SVG images that might be in the text.
            logger.debug("Getting SVG images...")
            soup = self.process_svg_images(soup)

            # Get any scripts that might be in there too.
            self.find_scripts(soup)
            
            # Remove existing stylesheet links
            logger.debug("Removing existing stylesheets...")
            for link in soup.find_all('link', rel='stylesheet'):
                link.decompose()
            
            # Extract body content
            logger.debug("Extracting body content...")
            body_content = soup.body.contents if soup.body else []
            self.combined_html.extend(body_content)
            
            # Add page break after each file except the last one
            logger.debug("Adding page breaks...")
            if html_filepath != self.html_filepaths[-1]:
                page_break = soup.new_tag('div')
                page_break['style'] = 'page-break-after: always;'
                self.combined_html.append(page_break)
        logger.debug("HTML combined successfully...")

    def add_scripts_to_final_soup(self):
        """
        Add collected scripts to final soup attribute.
        """
        for script in self.scripts:
            self.final_soup.head.append(BeautifulSoup(script, 'html.parser'))

    @try_except(exception=[FileNotFoundError, PermissionError], logger=logger, raise_exception=True)
    def combine_css_files(self) -> None:
        """
        Concatenate the contents of all CSS files into a single BeautifulSoup object.
        """
        # Add the scripts back in.
        self.add_scripts_to_final_soup()
        # Add stylesheets to head
        logger.debug("Combining CSS files...")
        for css_path in self.css_filepaths:
            with open(css_path, 'r', encoding='utf-8') as f:
                style_tag = self.final_soup.new_tag('style')
                style_tag.string = f.read()
                self.final_soup.head.append(style_tag)
        logger.debug("CSS combined successfully...")


    @try_except(logger=logger,  raise_exception=True)
    def add_combined_html_to_final_soup(self) -> None:
        logger.debug("Adding HTML to final soup...")
        self.final_soup.body.extend(self.combined_html)
        logger.debug("HTML added to final soup successfully...")


    @try_except(exception=[FileNotFoundError, PermissionError, 
                           AsyncPlaywrightError, AsyncPlaywrightTimeoutError], logger=logger, raise_exception=True)
    async def convert_final_soup_to_pdf(self) -> None:
        """
        Convert the final BeautifulSoup object to a PDF file.
        """
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write combined HTML to temporary file
            logger.debug("Writing final_soup to temprorary file...")
            temp_html = os.path.join(temp_dir, 'combined.html')
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(str(self.final_soup))

            pdf_html = os.path.join(OUTPUT_FOLDER, "combined.html")
            with open(pdf_html, 'w', encoding='utf-8') as f:
                f.write(str(self.final_soup))


            # Launch browser and create PDF
            async with async_playwright() as pw:
                logger.debug("Launching browser...")
                browser: Browser = await pw.chromium.launch(headless=False)
                logger.debug("Creating context...")
                context = await browser.new_context(viewport={'width': 1200, 'height': 800})
                logger.debug("Creating page...")
                page = await context.new_page()


                # Navigate to the temp HTML file
                logger.debug("Going to temp.html...")
                await page.goto(f'file://{temp_html}')
                
                # Wait for any LaTeX equations or other content to render
                miliseconds = 5000
                logger.debug(f"Waiting for {miliseconds} miliseconds...")
                await page.wait_for_timeout(miliseconds)
                
                # PDF options
                pdf_options = {
                    'path': self.pdf_filepath,
                    'format': 'Letter',
                    'margin': {
                        'top': '0.25in',
                        'right': '0.25in',
                        'bottom': '0.25in',
                        'left': '0.25in'
                    },
                    'print_background': True,
                    'prefer_css_page_size': True
                }
                
                # Generate PDF
                logger.debug(f"Generating PDF at {self.pdf_filepath}...")
                await page.pdf(**pdf_options)

                # Close page, context, and browser
                logger.debug(f"Closing page...")
                await page.close()
                logger.debug(f"Closing context...")
                await context.close()
                logger.debug(f"Closing browser...")
                await browser.close()