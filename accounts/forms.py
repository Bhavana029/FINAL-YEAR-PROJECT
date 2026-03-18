from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username',
            'id': 'id_username',
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'id': 'id_email',
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'id': 'id_password1',
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'id': 'id_password2',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # ── Username: letters only, no numbers ──
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        if re.search(r'\d', username):
            raise forms.ValidationError("Username must not contain numbers.")
        if not re.match(r'^[a-zA-Z_]+$', username):
            raise forms.ValidationError("Username can only contain letters and underscores.")
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters.")
        return username

    # ── Email: must be unique ──
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    # ── Password: min 8 chars, at least 1 letter + 1 number ──
    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[a-zA-Z]', password):
            raise forms.ValidationError("Password must contain at least one letter.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
        return password

    # ── Passwords match ──
    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2