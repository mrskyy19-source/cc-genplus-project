# Enterprise Synthetic Test Data Generator

> **⚠️ IMPORTANT: For Legitimate Testing Purposes Only**
> This tool generates **synthetic test data** for software testing, QA, demo environments, and educational use. All generated data is algorithmically created and does not represent real individuals, financial accounts, or transactions.

## Features

- **Multiple Data Types**: Credit cards (Luhn-valid), Persons, Financial Transactions
- **Enterprise Output Formats**: JSON, JSONL, CSV, SQL, XML
- **Reproducible Generation**: Seed-based deterministic output
- **Configurable Security Levels**: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
- **Batch Processing**: Generate multiple data types in one run
- **Validation**: Built-in Luhn algorithm validation for credit cards
- **Metadata Tracking**: Generation timestamps, versioning, checksums

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Quick Start
Bash

Copy
# Generate 100 credit card test records as JSON
python cc_genplus.py --type credit_cards --count 100

# Generate 500 person records as CSV with seed for reproducibility
python cc_genplus.py --type persons --count 500 --format csv --seed 42

# Generate batch: 200 cards, 100 persons, 500 transactions
python cc_genplus.py --batch '{"credit_cards": 200, "persons": 100, "transactions": 500}'

# Generate SQL INSERT statements for test database
python cc_genplus.py --type transactions --count 1000 --format sql --output ./db_seeds
Command Line Options
Option
Description	Default
--type	Data type: credit_cards, persons, transactions	Required*
--count	Number of records	1000
--format	Output format: json, jsonl, csv, sql, xml	json
--seed	Random seed for reproducibility	Random
--output	Output directory	./output
--batch	JSON string for multi-type generation	-
--locale	Faker locale	en_US
--security-level	Data classification	internal
--no-metadata	Exclude metadata fields	false
--no-validate	Skip validation	false
*Either --type or --batch is required.

Data Types
Credit Cards (credit_cards)
Generates Luhn-valid test card numbers using reserved test prefixes:

Visa: 400000, 411111, 422222...
Mastercard: 510000, 520000...
Amex: 340000, 370000...
Discover, JCB, Diners, UnionPay test ranges
Fields: card_number, card_type, expiry_month, expiry_year, cvv, holder_name, billing_address

Persons (persons)
Synthetic personal data for testing user systems.

Fields: first_name, last_name, email, phone, address, date_of_birth, ssn, company, job_title

Transactions (transactions)
Financial transaction test data.

Fields: transaction_id, timestamp, type, amount, currency, status, merchant, card_last_four, description

Output Formats
JSON (default)
JSON

Copy
[
  {
    "card_number": "4111111111111111",
    "card_type": "visa",
    "expiry_month": "12",
    "expiry_year": "2025",
    "cvv": "123",
    "holder_name": "John Doe",
    "billing_address": {...},
    "_metadata": {...}
  }
]
JSONL (newline-delimited)
Jsonl

Copy
{"card_number": "4111111111111111", "card_type": "visa", ...}
{"card_number": "5555555555554444", "card_type": "mastercard", ...}
CSV
Flattened structure with nested objects as JSON strings.

SQL
INSERT statements for database seeding.

XML
Structured XML output.

Programmatic Usage
Python

Copy
from cc_genplus import GeneratorConfig, EnterpriseDataGenerator, OutputFormat, SecurityLevel

config = GeneratorConfig(
    locale="en_US",
    seed=42,
    output_format=OutputFormat.JSON,
    security_level=SecurityLevel.INTERNAL,
    output_dir="./test_data"
)

generator = EnterpriseDataGenerator(config)

# Single type
filepath = generator.generate_and_save("credit_cards", 1000)

# Batch generation
results = generator.generate_batch([
    {"type": "credit_cards", "count": 500, "filename": "cards"},
    {"type": "persons", "count": 200, "filename": "users"},
    {"type": "transactions", "count": 1000, "filename": "txns"}
])
Compliance & Safety
No Real Data: All data is algorithmically generated
Test Prefixes Only: Credit cards use reserved test ranges (never real issuer BINs)
Synthetic Identifiers: SSNs, phone numbers, emails are fake
Audit Trail: Metadata includes generation timestamps and checksums
Security Classification: Configurable sensitivity levels
License
Commercial Use Permitted - See LICENSE file for details.

Contributing
Fork the repository
Create a feature branch
Add tests for new functionality
Ensure all validation passes
Submit a pull request
Support
For issues, feature requests, or security concerns, please open a GitHub issue.
