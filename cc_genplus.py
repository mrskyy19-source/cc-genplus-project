#!/usr/bin/env python3
"""
Enterprise-Grade Synthetic Test Data Generator
================================================
Purpose: Generate safe, synthetic test data for legitimate business purposes
including software testing, QA, demo environments, and educational use.

License: Commercial Use Permitted
Version: 4.0.0-enterprise
"""

import random
import logging
import json
import hashlib
import csv
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import Counter
import argparse
import threading
from abc import ABC, abstractmethod

from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('generator.log')
    ]
)
logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output formats for enterprise use."""
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    SQL = "sql"
    XML = "xml"


class SecurityLevel(Enum):
    """Data sensitivity levels for compliance."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class GeneratorConfig:
    """Configuration for the data generator."""
    locale: str = "en_US"
    seed: Optional[int] = None
    output_format: OutputFormat = OutputFormat.JSON
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    batch_size: int = 1000
    output_dir: str = "./output"
    include_metadata: bool = True
    validate_output: bool = True
    
    def __post_init__(self):
        if isinstance(self.output_format, str):
            self.output_format = OutputFormat(self.output_format)
        if isinstance(self.security_level, str):
            self.security_level = SecurityLevel(self.security_level)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


class DataGenerator(ABC):
    """Abstract base class for data generators."""
    
    @abstractmethod
    def generate(self, count: int) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        pass


class CreditCardGenerator(DataGenerator):
    """Generates synthetic credit card numbers for testing (Luhn valid)."""
    
    # Test card prefixes (never real issuer ranges)
    TEST_PREFIXES = {
        'visa': ['400000', '411111', '422222', '433333', '444444', '455555'],
        'mastercard': ['510000', '520000', '530000', '540000', '550000'],
        'amex': ['340000', '370000'],
        'discover': ['601100', '601111', '601122'],
        'jcb': ['352800', '358900'],
        'diners': ['300000', '305000', '360000', '380000'],
        'unionpay': ['620000', '622200', '624000', '626000', '628200'],
    }
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.fake = Faker(config.locale)
        if config.seed:
            random.seed(config.seed)
            self.fake.seed_instance(config.seed)
    
    def _luhn_checksum(self, number: str) -> int:
        """Calculate Luhn checksum."""
        digits = [int(d) for d in number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        return checksum % 10
    
    def _make_luhn_valid(self, number: str) -> str:
        """Make a number Luhn valid by adjusting the last digit."""
        check = self._luhn_checksum(number + '0')
        check_digit = (10 - check) % 10
        return number + str(check_digit)
    
    def generate(self, count: int) -> List[Dict[str, Any]]:
        """Generate synthetic credit card test data."""
        results = []
        card_types = list(self.TEST_PREFIXES.keys())
        
        for _ in range(count):
            card_type = random.choice(card_types)
            prefix = random.choice(self.TEST_PREFIXES[card_type])
            
            # Generate remaining digits (15-16 total depending on type)
            if card_type == 'amex':
                remaining_length = 15 - len(prefix)
            else:
                remaining_length = 16 - len(prefix)
            
            body = ''.join(str(random.randint(0, 9)) for _ in range(remaining_length - 1))
            partial = prefix + body
            full_number = self._make_luhn_valid(partial)
            
            # Generate expiry (future date)
            exp_year = random.randint(datetime.now().year, datetime.now().year + 5)
            exp_month = random.randint(1, 12)
            
            # Generate CVV
            cvv_length = 4 if card_type == 'amex' else 3
            cvv = ''.join(str(random.randint(0, 9)) for _ in range(cvv_length))
            
            record = {
                'card_number': full_number,
                'card_type': card_type,
                'expiry_month': f"{exp_month:02d}",
                'expiry_year': str(exp_year),
                'cvv': cvv,
                'holder_name': self.fake.name(),
                'billing_address': {
                    'street': self.fake.street_address(),
                    'city': self.fake.city(),
                    'state': self.fake.state(),
                    'zipcode': self.fake.zipcode(),
                    'country': self.fake.country_code()
                }
            }
            
            if self.config.include_metadata:
                record['_metadata'] = {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'generator_version': '4.0.0-enterprise',
                    'security_level': self.config.security_level.value,
                    'checksum': hashlib.sha256(full_number.encode()).hexdigest()[:16]
                }
            
            results.append(record)
        
        return results
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate generated credit card data."""
        required_fields = ['card_number', 'card_type', 'expiry_month', 'expiry_year', 'cvv']
        if not all(field in data for field in required_fields):
            return False
        
        # Luhn check
        number = data['card_number'].replace(' ', '').replace('-', '')
        return self._luhn_checksum(number) == 0


class PersonGenerator(DataGenerator):
    """Generates synthetic person data for testing."""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.fake = Faker(config.locale)
        if config.seed:
            self.fake.seed_instance(config.seed)
    
    def generate(self, count: int) -> List[Dict[str, Any]]:
        results = []
        for _ in range(count):
            profile = self.fake.profile()
            record = {
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self.fake.email(),
                'phone': self.fake.phone_number(),
                'address': {
                    'street': self.fake.street_address(),
                    'city': self.fake.city(),
                    'state': self.fake.state(),
                    'zipcode': self.fake.zipcode(),
                    'country': self.fake.country()
                },
                'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
                'ssn': self.fake.ssn(),  # Synthetic SSN for testing only
                'company': self.fake.company(),
                'job_title': self.fake.job(),
            }
            
            if self.config.include_metadata:
                record['_metadata'] = {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'generator_version': '4.0.0-enterprise',
                    'security_level': self.config.security_level.value
                }
            
            results.append(record)
        
        return results
    
    def validate(self, data: Dict[str, Any]) -> bool:
        required = ['first_name', 'last_name', 'email', 'phone']
        return all(field in data for field in required)


class TransactionGenerator(DataGenerator):
    """Generates synthetic financial transaction data."""
    
    TRANSACTION_TYPES = ['purchase', 'refund', 'withdrawal', 'deposit', 'transfer', 'fee']
    CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF']
    STATUSES = ['completed', 'pending', 'failed', 'cancelled', 'processing']
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.fake = Faker(config.locale)
        if config.seed:
            self.fake.seed_instance(config.seed)
    
    def generate(self, count: int) -> List[Dict[str, Any]]:
        results = []
        for _ in range(count):
            record = {
                'transaction_id': self.fake.uuid4(),
                'timestamp': self.fake.date_time_between(
                    start_date='-1y', end_date='now', tzinfo=timezone.utc
                ).isoformat(),
                'type': random.choice(self.TRANSACTION_TYPES),
                'amount': round(random.uniform(0.01, 10000.00), 2),
                'currency': random.choice(self.CURRENCIES),
                'status': random.choice(self.STATUSES),
                'merchant': {
                    'name': self.fake.company(),
                    'category': self.fake.random_element([
                        'retail', 'dining', 'travel', 'entertainment', 'groceries',
                        'utilities', 'healthcare', 'education', 'other'
                    ]),
                    'location': {
                        'city': self.fake.city(),
                        'country': self.fake.country_code()
                    }
                },
                'card_last_four': ''.join(str(random.randint(0, 9)) for _ in range(4)),
                'description': self.fake.sentence(nb_words=6)
            }
            
            if self.config.include_metadata:
                record['_metadata'] = {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'generator_version': '4.0.0-enterprise',
                    'security_level': self.config.security_level.value
                }
            
            results.append(record)
        
        return results
    
    def validate(self, data: Dict[str, Any]) -> bool:
        required = ['transaction_id', 'timestamp', 'type', 'amount', 'currency', 'status']
        return all(field in data for field in required)


class OutputWriter:
    """Handles writing output in various formats."""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def write(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Write data to file in configured format."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{filename}_{timestamp}"
        
        if self.config.output_format == OutputFormat.JSON:
            return self._write_json(data, base_name)
        elif self.config.output_format == OutputFormat.JSONL:
            return self._write_jsonl(data, base_name)
        elif self.config.output_format == OutputFormat.CSV:
            return self._write_csv(data, base_name)
        elif self.config.output_format == OutputFormat.SQL:
            return self._write_sql(data, base_name)
        elif self.config.output_format == OutputFormat.XML:
            return self._write_xml(data, base_name)
        else:
            raise ValueError(f"Unsupported format: {self.config.output_format}")
    
    def _write_json(self, data: List[Dict], base_name: str) -> str:
        filepath = Path(self.config.output_dir) / f"{base_name}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Written {len(data)} records to {filepath}")
        return str(filepath)
    
    def _write_jsonl(self, data: List[Dict], base_name: str) -> str:
        filepath = Path(self.config.output_dir) / f"{base_name}.jsonl"
        with open(filepath, 'w') as f:
            for record in data:
                f.write(json.dumps(record, default=str) + '\n')
        logger.info(f"Written {len(data)} records to {filepath}")
        return str(filepath)
    
    def _write_csv(self, data: List[Dict], base_name: str) -> str:
        filepath = Path(self.config.output_dir) / f"{base_name}.csv"
        if not data:
            return str(filepath)
        
        # Flatten nested structures for CSV
        flattened = [self._flatten_dict(record) for record in data]
        fieldnames = set()
        for record in flattened:
            fieldnames.update(record.keys())
        fieldnames = sorted(fieldnames)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened)
        logger.info(f"Written {len(data)} records to {filepath}")
        return str(filepath)
    
    def _write_sql(self, data: List[Dict], base_name: str) -> str:
        filepath = Path(self.config.output_dir) / f"{base_name}.sql"
        if not data:
            return str(filepath)
        
        # Simple INSERT statements
        with open(filepath, 'w') as f:
            f.write(f"-- Generated test data - {datetime.now(timezone.utc).isoformat()}\n\n")
            for record in data:
                flat = self._flatten_dict(record)
                columns = ', '.join(flat.keys())
                values = ', '.join(self._sql_value(v) for v in flat.values())
                f.write(f"INSERT INTO {base_name} ({columns}) VALUES ({values});\n")
        logger.info(f"Written {len(data)} records to {filepath}")
        return str(filepath)
    
    def _write_xml(self, data: List[Dict], base_name: str) -> str:
        filepath = Path(self.config.output_dir) / f"{base_name}.xml"
        with open(filepath, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<{base_name}>\n')
            for record in data:
                f.write('  <record>\n')
                for key, value in self._flatten_dict(record).items():
                    f.write(f'    <{key}>{self._xml_escape(str(value))}</{key}>\n')
                f.write('  </record>\n')
            f.write(f'</{base_name}>\n')
        logger.info(f"Written {len(data)} records to {filepath}")
        return str(filepath)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _sql_value(self, value: Any) -> str:
        """Convert value to SQL literal."""
        if value is None:
            return 'NULL'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        else:
            escaped = str(value).replace("'", "''")
            return f"'{escaped}'"
    
    def _xml_escape(self, text: str) -> str:
        """Escape XML special characters."""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


class EnterpriseDataGenerator:
    """Main orchestrator for enterprise data generation."""
    
    GENERATORS = {
        'credit_cards': CreditCardGenerator,
        'persons': PersonGenerator,
        'transactions': TransactionGenerator,
    }
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.writer = OutputWriter(config)
        self.generators = {}
        for name, gen_class in self.GENERATORS.items():
            self.generators[name] = gen_class(config)
    
    def generate(self, data_type: str, count: int) -> List[Dict[str, Any]]:
        """Generate data of specified type."""
        if data_type not in self.generators:
            raise ValueError(f"Unknown data type: {data_type}. Available: {list(self.GENERATORS.keys())}")
        
        logger.info(f"Generating {count} {data_type} records...")
        generator = self.generators[data_type]
        data = generator.generate(count)
        
        if self.config.validate_output:
            valid_count = sum(1 for record in data if generator.validate(record))
            logger.info(f"Validation: {valid_count}/{count} records passed")
        
        return data
    
    def generate_and_save(self, data_type: str, count: int, filename: Optional[str] = None) -> str:
        """Generate data and save to file."""
        data = self.generate(data_type, count)
        filename = filename or data_type
        return self.writer.write(data, filename)
    
    def generate_batch(self, specs: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate multiple data types in batch."""
        results = {}
        for spec in specs:
            data_type = spec['type']
            count = spec.get('count', self.config.batch_size)
            filename = spec.get('filename', data_type)
            filepath = self.generate_and_save(data_type, count, filename)
            results[data_type] = filepath
        return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Enterprise Synthetic Test Data Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 1000 credit cards as JSON
  python cc_genplus.py --type credit_cards --count 1000 --format json
  
  # Generate mixed batch
  python cc_genplus.py --batch '{"credit_cards": 500, "persons": 200, "transactions": 1000}'
  
  # Generate with specific seed for reproducibility
  python cc_genplus.py --type persons --count 100 --seed 42 --format csv
  
  # Generate to specific directory
  python cc_genplus.py --type transactions --count 5000 --output ./test_data
        """
    )
    
    parser.add_argument('--type', choices=['credit_cards', 'persons', 'transactions'],
                       help='Type of data to generate')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of records to generate (default: 1000)')
    parser.add_argument('--format', choices=[f.value for f in OutputFormat],
                       default='json', help='Output format (default: json)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--output', default='./output', help='Output directory')
    parser.add_argument('--batch', help='JSON string for batch generation')
    parser.add_argument('--locale', default='en_US', help='Faker locale')
    parser.add_argument('--security-level', choices=[s.value for s in SecurityLevel],
                       default='internal', help='Data security classification')
    parser.add_argument('--no-metadata', action='store_true', help='Exclude metadata fields')
    parser.add_argument('--no-validate', action='store_true', help='Skip output validation')
    parser.add_argument('--version', action='version', version='4.0.0-enterprise')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    config = GeneratorConfig(
        locale=args.locale,
        seed=args.seed,
        output_format=OutputFormat(args.format),
        security_level=SecurityLevel(args.security_level),
        output_dir=args.output,
        include_metadata=not args.no_metadata,
        validate_output=not args.no_validate,
    )
    
    generator = EnterpriseDataGenerator(config)
    
    if args.batch:
        try:
            batch_spec = json.loads(args.batch)
            specs = [{'type': k, 'count': v} for k, v in batch_spec.items()]
            results = generator.generate_batch(specs)
            for data_type, filepath in results.items():
                print(f"{data_type}: {filepath}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid batch JSON: {e}")
            sys.exit(1)
    elif args.type:
        filepath = generator.generate_and_save(args.type, args.count)
        print(f"Generated: {filepath}")
    else:
        logger.error("Must specify --type or --batch")
        sys.exit(1)


if __name__ == '__main__':
    main()
