import os
import zipfile
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

OUTPUT_DIR = "sample_zips"
PDF_FORMS = [
    ("Loan_Application.pdf", "Home Loan Application Form", ["Applicant Name", "Property Address", "Loan Amount", "Interest Rate", "Term (years)", "Signature"]),
    ("Disclosure.pdf", "Disclosure Statement", ["Disclosure Date", "Loan Terms", "Interest Rate", "Fees", "Signature"]),
    ("Credit_Report.pdf", "Credit Report", ["Applicant Name", "Credit Score", "Report Date", "Accounts", "Signature"]),
    ("Appraisal_Report.pdf", "Appraisal Report", ["Property Address", "Appraised Value", "Appraiser Name", "Date", "Signature"]),
    ("Income_Verification.pdf", "Income Verification", ["Applicant Name", "Employer", "Income", "Tax Year", "Signature"]),
    ("Bank_Statement.pdf", "Bank Statement", ["Account Holder", "Account Number", "Balance", "Statement Date", "Signature"]),
    ("Tax_Return.pdf", "Tax Return", ["Taxpayer Name", "Year", "Income", "Deductions", "Signature"]),
    ("Closing_Documents.pdf", "Closing Documents", ["Closing Date", "Property Address", "Loan Amount", "Buyer", "Seller", "Signature"]),
]


def make_pdf(path, title, fields, values):
    c = canvas.Canvas(path, pagesize=LETTER)
    _, height = LETTER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, title)
    c.setFont("Helvetica", 12)
    y = height - 120
    for field, value in zip(fields, values):
        c.drawString(72, y, f"{field}: {value}")
        y -= 28
    c.save()


def make_zip(zip_path, pdf_dir):
    with zipfile.ZipFile(zip_path, "w") as z:
        for pdf_name in os.listdir(pdf_dir):
            z.write(os.path.join(pdf_dir, pdf_name), pdf_name)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_dir = os.path.join(OUTPUT_DIR, "set_7")
    os.makedirs(pdf_dir, exist_ok=True)

    name = "Avery Morgan"
    address = "742 Evergreen Terrace"
    employer = "Globex Inc"
    seller = "Pat Rivera"
    appraiser = "Jamie Wells"

    values_by_pdf = {
        "Loan_Application.pdf": [name, address, "$385,000", "5.25%", "30", name],
        # Error 1 (deterministic): missing fees
        "Disclosure.pdf": ["03/12/2026", "$385,000 @ 5.25% for 30 years", "5.25%", "", name],
        "Credit_Report.pdf": [name, "742", "02/28/2026", "6 accounts", name],
        "Appraisal_Report.pdf": [address, "$410,000", appraiser, "03/01/2026", appraiser],
        "Income_Verification.pdf": [name, employer, "$118,400", "2025", name],
        # Error 2 (model confidence/negative): negative balance
        "Bank_Statement.pdf": [name, "28476193", "-1500", "03/10/2026", name],
        "Tax_Return.pdf": [name, "2025", "$118,400", "$8,750", name],
        "Closing_Documents.pdf": ["03/15/2026", address, "$385,000", name, seller, name],
    }

    for pdf_name, title, fields in PDF_FORMS:
        values = values_by_pdf[pdf_name]
        make_pdf(os.path.join(pdf_dir, pdf_name), title, fields, values)

    zip_path = os.path.join(OUTPUT_DIR, "home_loan_docs_7.zip")
    make_zip(zip_path, pdf_dir)

    for pdf_file in os.listdir(pdf_dir):
        os.remove(os.path.join(pdf_dir, pdf_file))
    os.rmdir(pdf_dir)

    print(zip_path)


if __name__ == "__main__":
    main()
