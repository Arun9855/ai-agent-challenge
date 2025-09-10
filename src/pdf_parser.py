import PyPDF2
import pandas as pd
import re
from pathlib import Path

class BankStatementParser:
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.transactions = []
        
    def extract_text_from_pdf(self):
        """Extract text from PDF file"""
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def parse_transactions(self, text):
        """Parse transactions from the extracted text"""
        # This will need to be customized based on the actual PDF format
        # Add specific parsing logic for ICICI bank statements
        pass
    
    def save_to_csv(self, output_path):
        """Save parsed transactions to CSV"""
        df = pd.DataFrame(self.transactions)
        df.to_csv(output_path, index=False)

    def process(self, output_path):
        """Main processing method"""
        text = self.extract_text_from_pdf()
        self.parse_transactions(text)
        self.save_to_csv(output_path)

def main():
    # Example usage
    pdf_path = "../data/icici/icici sample.pdf"
    output_path = "../data/icici/result.csv"
    
    parser = BankStatementParser(pdf_path)
    parser.process(output_path)

if __name__ == "__main__":
    main()
