import pdfplumber
from io import BytesIO
import re

def extract_pdf_text(pdf_bytes):
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text

def to_snake_case(s):
    s = s.replace('(', '').replace(')', '')
    s = re.sub(r'[^a-zA-Z0-9 ]', '', s)
    s = s.replace(' ', '_')
    return s.lower()

def parse_fields(text, doc_type):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    fields = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            snake_key = to_snake_case(key.strip())
            fields[snake_key] = value.strip()
    return fields

def build_object(doc_type, fields):
    if doc_type == 'Loan Application':
        return LoanApplication(
            fields.get('applicant_name',''), fields.get('property_address',''), fields.get('loan_amount',''),
            fields.get('interest_rate',''), fields.get('term_years',''), fields.get('signature',''))
    elif doc_type == 'Disclosure':
        return Disclosure(
            fields.get('disclosure_date',''), fields.get('loan_terms',''), fields.get('interest_rate',''),
            fields.get('fees',''), fields.get('signature',''))
    elif doc_type == 'Credit Report':
        return CreditReport(
            fields.get('applicant_name',''), fields.get('credit_score',''), fields.get('report_date',''),
            fields.get('accounts',''), fields.get('signature',''))
    elif doc_type == 'Appraisal Report':
        return AppraisalReport(
            fields.get('property_address',''), fields.get('appraised_value',''), fields.get('appraiser_name',''),
            fields.get('date',''), fields.get('signature',''))
    elif doc_type == 'Income Verification':
        return IncomeVerification(
            fields.get('applicant_name',''), fields.get('employer',''), fields.get('income',''),
            fields.get('tax_year',''), fields.get('signature',''))
    elif doc_type == 'Bank Statement':
        return BankStatement(
            fields.get('account_holder',''), fields.get('account_number',''), fields.get('balance',''),
            fields.get('statement_date',''), fields.get('signature',''))
    elif doc_type == 'Tax Return':
        return TaxReturn(
            fields.get('taxpayer_name',''), fields.get('year',''), fields.get('income',''),
            fields.get('deductions',''), fields.get('signature',''))
    elif doc_type == 'Closing Documents':
        return ClosingDocuments(
            fields.get('closing_date',''), fields.get('property_address',''), fields.get('loan_amount',''),
            fields.get('buyer',''), fields.get('seller',''), fields.get('signature',''))
    else:
        return fields

class LoanApplication:
    def __init__(self, applicant_name, property_address, loan_amount, interest_rate, term_years, signature):
        self.applicant_name = applicant_name
        self.property_address = property_address
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.term_years = term_years
        self.signature = signature

class Disclosure:
    def __init__(self, disclosure_date, loan_terms, interest_rate, fees, signature):
        self.disclosure_date = disclosure_date
        self.loan_terms = loan_terms
        self.interest_rate = interest_rate
        self.fees = fees
        self.signature = signature

class CreditReport:
    def __init__(self, applicant_name, credit_score, report_date, accounts, signature):
        self.applicant_name = applicant_name
        self.credit_score = credit_score
        self.report_date = report_date
        self.accounts = accounts
        self.signature = signature

class AppraisalReport:
    def __init__(self, property_address, appraised_value, appraiser_name, date, signature):
        self.property_address = property_address
        self.appraised_value = appraised_value
        self.appraiser_name = appraiser_name
        self.date = date
        self.signature = signature

class IncomeVerification:
    def __init__(self, applicant_name, employer, income, tax_year, signature):
        self.applicant_name = applicant_name
        self.employer = employer
        self.income = income
        self.tax_year = tax_year
        self.signature = signature

class BankStatement:
    def __init__(self, account_holder, account_number, balance, statement_date, signature):
        self.account_holder = account_holder
        self.account_number = account_number
        self.balance = balance
        self.statement_date = statement_date
        self.signature = signature

class TaxReturn:
    def __init__(self, taxpayer_name, year, income, deductions, signature):
        self.taxpayer_name = taxpayer_name
        self.year = year
        self.income = income
        self.deductions = deductions
        self.signature = signature

class ClosingDocuments:
    def __init__(self, closing_date, property_address, loan_amount, buyer, seller, signature):
        self.closing_date = closing_date
        self.property_address = property_address
        self.loan_amount = loan_amount
        self.buyer = buyer
        self.seller = seller
        self.signature = signature

def extract_and_validate(document_bytes):
    from ai_governance_platform.services.validation_service import (
        validate_loan_application, validate_disclosure, validate_credit_report,
        validate_appraisal_report, validate_income_verification, validate_bank_statement,
        validate_tax_return, validate_closing_documents
    )
    text = extract_pdf_text(document_bytes)
    # Simple heuristic for doc_type
    doc_type = None
    if 'Loan Application' in text:
        doc_type = 'Loan Application'
    elif 'Disclosure' in text:
        doc_type = 'Disclosure'
    elif 'Credit Report' in text:
        doc_type = 'Credit Report'
    elif 'Appraisal Report' in text:
        doc_type = 'Appraisal Report'
    elif 'Income Verification' in text:
        doc_type = 'Income Verification'
    elif 'Bank Statement' in text:
        doc_type = 'Bank Statement'
    elif 'Tax Return' in text:
        doc_type = 'Tax Return'
    elif 'Closing Documents' in text:
        doc_type = 'Closing Documents'
    else:
        doc_type = 'Unknown'
    fields = parse_fields(text, doc_type)
    obj = build_object(doc_type, fields)
    errors = []
    if doc_type == 'Loan Application':
        errors = validate_loan_application(obj)
    elif doc_type == 'Disclosure':
        errors = validate_disclosure(obj)
    elif doc_type == 'Credit Report':
        errors = validate_credit_report(obj)
    elif doc_type == 'Appraisal Report':
        errors = validate_appraisal_report(obj)
    elif doc_type == 'Income Verification':
        errors = validate_income_verification(obj)
    elif doc_type == 'Bank Statement':
        errors = validate_bank_statement(obj)
    elif doc_type == 'Tax Return':
        errors = validate_tax_return(obj)
    elif doc_type == 'Closing Documents':
        errors = validate_closing_documents(obj)
    return {
        'doc_type': doc_type,
        'fields': fields,
        'errors': errors,
        'confidence': 0.8 if not errors else 0.5,
        'status': 'success' if not errors else 'validation_errors'
    }
