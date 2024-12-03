"""
Multiple Jupyter to PDF Converter
Copyright (C) 2024  Omar Tazi

A python script to convert multiple Jupyter notebooks to PDF format simultaneously,
with options for selective conversion and PDF merging.
"""

# Standard library imports
import os
import subprocess
import threading
import time
import queue
import sys

# Third-party imports
from PyPDF2 import PdfMerger

def get_size_mb(file_path):
    """Convert file size to MB with 2 decimal places"""
    return round(os.path.getsize(file_path) / (1024 * 1024), 2)

def get_user_selection(total_files):
    while True:
        print("\n    Select files to convert using any of these methods:")
        print("    • Type 'all' or press Enter to select everything")
        print("    • Type a single number (e.g., '3')")
        print("    • Type a range with dash (e.g., '2-7')")
        print("    • Type multiple selections with semicolon (e.g., '1;4;7')")
        print("    • Combine ranges and numbers (e.g., '1-3;5;7-9')")
        selection = input("\n→ Your selection: ").strip().lower()
        
        if selection in ['all', '', '*', 'everything', 'every', 'all files', 'allfiles', 'all-files','ALL', 'ALL FILES','All', 'All Files','a','A','x','X',0]:       
            return list(range(1, total_files + 1))
        try:
            selected_files = []
            for part in selection.split(';'):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected_files.extend(range(start, end + 1))
                else:
                    selected_files.append(int(part))
            
            # Remove duplicates while preserving order
            selected_files = list(dict.fromkeys(selected_files))
            
            if all(1 <= num <= total_files for num in selected_files):
                print(f"\n    Selected {len(selected_files)} unique files.")
                return selected_files
        except ValueError:
            pass
        print("Invalid selection. Please try again or press Ctrl+C to cancel.")

def get_input_with_timeout(prompt, timeout=300):  # Changed to 5 minutes
    """Get user input with a timeout and display countdown"""
    user_input = queue.Queue()
    stop_countdown = threading.Event()
    
    print(f"\nYou have {timeout//60} minutes to respond...")
    
    def input_thread():
        try:
            user_input.put(input(prompt + "\n→ "))  # Get input with prompt on the same line
        except (KeyboardInterrupt, EOFError):
            user_input.put(None)
        finally:
            stop_countdown.set()
    
    def countdown_thread():
        remaining = timeout
        while remaining > 0 and not stop_countdown.is_set():
            sys.stdout.write(f'\rTime remaining: {remaining:3d}s\t\033[K')
            sys.stdout.flush()
            time.sleep(1)
            remaining -= 1
        if not stop_countdown.is_set():
            stop_countdown.set()
    
    input_thread = threading.Thread(target=input_thread)
    countdown_thread = threading.Thread(target=countdown_thread)  # Fixed: Changed target(countdown_thread) to target=countdown_thread
    
    try:
        input_thread.start()
        countdown_thread.start()
        
        while input_thread.is_alive():
            time.sleep(0.1)
        
        result = user_input.get_nowait()
        stop_countdown.set()
        if result is None:
            print("\nOperation cancelled by user.")
            sys.exit(0)
        return result
        
    except (queue.Empty, KeyboardInterrupt):
        stop_countdown.set()
        print("\nOperation cancelled.")
        sys.exit(1)
    finally:
        stop_countdown.set()

def display_greeting():
    """Display ASCII art greeting"""
    print("\n" + "=" * 60)
    print("""
███╗   ███╗██╗   ██╗██╗  ████████╗██╗    ███╗   ██╗██████╗ ██████╗ ██████╗ ██████╗ ███████╗
████╗ ████║██║   ██║██║  ╚══██╔══╝██║    ████╗  ██║██╔══██╗╚════██╗██╔══██╗██╔══██╗██╔════╝
██╔████╔██║██║   ██║██║     ██║   ██║    ██╔██╗ ██║██████╔╝ █████╔╝██████╔╝██║  ██║█████╗  
██║╚██╔╝██║██║   ██║██║     ██║   ██║    ██║╚██╗██║██╔══██╗██╔═══╝ ██╔═══╝ ██║  ██║██╔══╝  
██║ ╚═╝ ██║╚██████╔╝███████╗██║   ██║    ██║ ╚████║██████╔╝███████╗██║     ██████╔╝██║     
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝     ╚═════╝ ╚═╝                                                                                 
    """)
    print("=" * 60 + "\n")

def display_intro():
    """Display introduction text explaining the app's purpose"""
    print("""    Welcome to Multi NB2PDF Converter!
    
    This tool helps you:
    • Convert multiple Jupyter notebooks to PDF format
    • Select specific notebooks to convert
    • Combine all PDFs into a single document (optional)
    • Track conversion progress with size estimates
    
    Let's get started...\n""")

def display_files_paginated(notebook_files, folder_path, page_size=20):
    """Display files in pages with navigation"""
    total_pages = (len(notebook_files) + page_size - 1) // page_size
    current_page = 1
    
    while True:
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, len(notebook_files))
        
        print("\n    " + "̄" * 50)
        print("    Files found (Page {}/{})".format(current_page, total_pages))
        print("    " + "-" * 50)
        
        for index in range(start_idx, end_idx):
            filename = notebook_files[index]
            file_size = get_size_mb(os.path.join(folder_path, filename))
            print(f'    {index + 1:2d}. {filename} ({file_size:.2f} MB)')
        
        print("    " + "-" * 50)
        
        # Auto-continue if it's the last page
        if current_page == total_pages:
            break
            
        if total_pages > 1:
            print("\n    Navigation: [N]ext | [P]revious | [Enter] Continue")
            choice = input("    Choose action: ").strip().lower()
            
            if choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'p' and current_page > 1:
                current_page -= 1
            elif choice in ['', 'c']:
                break

def sanitize_filename(filename):
    """Sanitize and validate filename"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Ensure filename ends with .pdf
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    return filename if filename else 'merged-notebook.pdf'

def get_merge_filename(default_name='merged-notebook.pdf', timeout=60):
    """Get merged PDF filename with timeout"""
    try:
        custom_name = get_input_with_timeout("Enter name for merged PDF: ", timeout).strip()
        if not custom_name:
            return default_name
        return sanitize_filename(custom_name)
    except:
        print("\nUsing default filename due to timeout...")
        return default_name

def get_unique_filename(filepath):
    """Get unique filename by adding number suffix if file exists"""
    if not os.path.exists(filepath):
        return filepath
    
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = os.path.join(directory, f"{name}_{counter}{ext}")
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1

def main():
    # Display greeting and intro
    display_greeting()
    display_intro()
    
    # Get the current working directory
    current_dir = os.getcwd()
    current_folder = os.path.basename(current_dir)
    
    # Ask user about notebook location
    print(f"The notebooks you want to convert are in the current working directory '{current_folder}'.\n")
    location_choice = get_input_with_timeout("\nIs this correct? (y/n): ").strip().lower()
    
    if location_choice in ['yes', 'y', 'Y', 'YES', 'Yes', '']:
        folder_path = current_dir
    else:
        path_input = get_input_with_timeout("Enter the path where the notebooks are located: ").strip()
        
        if not path_input:
            print("No path provided. Exiting.")
            return
        
        folder_path = path_input
        if not os.path.exists(folder_path):
            print("Error: The specified path does not exist.")
            return

    # Get a list of all .ipynb files in the folder
    try:
        notebook_files = [f for f in os.listdir(folder_path) if f.endswith('.ipynb')]
        if not notebook_files:
            print(f"No Jupyter notebooks found in {folder_path}")
            return
    except Exception as e:
        print(f"Error reading directory: {e}")
        return

    total_files = len(notebook_files)

    # Calculate total size
    total_size = sum(get_size_mb(os.path.join(folder_path, f)) for f in notebook_files)
    
    # Display total files and size
    print(f'\n    This folder contains {total_files} notebooks for a total of {total_size:.2f} MB\n')
    
    # Display paginated list of files
    display_files_paginated(notebook_files, folder_path)

    # Get user selection
    selected_files = get_user_selection(total_files)
    total_selected_files = len(selected_files)

    # Only ask about merging if more than one file is selected
    merge_choice = 'no'
    if total_selected_files > 1:
        merge_choice = input("Do you want to merge all PDFs into a single PDF? (yes/no): ").strip().lower()
        merge_pdfs = merge_choice in ['yes', 'y', 'Yes', 'YES', '', 'Y']

    # Convert selected .ipynb files to PDF
    pdf_files = []
    for count, index in enumerate(selected_files, start=1):
        filename = notebook_files[index - 1]
        notebook_path = os.path.join(folder_path, filename)
        file_size = get_size_mb(notebook_path)
        print(f'\n    Converting file {count}/{total_selected_files}:')
        print(f'    → {filename} ({file_size:.2f} MB)')
        subprocess.run(['jupyter', 'nbconvert', '--to', 'pdf', notebook_path])
        pdf_filename = filename.replace('.ipynb', '.pdf')
        pdf_files.append(os.path.join(folder_path, pdf_filename))
        print("\n    " + "-" * 50)

    print('\n    Conversion complete!')

    if merge_pdfs:
        # Get filename when user chooses to merge
        output_filename = get_merge_filename()
        output_pdf_path = os.path.join(folder_path, output_filename)
        
        # Check if file exists
        if os.path.exists(output_pdf_path):
            print(f"\nFile '{output_filename}' already exists!")
            print("Choose an action:")
            print("1. Overwrite existing file")
            print("2. Auto-generate unique name")
            print("3. Enter new filename")
            
            try:
                choice = get_input_with_timeout("Enter choice (1-3): ", 60).strip()
                if choice == "1":
                    pass  # Keep original path, will overwrite
                elif choice == "2":
                    output_pdf_path = get_unique_filename(output_pdf_path)
                    print(f"Using filename: {os.path.basename(output_pdf_path)}")
                elif choice == "3":
                    new_filename = get_merge_filename()
                    output_pdf_path = os.path.join(folder_path, new_filename)
                else:
                    print("Invalid choice, using auto-generated name")
                    output_pdf_path = get_unique_filename(output_pdf_path)
            except:
                print("Timeout or error, using auto-generated name")
                output_pdf_path = get_unique_filename(output_pdf_path)
        
        try:
            # Merge PDFs
            merger = PdfMerger()
            for pdf in pdf_files:
                merger.append(pdf)
            merger.write(output_pdf_path)
            merger.close()
            print(f'\n    ✓ All PDFs have been merged into: {output_pdf_path}')
        except Exception as e:
            print(f"\nError saving merged PDF: {e}")
            fallback_name = 'merged-notebook.pdf'
            output_pdf_path = os.path.join(folder_path, fallback_name)
            print(f"Saving with fallback name: {fallback_name}")
            merger.write(output_pdf_path)
            merger.close()
    
    else:
        print('\n    ✓ PDFs have been kept separate.')

if __name__ == "__main__":
    main()