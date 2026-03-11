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
