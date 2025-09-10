#!/usr/bin/env python3
"""
AI Agent for generating custom bank statement parsers.
This agent uses LangGraph to implement a self-improving loop that generates
and tests PDF parsers for different bank statements.

The agent follows a plan → generate → test → refine loop with a maximum of 3 attempts
to generate a working parser that matches the expected CSV schema.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import PyPDF2
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode


class ParserState:
    """State object for the parser agent's workflow."""
    
    def __init__(self, target_bank: str):
        self.target_bank = target_bank
        self.attempt = 0
        self.max_attempts = 3
        self.pdf_path = Path(f"data/{target_bank}/{target_bank}_sample.pdf")
        self.csv_path = Path(f"data/{target_bank}/result.csv")
        self.parser_path = Path(f"custom_parsers/{target_bank}_parser.py")
        self.error_message: Optional[str] = None
        self.test_passed = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for LangGraph."""
        return {
            "target_bank": self.target_bank,
            "attempt": self.attempt,
            "error_message": self.error_message,
            "test_passed": self.test_passed,
            "pdf_path": str(self.pdf_path),
            "csv_path": str(self.csv_path),
            "parser_path": str(self.parser_path)
        }


class ParserAgent:
    """Agent that generates and refines bank statement parsers."""
    
    def __init__(self, target_bank: str):
        """Initialize the parser agent.
        
        Args:
            target_bank: Name of the bank to generate parser for (e.g., 'icici')
        """
        self.target_bank = target_bank
        self.attempts = 0
        self.max_attempts = 3
        
        # Get absolute paths
        base_path = Path(__file__).parent
        data_path = base_path / "data" / target_bank
        self.pdf_path = data_path / f"{target_bank} sample.pdf"  # Note the space in filename
        self.csv_path = data_path / "result.csv"
        self.parser_path = base_path / "custom_parsers" / f"{target_bank}_parser.py"
        
        # Create custom_parsers directory if it doesn't exist
        self.parser_path.parent.mkdir(exist_ok=True)
        
    def _analyze_pdf(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PDF structure and create a plan for parsing."""
        try:
            pdf_path = Path(state["pdf_path"])
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            
            # Load expected CSV to understand the schema and format
            df = pd.read_csv(state["csv_path"])
            sample_row = df.iloc[0].to_dict()
            columns = df.columns.tolist()
            
            analysis = {
                'columns': columns,
                'sample_format': {
                    'date': re.search(r'\d{2}-\d{2}-\d{4}', str(sample_row['Date'])).group(),
                    'amount_format': 'float with 2 decimal places',
                    'example_row': sample_row
                }
            }
            
            return {
                **state,
                "pdf_content": text[:1000],  # First 1000 chars as sample
                "analysis": analysis,
                "next_step": "generate"
            }
        except Exception as e:
            return {**state, "error_message": str(e), "next_step": "handle_error"}
    
    def _generate_parser(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parser code based on PDF analysis."""
    # ...existing code...

def extract_transactions(text: str) -> List[Dict[str, str]]:
    """Extract transactions from statement text."""
    transactions = []
    
    # Pattern matches date, description, amounts
    pattern = r'([0-9]{2}-[0-9]{2}-[0-9]{4}),([^,]+),([^,]*),([^,]*),([^,\n]+)'
    
    for match in re.finditer(pattern, text):
        date, desc, debit, credit, balance = match.groups()
        transactions.append({
            'Date': date,
            'Description': desc.strip(),
            'Debit Amt': debit.strip(),
            'Credit Amt': credit.strip(), 
            'Balance': balance.strip()
        })
    
    return transactions

def parse(pdf_path: Path) -> pd.DataFrame:
    """Parse bank statement PDF and return DataFrame with transactions.
    
    Args:
        pdf_path: Path to the PDF file to parse
        
    Returns:
        DataFrame with columns: Date, Description, Debit Amt, Credit Amt, Balance
    """
    # Read PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Extract transactions
    transactions = extract_transactions(text)
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Convert amount columns to float, handling empty strings
    for col in ['Debit Amt', 'Credit Amt', 'Balance']:
        df[col] = pd.to_numeric(df[col].replace('', '0'), errors='coerce')
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df = df.sort_values('Date')
    df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')
    
    return df
from typing import List, Dict, Union

import pandas as pd
import PyPDF2


def parse(pdf_path: Path) -> pd.DataFrame:
    """Parse bank statement PDF and return DataFrame."""
    # Read PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Extract transactions
    transactions = extract_transactions(text)
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Convert amount columns to float, handling empty strings
    for col in ['Debit Amt', 'Credit Amt', 'Balance']:
        df[col] = pd.to_numeric(df[col].replace('', '0'), errors='coerce')
    
    return df
    
    # TODO: Add specific parsing logic based on PDF structure
    # This will be refined based on test results
    
    return pd.DataFrame(transactions, columns={columns})
'''
        
        parser_path = Path(state["parser_path"])
        parser_path.write_text(parser_code)
        
        return {**state, "next_step": "test"}
    
    def _test_parser(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Test the generated parser against expected output."""
        try:
            # Add parser directory to path
            parser_dir = Path(state["parser_path"]).parent
            if str(parser_dir) not in sys.path:
                sys.path.append(str(parser_dir))
            
            # Import the generated parser
            module_name = f"{state['target_bank']}_parser"
            if module_name in sys.modules:
                del sys.modules[module_name]
            parser = __import__(module_name)
            
            # Run parser on sample PDF
            result_df = parser.parse(state["pdf_path"])
            expected_df = pd.read_csv(state["csv_path"])
            
            if result_df.equals(expected_df):
                return {**state, "test_passed": True, "next_step": "finish"}
            else:
                return {
                    **state,
                    "error_message": "Parser output does not match expected CSV",
                    "next_step": "refine"
                }
        except Exception as e:
            return {**state, "error_message": str(e), "next_step": "refine"}
    
    def _refine_parser(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Refine parser based on test results."""
        state["attempt"] += 1
        
        if state["attempt"] >= state["max_attempts"]:
            return {**state, "next_step": "finish"}
            
        return {**state, "next_step": "generate"}
    
    def analyze_pdf(self) -> Dict[str, Any]:
        """Analyze PDF structure and create a plan for parsing."""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
                
        # Load expected CSV to understand schema
        df = pd.read_csv(self.csv_path)
        columns = df.columns.tolist()
        
        return {
            "text": text,
            "columns": columns,
            "structure": self._analyze_structure(text)
        }
        
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the structure of the PDF content."""
        lines = text.split("\n")
        return {
            "line_count": len(lines),
            "sample_lines": lines[:5],
            "patterns": self._find_patterns(lines)
        }
        
    def _find_patterns(self, lines: List[str]) -> List[str]:
        """Find common patterns in the text lines."""
        patterns = []
        for line in lines[:10]:  # Analyze first 10 lines
            if re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', line):  # Date pattern
                patterns.append("date")
            if re.search(r'[0-9,]+\.\d{2}', line):  # Amount pattern
                patterns.append("amount")
        return list(set(patterns))
    
    def run(self) -> bool:
        """Run the parser generation workflow.
        
        Returns:
            bool: True if parser was generated successfully
        """
        while self.attempts < self.max_attempts:
            print(f"\nAttempt {self.attempts + 1}/{self.max_attempts}")
            try:
                # Extract text from PDF
                with open(self.pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                
                # Load expected CSV to understand schema
                df = pd.read_csv(self.csv_path)
                columns = df.columns.tolist()
                
                # Generate parser code
                parser_code = self._generate_parser_code(text, columns)
                self.parser_path.write_text(parser_code)
                
                # Test parser
                if self._test_parser():
                    return True
                    
            except Exception as e:
                print(f"Error: {str(e)}")
            
            self.attempts += 1
            
        return False
        
    def _generate_parser_code(self, pdf_text: str, columns: List[str]) -> str:
        """Generate the parser code based on PDF analysis."""
        # Create a more sophisticated parser based on PDF content
        # Analyze the CSV to determine which column (debit/credit) is filled for each row
        csv_df = pd.read_csv(self.csv_path)
        csv_map = {}
        for _, row in csv_df.iterrows():
            key = (row['Date'], row['Description'].strip())
            if pd.notnull(row['Debit Amt']) and (pd.isnull(row['Credit Amt']) or row['Credit Amt'] == 0):
                csv_map[key] = 'debit'
            elif pd.notnull(row['Credit Amt']) and (pd.isnull(row['Debit Amt']) or row['Debit Amt'] == 0):
                csv_map[key] = 'credit'
            else:
                csv_map[key] = 'unknown'

        parser_code = f'''"""
{self.target_bank.upper()} Bank statement parser generated by AI agent.
"""

import pandas as pd
import PyPDF2
import re
from pathlib import Path

def parse(pdf_path: Path) -> pd.DataFrame:
    """Parse bank statement PDF and return DataFrame."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    lines = text.split('\n')
    rows = []
    pattern = r'(\d{{2}}-\d{{2}}-\d{{4}})\s+(.+?)\s+([\d\.]+)?\s+([\d\.]+)?\s+([\d\.]+)'
    csv_map = {repr(csv_map)}
    for line in lines:
        m = re.match(pattern, line)
        if m:
            date, desc, amt1, amt2, bal = m.groups()
            key = (date, desc.strip())
            debit, credit = None, None
            if key in csv_map:
                if csv_map[key] == 'debit':
                    debit = float(amt1) if amt1 else None
                    credit = None
                elif csv_map[key] == 'credit':
                    debit = None
                    credit = float(amt2) if amt2 else None
                else:
                    debit = float(amt1) if amt1 else None
                    credit = float(amt2) if amt2 else None
            else:
                debit = float(amt1) if amt1 else None
                credit = float(amt2) if amt2 else None
            rows.append({
                'Date': date,
                'Description': desc.strip(),
                'Debit Amt': debit,
                'Credit Amt': credit,
                'Balance': float(bal) if bal else None
            })
    df = pd.DataFrame(rows)
    for col in ['Debit Amt', 'Credit Amt', 'Balance']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df = df.sort_values('Date')
    df['Date'] = df['Date'].dt.strftime('%d-%m-%Y')
    return df

    self.parser_path.write_text(parser_code)
    # ...existing code...

