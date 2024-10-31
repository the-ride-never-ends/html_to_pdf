import os
from pathlib import Path

def choose_folders_with_html_files_to_convert(input_folder: str, output_folder: str, logger=None) -> list[dict]:
    """
    Import HTML and CSS files from specified folders and their subfolders.
    
    Args:
        input_folder (str): Root directory to search for HTML/CSS files
        logger (Optional[logging.Logger]): Logger instance for debugging
    
    Returns:
        List[Dict[str, List[str]]]: List of dictionaries containing:
            - dir_name: Name of the directory
            - html_files: List of HTML files (excluding those starting with '_')
            - css_files: List of CSS/SCSS files (excluding those starting with '_')
    
    Raises:
        FileNotFoundError: If input_folder doesn't exist
        PermissionError: If there's no read access to directories
    """
    assert logger
    # Convert to Path object for better path handling
    input_path = Path(input_folder)
    
    # Validate input folder
    if not input_path.exists():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")
    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_folder}")

    # Get all document folders
    try:
        documents_folders = [
            f.name for f in input_path.iterdir() 
            if f.is_dir() and not f.name.startswith('.')
        ]
    except PermissionError as e:
        if logger:
            logger.error(f"Permission denied accessing {input_folder}: {e}")
        raise
    
    if not documents_folders:
        if logger:
            logger.warning(f"No subdirectories found in {input_folder}")
        return []

    # Display available folders
    available_list = "\n".join(f"- {folder}" for folder in sorted(documents_folders))
    separator = "*" * 20
    print(f"{separator}\nAvailable Folders:\n{available_list}\n{separator}")

    # Get user input and validate
    while True:
        chosen_input = input("\nEnter folder names to convert (comma-separated): ").strip()
        if not chosen_input:
            print("No folders selected. Please try again.")
            continue
            
        chosen_documents = [doc.strip() for doc in chosen_input.split(',')]
        invalid_folders = [doc for doc in chosen_documents if doc not in documents_folders]
        
        if invalid_folders:
            print(f"Invalid folder(s): {', '.join(invalid_folders)}\nPlease try again.")
            continue
        break

    # Process chosen directories
    docs_list_of_dicts = []
    for chosen_dir in chosen_documents:
        dir_path = input_path / chosen_dir
        try:
            # Get files with proper extensions, excluding those starting with '_'
            html_filepaths = [
                f for f in dir_path.glob('**/*.html')
                if not f.name.startswith('_')
            ]
            scss_filepaths = [
                f for f in dir_path.glob('**/*.scss')
                if not f.name.startswith('_')
            ]
            css_filepaths = [
                f for f in dir_path.glob('**/*.css')
                if not f.name.startswith('_')
            ]
            css_filepaths.extend(scss_filepaths)

            dir_dict = {
                'input_dir': str(dir_path),
                'pdf_filepath': os.path.join(output_folder, os.path.split(dir_path)[-1] + '.pdf'),
                'html_filepaths': sorted(html_filepaths),
                'css_filepaths': sorted(css_filepaths)  
            }

            logger.info(f"Processing directory: {chosen_dir}")
            logger.info(f"Found files: {dir_dict}")
            
            docs_list_of_dicts.append(dir_dict)
            
        except PermissionError as e:
            logger.error(f"Permission denied accessing {dir_path}: {e}")
            print(f"Warning: Could not access {chosen_dir}")
            continue

    logger.info(f"Found {len(docs_list_of_dicts)} documents.")
    return docs_list_of_dicts




















    # assert logger
    # # Get all the document folders from the input folder.
    # try:
    #     documents_folders = [
    #         f for f in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, f))
    #     ]
    # except PermissionError as e:
    #     logger.error(f"Permission denied accessing {input_folder}: {e}")
    #     raise e

    # available_list = "\n".join(f"- {folder}" for folder in sorted(documents_folders))
    # format_asterisks = '*' * 20
    # print("***Available Files***\n", 
    #       available_list,
    #       format_asterisks,
    # )
    # chosen_documents = input("Enter the folders you want to convert to pdf(comma-separated): ").split(',')
    # chosen_documents = [os.path.join(input_folder, document.strip()) for document in chosen_documents]

    # # Walk through each directory and its subdirectories to find their HTML and CSS files.
    # docs_list_of_dicts = []
    # for pdf_dirs in chosen_documents:
    #     for dir, _, files in os.walk(pdf_dirs):
    #         if 

    #     for dir in dirs:
    #         # Get all HTML and CSS files from the directory unless they start with an underscore.
    #         html_filepaths = [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.html') and not f.startswith('_')]
    #         css_filepaths = [os.path.join(dir, f) for f in os.listdir(dir) if (f.endswith('.css') or f.endswith('.scss')) and not f.startswith('_')]

    #         # Skip if we can't find the files.
    #         if not html_filepaths or not css_filepaths:
    #                logger.warning("document {dir} did not contain either HTML or CCS files. Skipping...")
    #                continue

    #         dir_dict = {
    #             'pdf_name': dir.split(os.sep)[-1],  # Get the last part of the directory path and set that to the pdf name
    #             'html_files': sorted (html_filepaths),
    #             'css_files': sorted(css_filepaths),
    #         }
    #         logger.info(f"dir_dict: {dir_dict}",f=True)

    #         docs_list_of_dicts.append(dir_dict)
    # return docs_list_of_dicts

