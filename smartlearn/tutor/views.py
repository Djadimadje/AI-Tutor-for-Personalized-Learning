import os
import joblib
import numpy as np
import pandas as pd
from django.shortcuts import render

# Load model and encoders once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, 'model/ai_recommender.pkl'))
subject_encoder = joblib.load(os.path.join(BASE_DIR, 'model/subject_encoder.pkl'))
difficulty_encoder = joblib.load(os.path.join(BASE_DIR, 'model/difficulty_encoder.pkl'))
output_encoder = joblib.load(os.path.join(BASE_DIR, 'model/output_encoder.pkl'))

def home(request):
    result = None

    if request.method == 'POST':
        try:
            subject = subject_encoder.transform([request.POST['subject']])[0]
            score = float(request.POST['score'])
            difficulty = difficulty_encoder.transform([request.POST['difficulty']])[0]

            df = pd.DataFrame([{
                'Subject': subject,
                'Score': score,
                'Difficulty': difficulty
            }])

            prediction = model.predict(df)
            result = output_encoder.inverse_transform(prediction)[0]

        except Exception as e:
            result = f"Error: {e}"

    return render(request, 'tutor/home.html', {'result': result})
