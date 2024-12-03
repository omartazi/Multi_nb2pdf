```sh
███╗   ███╗██╗   ██╗██╗  ████████╗██╗    ███╗   ██╗██████╗ ██████╗ ██████╗ ██████╗ ███████╗
████╗ ████║██║   ██║██║  ╚══██╔══╝██║    ████╗  ██║██╔══██╗╚════██╗██╔══██╗██╔══██╗██╔════╝
██╔████╔██║██║   ██║██║     ██║   ██║    ██╔██╗ ██║██████╔╝ █████╔╝██████╔╝██║  ██║█████╗  
██║╚██╔╝██║██║   ██║██║     ██║   ██║    ██║╚██╗██║██╔══██╗██╔═══╝ ██╔═══╝ ██║  ██║██╔══╝  
██║ ╚═╝ ██║╚██████╔╝███████╗██║   ██║    ██║ ╚████║██████╔╝███████╗██║     ██████╔╝██║     
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝     ╚═════╝ ╚═╝                                                                                                 
```
 Convert Multiple Jupyter Notebooks to PDF
 
# Multiple Jupyter Notebooks to PDF Converter (Multi_nb2pdf)

This repository contains a Python script to convert multiple Jupyter notebooks (`.ipynb` files) to PDF format simultaneously. The script allows the user to select specific notebooks or ranges of notebooks to convert, and provides an option to merge all generated PDFs into a single PDF file.

## Features

- Convert selected Jupyter notebooks to PDF.
- Option to merge all generated PDFs into a single PDF file.
- User-friendly selection of notebooks to convert.

## Requirements

- Python 3.x
- [Jupyter](https://jupyter.org/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [nbconvert](https://pypi.org/project/nbconvert/)
- [pandoc](https://pandoc.org/)
- [MiKTeX](https://miktex.org/) (for `xelatex`)

## Installation

1. Clone the repository and navigate to the directory:

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Set up your Python environment and install dependencies:

    Using `venv`:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    pip install -r requirements.txt
    ```

    Using `conda`:
    ```sh
    conda create --name multi_nb2pdf_env python=3.x
    conda activate multi_nb2pdf_env
    pip install -r requirements.txt
    ```

3. Ensure MiKTeX is installed and added to your system PATH.

## Usage

1. Place the script `multi_nb2pdf.py` in the directory/folder containing your Jupyter notebooks, or copy its path.
2. Run the script:

    ```sh
    python multi_nb2pdf.py
    ```

    You will be prompted to select the notebooks you want to convert and whether you want to merge the generated PDFs into a single file.
