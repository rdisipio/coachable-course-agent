import json
import pandas as pd

def load_courses(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_esco_skills(path):
    return pd.read_csv(path)  # Expecting columns: name, uri
