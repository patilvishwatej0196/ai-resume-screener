# resume_reader.py
# This file reads PDF resumes and extracts the text from them
# We will use this in the matching engine later

# Import pdfplumber - the library that can open and read PDF files
import pdfplumber

# Import os - helps us work with files and folder paths
import os


# -------------------------------------------------------
# FUNCTION 1: Extract text from a single PDF file
# -------------------------------------------------------

def extract_text_from_pdf(pdf_path):
    # This function takes a PDF file path as input
    # and returns all the text inside that PDF as a string

    # 'try' means: attempt the following code
    # if anything goes wrong, jump to 'except' instead of crashing
    try:

        # Open the PDF file using pdfplumber
        # 'with' means: open the file, do the work, then close it automatically
        with pdfplumber.open(pdf_path) as pdf:

            # Create an empty list to store text from each page
            all_text = []

            # Loop through every page in the PDF
            # pdf.pages gives us a list of all pages
            for page in pdf.pages:

                # Extract the text from this single page
                # extract_text() returns a string or None if page is empty
                page_text = page.extract_text()

                # Check if the page actually had text (not empty/image-only)
                if page_text:

                    # Add this page's text to our list
                    all_text.append(page_text)

            # Join all pages together into one big string
            # '\n' adds a new line between each page's text
            full_text = '\n'.join(all_text)

            # Return the complete text of the entire PDF
            return full_text

    # If anything goes wrong (file not found, corrupted PDF, etc.)
    except Exception as e:

        # Print what went wrong so we know which file caused the issue
        print(f"Error reading {pdf_path}: {e}")

        # Return empty string so the program keeps running
        return ""


# -------------------------------------------------------
# FUNCTION 2: Read all PDFs from a folder
# -------------------------------------------------------

def read_all_resumes(folder_path):
    # This function reads every PDF file in a folder
    # Returns a dictionary: { filename: extracted_text }

    # Create an empty dictionary to store results
    # Format: { "resume1.pdf": "John Doe Python Developer..." }
    resumes = {}

    # Check if the folder actually exists before trying to read it
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return resumes

    # os.listdir gives us a list of all files in the folder
    for filename in os.listdir(folder_path):

        # Only process files that end with .pdf
        # .lower() handles both .PDF and .pdf
        if filename.lower().endswith('.pdf'):

            # Build the full path to this PDF file
            # os.path.join safely combines folder path + filename
            full_path = os.path.join(folder_path, filename)

            # Print a message so we can see progress
            print(f"Reading: {filename}")

            # Call our extract function on this PDF
            text = extract_text_from_pdf(full_path)

            # Only save it if we actually got some text
            if text.strip():

                # Save to dictionary with filename as key
                resumes[filename] = text

                # Print how many characters were extracted
                print(f"  Extracted {len(text)} characters")

            else:
                # Warn us if a PDF came back empty
                print(f"  Warning: No text found in {filename}")

    # Return the complete dictionary of all resumes
    return resumes


# -------------------------------------------------------
# FUNCTION 3: Read a single job description text file
# -------------------------------------------------------

def read_job_description(jd_path):
    # This function reads a .txt job description file
    # and returns its content as a string

    try:
        # Open the text file in read mode
        # encoding='utf-8' handles special characters properly
        with open(jd_path, 'r', encoding='utf-8') as file:

            # Read the entire file content into a string
            content = file.read()

            # Return the job description text
            return content

    except Exception as e:
        print(f"Error reading job description {jd_path}: {e}")
        return ""


# -------------------------------------------------------
# MAIN: Test everything when we run this file directly
# -------------------------------------------------------

# This block only runs when you run this file directly
# It will NOT run when other files import this file
if __name__ == "__main__":

    print("=" * 50)
    print("RESUME READER - TEST RUN")
    print("=" * 50)

    # --- TEST 1: Read all PDFs from resumes folder ---
    print("\n[TEST 1] Reading resumes from data/resumes/ folder...")
    print("-" * 40)

    # Path to the resumes folder
    resumes_folder = "data/resumes"

    # Call our function to read all resumes
    all_resumes = read_all_resumes(resumes_folder)

    # Check how many resumes were found
    if all_resumes:
        print(f"\nSuccessfully read {len(all_resumes)} resume(s)")

        # Show a preview of the first resume
        first_resume_name = list(all_resumes.keys())[0]
        first_resume_text = all_resumes[first_resume_name]

        print(f"\nPreview of '{first_resume_name}':")
        print("-" * 40)

        # Print only the first 500 characters as a preview
        # so the terminal doesn't get flooded
        print(first_resume_text[:500])
        print("...")

    else:
        print("No PDF resumes found in data/resumes/")
        print("Add some PDF files to data/resumes/ and try again")

    # --- TEST 2: Read a job description ---
    print("\n[TEST 2] Reading job description...")
    print("-" * 40)

    # Path to one of our job description files
    jd_path = "data/job_descriptions/python_developer.txt"

    # Read it
    jd_text = read_job_description(jd_path)

    if jd_text:
        print(f"Job description loaded ({len(jd_text)} characters)")
        print("\nPreview:")
        print("-" * 40)

        # Show first 300 characters
        print(jd_text[:300])
        print("...")
    else:
        print("Could not read job description file")

    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)