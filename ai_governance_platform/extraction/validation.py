# validation.py
# Document validation functions for each document type

def validate_loan_application(obj):
    errors = []
    if not getattr(obj, 'Applicant Name', None):
        errors.append('Applicant Name missing')
    if not getattr(obj, 'Property Address', None):
        errors.append('Property Address missing')
    if not getattr(obj, 'Loan Amount', None):
        errors.append('Loan Amount missing')
    if not getattr(obj, 'Interest Rate', None):
        errors.append('Interest Rate missing')
    if not getattr(obj, 'Term (years)', None):
        errors.append('Term (years) missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_disclosure(obj):
    errors = []
    if not getattr(obj, 'Disclosure Date', None):
        errors.append('Disclosure Date missing')
    if not getattr(obj, 'Loan Terms', None):
        errors.append('Loan Terms missing')
    if not getattr(obj, 'Interest Rate', None):
        errors.append('Interest Rate missing')
    if not getattr(obj, 'Fees', None):
        errors.append('Fees missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_credit_report(obj):
    errors = []
    if not getattr(obj, 'Applicant Name', None):
        errors.append('Applicant Name missing')
    if not getattr(obj, 'Credit Score', None):
        errors.append('Credit Score missing')
    if not getattr(obj, 'Report Date', None):
        errors.append('Report Date missing')
    if not getattr(obj, 'Accounts', None):
        errors.append('Accounts missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_appraisal_report(obj):
    errors = []
    if not getattr(obj, 'Property Address', None):
        errors.append('Property Address missing')
    if not getattr(obj, 'Appraised Value', None):
        errors.append('Appraised Value missing')
    if not getattr(obj, 'Appraiser Name', None):
        errors.append('Appraiser Name missing')
    if not getattr(obj, 'Date', None):
        errors.append('Date missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_income_verification(obj):
    errors = []
    if not getattr(obj, 'Applicant Name', None):
        errors.append('Applicant Name missing')
    if not getattr(obj, 'Employer', None):
        errors.append('Employer missing')
    if not getattr(obj, 'Income', None):
        errors.append('Income missing')
    if not getattr(obj, 'Tax Year', None):
        errors.append('Tax Year missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_bank_statement(obj):
    errors = []
    if not getattr(obj, 'Account Holder', None):
        errors.append('Account Holder missing')
    if not getattr(obj, 'Account Number', None):
        errors.append('Account Number missing')
    if not getattr(obj, 'Balance', None):
        errors.append('Balance missing')
    if not getattr(obj, 'Statement Date', None):
        errors.append('Statement Date missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_tax_return(obj):
    errors = []
    if not getattr(obj, 'Taxpayer Name', None):
        errors.append('Taxpayer Name missing')
    if not getattr(obj, 'Year', None):
        errors.append('Year missing')
    if not getattr(obj, 'Income', None):
        errors.append('Income missing')
    if not getattr(obj, 'Deductions', None):
        errors.append('Deductions missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors

def validate_closing_documents(obj):
    errors = []
    if not getattr(obj, 'Closing Date', None):
        errors.append('Closing Date missing')
    if not getattr(obj, 'Property Address', None):
        errors.append('Property Address missing')
    if not getattr(obj, 'Loan Amount', None):
        errors.append('Loan Amount missing')
    if not getattr(obj, 'Buyer', None):
        errors.append('Buyer missing')
    if not getattr(obj, 'Seller', None):
        errors.append('Seller missing')
    if not getattr(obj, 'Signature', None):
        errors.append('Signature missing')
    return errors
