# Validation service for loan documents

def validate_loan_application(obj):
    errors = []
    applicant_name = getattr(obj, 'applicant_name', '').strip()
    if not applicant_name:
        errors.append('Applicant name missing')
    # Only add one error for applicant name
    if not getattr(obj, 'property_address', '').strip():
        errors.append('Property address missing')
    if not getattr(obj, 'loan_amount', '').strip():
        errors.append('Loan amount missing')
    if not getattr(obj, 'interest_rate', '').strip():
        errors.append('Interest rate missing')
    if not getattr(obj, 'term_years', '').strip():
        errors.append('Term years missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_disclosure(obj):
    errors = []
    if not getattr(obj, 'disclosure_date', '').strip():
        errors.append('Disclosure date missing')
    if not getattr(obj, 'loan_terms', '').strip():
        errors.append('Loan terms missing')
    if not getattr(obj, 'interest_rate', '').strip():
        errors.append('Interest rate missing')
    if not getattr(obj, 'fees', '').strip():
        errors.append('Fees missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_credit_report(obj):
    errors = []
    if not getattr(obj, 'applicant_name', '').strip():
        errors.append('Applicant name missing')
    if not getattr(obj, 'credit_score', '').strip():
        errors.append('Credit score missing')
    if not getattr(obj, 'report_date', '').strip():
        errors.append('Report date missing')
    if not getattr(obj, 'accounts', '').strip():
        errors.append('Accounts missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_appraisal_report(obj):
    errors = []
    if not getattr(obj, 'property_address', '').strip():
        errors.append('Property address missing')
    if not getattr(obj, 'appraised_value', '').strip():
        errors.append('Appraised value missing')
    if not getattr(obj, 'appraiser_name', '').strip():
        errors.append('Appraiser name missing')
    if not getattr(obj, 'date', '').strip():
        errors.append('Date missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_income_verification(obj):
    errors = []
    if not getattr(obj, 'applicant_name', '').strip():
        errors.append('Applicant name missing')
    if not getattr(obj, 'employer', '').strip():
        errors.append('Employer missing')
    if not getattr(obj, 'income', '').strip():
        errors.append('Income missing')
    if not getattr(obj, 'tax_year', '').strip():
        errors.append('Tax year missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_bank_statement(obj):
    errors = []
    if not getattr(obj, 'account_holder', '').strip():
        errors.append('Account holder missing')
    if not getattr(obj, 'account_number', '').strip():
        errors.append('Account number missing')
    if not getattr(obj, 'balance', '').strip():
        errors.append('Balance missing')
    if not getattr(obj, 'statement_date', '').strip():
        errors.append('Statement date missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_tax_return(obj):
    errors = []
    if not getattr(obj, 'taxpayer_name', '').strip():
        errors.append('Taxpayer name missing')
    if not getattr(obj, 'year', '').strip():
        errors.append('Year missing')
    if not getattr(obj, 'income', '').strip():
        errors.append('Income missing')
    if not getattr(obj, 'deductions', '').strip():
        errors.append('Deductions missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors

def validate_closing_documents(obj):
    errors = []
    if not getattr(obj, 'closing_date', '').strip():
        errors.append('Closing date missing')
    if not getattr(obj, 'property_address', '').strip():
        errors.append('Property address missing')
    if not getattr(obj, 'loan_amount', '').strip():
        errors.append('Loan amount missing')
    if not getattr(obj, 'buyer', '').strip():
        errors.append('Buyer missing')
    if not getattr(obj, 'seller', '').strip():
        errors.append('Seller missing')
    if not getattr(obj, 'signature', '').strip():
        errors.append('Signature missing')
    return errors
