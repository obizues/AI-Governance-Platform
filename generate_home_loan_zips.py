import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import zipfile

# Directory for output
OUTPUT_DIR = "sample_zips"
PDF_FORMS = [
    ("Loan_Application.pdf", "Home Loan Application Form", ["Applicant Name", "Property Address", "Loan Amount", "Interest Rate", "Term (years)", "Signature"]),
    ("Disclosure.pdf", "Disclosure Statement", ["Disclosure Date", "Loan Terms", "Interest Rate", "Fees", "Signature"]),
    ("Credit_Report.pdf", "Credit Report", ["Applicant Name", "Credit Score", "Report Date", "Accounts", "Signature"]),
    ("Appraisal_Report.pdf", "Appraisal Report", ["Property Address", "Appraised Value", "Appraiser Name", "Date", "Signature"]),
    ("Income_Verification.pdf", "Income Verification", ["Applicant Name", "Employer", "Income", "Tax Year", "Signature"]),
    ("Bank_Statement.pdf", "Bank Statement", ["Account Holder", "Account Number", "Balance", "Statement Date", "Signature"]),
    ("Tax_Return.pdf", "Tax Return", ["Taxpayer Name", "Year", "Income", "Deductions", "Signature"]),
    ("Closing_Documents.pdf", "Closing Documents", ["Closing Date", "Property Address", "Loan Amount", "Buyer", "Seller", "Signature"])
]

def make_pdf(path, title, fields, values):
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, title)
    c.setFont("Helvetica", 12)
    y = height - 120
    for field, value in zip(fields, values):
        c.drawString(72, y, f"{field}: {value}")
        y -= 28
    c.save()

def make_zip(zip_path, pdf_dir):
    with zipfile.ZipFile(zip_path, 'w') as z:
        for pdf_name in os.listdir(pdf_dir):
            z.write(os.path.join(pdf_dir, pdf_name), pdf_name)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    NAMES = ["Alex Smith", "Taylor Lee", "Morgan Patel", "Jordan Kim", "Chris Obermeier", "Jamie Chen", "Riley Jones", "Casey Brown", "Drew White", "Sam Green"]
    ADDRESSES = ["123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Maple Dr", "654 Cedar Ln", "987 Elm St", "246 Spruce Ct", "135 Birch Blvd", "864 Willow Way", "579 Aspen Pl"]
    EMPLOYERS = ["Acme Corp", "Globex Inc", "Initech", "Umbrella LLC", "Stark Industries", "Wayne Enterprises", "Wonka Factory", "Cyberdyne Systems", "Hooli", "Pied Piper"]
    BUYERS = NAMES
    SELLERS = NAMES
    APPRAISERS = ["Pat Miller", "Lee Johnson", "Kim Taylor", "Morgan Lee", "Alex Kim"]
    import random
    def random_money(min_val, max_val):
        return f"${random.randint(min_val, max_val):,}"
    def random_rate():
        return f"{random.uniform(2.5, 7.0):.2f}%"
    def random_year():
        return str(random.randint(2018, 2026))
    def random_date():
        return f"{random.randint(1,12):02d}/{random.randint(1,28):02d}/{random_year()}"
    def random_account():
        return f"{random.randint(10000000,99999999)}"
    def random_credit_score():
        return str(random.randint(620, 850))
    def random_income():
        return random_money(40000, 200000)
    def random_deductions():
        return random_money(1000, 20000)
    for i in range(1, 6):
        pdf_dir = os.path.join(OUTPUT_DIR, f"set_{i}")
        os.makedirs(pdf_dir, exist_ok=True)
        name = NAMES[i % len(NAMES)]
        address = ADDRESSES[i % len(ADDRESSES)]
        employer = EMPLOYERS[i % len(EMPLOYERS)]
        buyer = name  # Buyer is always the applicant/owner
        seller = SELLERS[(i+2) % len(SELLERS)]
        appraiser = APPRAISERS[i % len(APPRAISERS)]
        for pdf_name, title, fields in PDF_FORMS:
            if pdf_name == "Loan_Application.pdf":
                values = [name, address, random_money(100000, 900000), random_rate(), str(random.randint(10, 30)), name]
            elif pdf_name == "Disclosure.pdf":
                values = [random_date(), f"{random_money(100000,900000)} @ {random_rate()} for {random.randint(10,30)} years", random_rate(), random_money(500, 5000), name]
            elif pdf_name == "Credit_Report.pdf":
                values = [name, random_credit_score(), random_date(), f"{random.randint(3,10)} accounts", name]
            elif pdf_name == "Appraisal_Report.pdf":
                values = [address, random_money(100000,900000), appraiser, random_date(), appraiser]
            elif pdf_name == "Income_Verification.pdf":
                values = [name, employer, random_income(), random_year(), name]
            elif pdf_name == "Bank_Statement.pdf":
                values = [name, random_account(), random_money(1000, 100000), random_date(), name]
            elif pdf_name == "Tax_Return.pdf":
                values = [name, random_year(), random_income(), random_deductions(), name]
            elif pdf_name == "Closing_Documents.pdf":
                values = [random_date(), address, random_money(100000,900000), name, seller, name]
            else:
                values = ["Sample"] * len(fields)
            pdf_path = os.path.join(pdf_dir, pdf_name)
            make_pdf(pdf_path, title, fields, values)
        zip_path = os.path.join(OUTPUT_DIR, f"home_loan_docs_{i}.zip")
        make_zip(zip_path, pdf_dir)
        for pdf_file in os.listdir(pdf_dir):
            os.remove(os.path.join(pdf_dir, pdf_file))
        os.rmdir(pdf_dir)
    print("Created 5 zip files with home loan PDFs.")

if __name__ == "__main__":
    main()
