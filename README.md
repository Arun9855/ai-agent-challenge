# Bank Statement Parser Agent

An AI agent that generates custom parsers for bank statement PDFs.

## Quick Start (5 Steps)

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-agent-challenge
```

2. Create a Python virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Place your bank statement files:
- Put sample PDF in `data/<bank>/<bank>_sample.pdf`
- Put expected CSV in `data/<bank>/result.csv`

5. Run the agent:
```bash
python agent.py --target <bank>
```

## Agent Architecture

The agent implements a self-improving loop using LangGraph:
Plan → Generate Code → Test → Self-Fix (≤3 attempts). It reads sample PDFs and expected CSV outputs to generate custom parsers that match the required schema. The agent uses continuous testing to validate and improve the generated parsers automatically.

## Project Structure

```
.
├── agent.py              # Main AI agent
├── custom_parsers/       # Generated parsers
│   └── icici_parser.py
├── data/                 # Sample data
│   └── icici/
│       ├── icici_sample.pdf
│       └── result.csv
├── test_parsers.py      # Parser tests
├── README.md
└── requirements.txt
```

## Running Tests

```bash
pytest test_parsers.py
```
