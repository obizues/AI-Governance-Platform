# Validation service for loan documents

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
            amt = float(str(loan_amount).replace('$','').replace(',',''))
            if amt <= 0:
                errors.append('Loan Amount must be positive')
        except Exception:
            errors.append('Loan Amount invalid format')
    if not getattr(obj, 'interest_rate', None):
        errors.append('Interest Rate missing')
    return errors

# Add more validation functions as needed
