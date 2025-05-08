import os
import joblib
import pandas as pd
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Prediction


# Custom form for registration
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default help text for password fields
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        # Customize error messages
        self.fields['password1'].error_messages = {
            'required': 'Password is required.',
            'password_too_short': 'Password must be at least 8 characters long.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Please confirm your password.',
            'password_mismatch': 'Passwords do not match.',
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # after registering, redirect to dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'tutor/register.html', {'form': form})


def landing(request):
    return render(request, 'tutor/landing.html')


# Load model and encoders once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, 'model/ai_recommender.pkl'))
subject_encoder = joblib.load(os.path.join(BASE_DIR, 'model/subject_encoder.pkl'))
difficulty_encoder = joblib.load(os.path.join(BASE_DIR, 'model/difficulty_encoder.pkl'))
output_encoder = joblib.load(os.path.join(BASE_DIR, 'model/output_encoder.pkl'))


@login_required
def predict(request):
    result = None
    if request.method == 'POST':
        try:
            subject = request.POST['subject']
            score = float(request.POST['score'])
            difficulty = request.POST['difficulty']

            input_df = pd.DataFrame([{
                'Subject': subject_encoder.transform([subject])[0],
                'Score': score,
                'Difficulty': difficulty_encoder.transform([difficulty])[0]
            }])

            prediction = model.predict(input_df)
            result = output_encoder.inverse_transform(prediction)[0]

            # Store result in DB if user is logged in (Phase 4 ready)
            Prediction.objects.create(
                user=request.user,
                subject=subject,
                score=score,
                difficulty=difficulty,
                recommendation=result
            )

        except Exception as e:
            result = f"Error: {e}"

    return render(request, 'tutor/predict.html', {'result': result})


@login_required
def dashboard(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tutor/dashboard.html', {'predictions': predictions})