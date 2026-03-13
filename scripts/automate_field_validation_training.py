import os
import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DATA_PATH = 'ai_governance_platform/data/field_validation_training_full.json'
MODEL_DIR = 'ai_governance_platform/models/'
LOG_PATH = 'ai_governance_platform/logs/model_training.log'

os.makedirs(MODEL_DIR, exist_ok=True)

def log_event(event):
    with open(LOG_PATH, 'a') as log_file:
        log_file.write(f'{datetime.now().isoformat()} - {event}\n')

def get_version():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def train_and_save():
    log_event('Training started')
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    X = pd.get_dummies(df[['field', 'value', 'doc_type']])
    y = df['valid'].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred)
    log_event('Training completed')
    log_event(f'Classification report:\n{report}')
    version = get_version()
    model_path = os.path.join(MODEL_DIR, f'field_validation_rf_model_{version}.joblib')
    joblib.dump(clf, model_path)
    log_event(f'Model saved: {model_path}')
    return model_path, report

if __name__ == '__main__':
    model_path, report = train_and_save()
    print(f'Model saved to {model_path}')
    print(report)
