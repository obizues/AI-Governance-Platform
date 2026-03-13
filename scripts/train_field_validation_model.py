import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import OrdinalEncoder
import joblib

# Load training data
with open('ai_governance_platform/data/field_validation_training_full.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame

df = pd.DataFrame(data)
# Add features

def is_negative(val):
    try:
        return float(str(val).replace('$','').replace(',','')) < 0
    except:
        return 0

def is_nonsensical(val):
    import re
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

def is_empty(val):
    return 1 if isinstance(val, str) and val.strip() == '' else 0

df['is_empty'] = df['value'].apply(is_empty)
df['is_negative'] = df.apply(lambda row: is_negative(row['value']), axis=1)
df['is_nonsensical'] = df.apply(lambda row: is_nonsensical(row['value']), axis=1)
df['is_out_of_range'] = df.apply(lambda row: is_out_of_range(row['field'], row['value']), axis=1)

# Ordinal encode field and doc_type
encoder = OrdinalEncoder()
df[['field_encoded', 'doc_type_encoded']] = encoder.fit_transform(df[['field', 'doc_type']])

# Use binary features + encoded features
X = df[['is_empty', 'is_negative', 'is_nonsensical', 'is_out_of_range', 'field_encoded', 'doc_type_encoded']]
y = df['valid'].astype(int)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train random forest model
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Evaluate

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# Print feature importance
print('Feature importances:', dict(zip(X.columns, clf.feature_importances_)))

# Save trained model
import os
model_dir = os.path.join('ai_governance_platform', 'models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'field_validation_rf_encoded_model.joblib')
joblib.dump(clf, model_path)
print(f'Model saved to {model_path}')
