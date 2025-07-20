import os
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt

# Folder containing the PDFs
folder_path = "verdicts"

# List to hold the page counts
page_counts = []

# Loop over all PDF files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(folder_path, filename)
        
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            page_counts.append(num_pages)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Plot the histogram
plt.figure(figsize=(10, 6))
plt.hist(page_counts, bins=range(1, max(page_counts)+2), edgecolor='black', align='left')
plt.title("Histogram of Number of Pages in PDFs")
plt.xlabel("Number of Pages")
plt.ylabel("Number of PDFs")
plt.xticks(range(1, max(page_counts)+1))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
