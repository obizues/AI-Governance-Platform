# validation.py
# Document validation functions for each document type

def validate_loan_application(obj):
    errors = []
    if not getattr(obj, 'applicant_name', None):
        errors.append('Applicant Name missing')
    if not getattr(obj, 'property_address', None):
        errors.append('Property Address missing')
    loan_amount = getattr(obj, 'loan_amount', None)
    if loan_amount is None or loan_amount == "":
        errors.append('Loan Amount missing')
    else:
        try:
            # Remove $ and commas, handle negative values
            amt = float(str(loan_amount).replace('$','').replace(',',''))
            if amt <= 0:
                errors.append('Loan Amount must be positive')
        except Exception:
            errors.append('Loan Amount invalid format')
    if not getattr(obj, 'interest_rate', None):
        errors.append('Interest Rate missing')
    if not getattr(obj, 'term_years', None):
        errors.append('Term (years) missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_disclosure(obj):
    errors = []
    if not getattr(obj, 'disclosure_date', None):
        errors.append('Disclosure Date missing')
    if not getattr(obj, 'loan_terms', None):
        errors.append('Loan Terms missing')
    if not getattr(obj, 'interest_rate', None):
        errors.append('Interest Rate missing')
    if not getattr(obj, 'fees', None):
        errors.append('Fees missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_credit_report(obj):
    errors = []
    if not getattr(obj, 'applicant_name', None):
        errors.append('Applicant Name missing')
    if not getattr(obj, 'credit_score', None):
        errors.append('Credit Score missing')
    if not getattr(obj, 'report_date', None):
        errors.append('Report Date missing')
    if not getattr(obj, 'accounts', None):
        errors.append('Accounts missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_appraisal_report(obj):
    errors = []
    if not getattr(obj, 'property_address', None):
        errors.append('Property Address missing')
    if not getattr(obj, 'appraised_value', None):
        errors.append('Appraised Value missing')
    if not getattr(obj, 'appraiser_name', None):
        errors.append('Appraiser Name missing')
    if not getattr(obj, 'date', None):
        errors.append('Date missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_income_verification(obj):
    errors = []
    if not getattr(obj, 'applicant_name', None):
        errors.append('Applicant Name missing')
    if not getattr(obj, 'employer', None):
        errors.append('Employer missing')
    if not getattr(obj, 'income', None):
        errors.append('Income missing')
    if not getattr(obj, 'tax_year', None):
        errors.append('Tax Year missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_bank_statement(obj):
    errors = []
    if not getattr(obj, 'account_holder', None):
        errors.append('Account Holder missing')
    if not getattr(obj, 'account_number', None):
        errors.append('Account Number missing')
    if not getattr(obj, 'balance', None):
        errors.append('Balance missing')
    if not getattr(obj, 'statement_date', None):
        errors.append('Statement Date missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_tax_return(obj):
    errors = []
    if not getattr(obj, 'taxpayer_name', None):
        errors.append('Taxpayer Name missing')
    if not getattr(obj, 'year', None):
        errors.append('Year missing')
    if not getattr(obj, 'income', None):
        errors.append('Income missing')
    if not getattr(obj, 'deductions', None):
        errors.append('Deductions missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors

def validate_closing_documents(obj):
    errors = []
    if not getattr(obj, 'closing_date', None):
        errors.append('Closing Date missing')
    if not getattr(obj, 'property_address', None):
        errors.append('Property Address missing')
    if not getattr(obj, 'loan_amount', None):
        errors.append('Loan Amount missing')
    if not getattr(obj, 'buyer', None):
        errors.append('Buyer missing')
    if not getattr(obj, 'seller', None):
        errors.append('Seller missing')
    if not getattr(obj, 'signature', None):
        errors.append('Signature missing')
    return errors
