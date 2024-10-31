import asyncio
import os
import sys



from converter import HTMLToPDFConverter
from utils.choose_folders_with_html_files_to_convert import choose_folders_with_html_files_to_convert
from utils.shared.next_step import next_step

from config.config import INPUT_FOLDER, OUTPUT_FOLDER
from logger.logger import Logger
logger = Logger(logger_name=__name__)


async def main():

    next_step(f"Step 1. Choose HTML files to convert in directory: {INPUT_FOLDER}")
    docs_list_of_dicts = choose_folders_with_html_files_to_convert(INPUT_FOLDER, OUTPUT_FOLDER, logger=logger)

    next_step(f"Step 2. Instantiate HTMLToPDFConverter class.")

    pdfs = []
    for dic in docs_list_of_dicts:
        # We instantiate the class every time to avoid subsequent iterations 
        # using the same html_filepaths and css_filepaths as the previous one.
        converter = HTMLToPDFConverter(dic)

        next_step(f"Step 3. Combine HTML files into one.")
        converter.combine_html_files()

        next_step(f"Step 4. Combine CSS files into one.")
        converter.combine_css_files()

        next_step(f"Step 5. Add combined HTML to combined CSS file")
        converter.add_combined_html_to_final_soup()

        next_step(f"Step 6. Save combined file to PDF")
        await converter.convert_final_soup_to_pdf()

        print(f"Successfully created PDF: {converter.pdf_name}")
        pdfs.append(dic)

    if pdfs:
        print(f"Successfully created {len(pdfs)} PDFs")
    else:
        print("No pdfs were created.")

    sys.exit(0)


if __name__ == "__main__":
    import os
    base_name = os.path.basename(__file__) 
    program_name = os.path.split(os.path.split(__file__)[0])[1] if base_name != "main.py" else os.path.splitext(base_name)[0] 
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"'{program_name}' program stopped.")


