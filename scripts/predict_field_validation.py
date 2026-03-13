import joblib
import pandas as pd
import os
import csv
import re

def load_model(model_path):
    return joblib.load(model_path)

def load_latest_model(model_dir):
    models = [f for f in os.listdir(model_dir) if f.endswith('.joblib')]
    if not models:
        raise FileNotFoundError('No model files found.')
    latest = sorted(models)[-1]
    return joblib.load(os.path.join(model_dir, latest)), latest

def preprocess_input(field, value, doc_type):
    def is_empty(val):
        return 1 if isinstance(val, str) and val.strip() == '' else 0
    def is_negative(val):
        try:
            return float(str(val).replace('$','').replace(',','')) < 0
        except:
            return 0
    def is_nonsensical(val):
        return int(bool(re.match(r'[^\w\s]', str(val))) or bool(re.match(r'[a-zA-Z]+', str(val))) and not str(val).replace(' ','').isalnum())
    def is_out_of_range(field, val):
        try:
            if field == 'credit_score':
                v = int(val)
                return v < 300 or v > 850
            if field == 'tax_year':
                v = int(val)
                return v < 1900 or v > 2100
            if field == 'interest_rate':
                v = float(str(val).replace('%',''))
                return v < 0 or v > 20
            if field == 'loan_amount' or field == 'income' or field == 'appraised_value':
                v = float(str(val).replace('$','').replace(',',''))
                return v < 0 or v > 1000000
            return 0
        except:
            return 0
    df = pd.DataFrame([{ 'field': field, 'value': value, 'doc_type': doc_type }])
    df['is_empty'] = is_empty(value)
    df['is_negative'] = is_negative(value)
    df['is_nonsensical'] = is_nonsensical(value)
    df['is_out_of_range'] = is_out_of_range(field, value)
    from sklearn.preprocessing import OrdinalEncoder
    encoder = OrdinalEncoder()
    df[['field_encoded', 'doc_type_encoded']] = encoder.fit_transform(df[['field', 'doc_type']])
    X = df[['is_empty', 'is_negative', 'is_nonsensical', 'is_out_of_range', 'field_encoded', 'doc_type_encoded']]
    return X

def predict_validity(model, model_features, field, value, doc_type):
    X = preprocess_input(field, value, doc_type)
    # Align columns with model training
    X = X.reindex(columns=model_features, fill_value=0)
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    # Handle case where only one class is present
    if len(proba) == 1:
        prob = proba[0]
    else:
        prob = proba[int(pred)]
    return pred, prob

def log_prediction(field, value, doc_type, pred, prob, outcome):
    with open(LOG_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([field, value, doc_type, pred, prob, outcome])

CONFIDENCE_THRESHOLD = 0.8
LOG_PATH = 'ai_governance_platform/logs/prediction_log.csv'

if __name__ == '__main__':
    model_dir = 'ai_governance_platform/models/'
    model_path = os.path.join(model_dir, 'field_validation_rf_encoded_model.joblib')
    model = load_model(model_path)
    print(f'Loaded model: field_validation_rf_encoded_model.joblib')
    model_features = ['is_empty', 'is_negative', 'is_nonsensical', 'is_out_of_range', 'field_encoded', 'doc_type_encoded']

    test_cases = [
        # Valid cases
        ('loan_amount', '$250,000', 'Loan Application'),
        ('income', '$135,926', 'Income Verification'),
        ('credit_score', '750', 'Credit Report'),
        # Invalid cases
        ('loan_amount', '-50000', 'Loan Application'),
        ('income', '-135,926', 'Income Verification'),
        ('credit_score', '500', 'Credit Report'),
        ('property_address', '', 'Loan Application'),
        ('application_date', '32/13/2026', 'Loan Application'),
        ('balance', '-1000', 'Bank Statement'),
        ('account_number', '123abc', 'Bank Statement'),
        ('appraiser_name', '', 'Appraisal Report'),
        ('deductions', '-5000', 'Tax Return'),
        ('interest_rate', '-5.55%', 'Disclosure'),
        ('loan_terms', 'nonsense', 'Disclosure'),
    ]

    for field, value, doc_type in test_cases:
        pred, prob = predict_validity(model, model_features, field, value, doc_type)
        if prob >= CONFIDENCE_THRESHOLD:
            outcome = 'auto_processed'
        else:
            outcome = 'human_review'
        print(f'Test: {field} | Value: {value} | Doc: {doc_type} => Prediction: {pred} (valid=1, invalid=0), Confidence: {prob:.2f} -- {outcome}')
        log_prediction(field, value, doc_type, pred, prob, outcome)
