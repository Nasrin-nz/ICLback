from django import forms
from .models import TemporaryUser
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Invalid login credentials')
        return self.cleaned_data

    def get_user(self):
        return self.user


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = TemporaryUser
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email, is_active=True).exists():
            user = User.objects.get(email=email)
            reset_password_url = reverse('password_reset')
            raise forms.ValidationError(
                format_html(
                    'An account with this email already exists. Your username is <strong>{}</strong>. '
                    'If you forgot your password, you can <a href="{}">reset it here</a>.',
                    user.username,
                    reset_password_url
                )
            )
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username, is_active=True).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different username.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        try:
            temp_user = TemporaryUser.objects.get(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email']
            )
        except TemporaryUser.DoesNotExist:
            temp_user = super().save(commit=False)

        temp_user.password = self.cleaned_data["password1"]
        if commit:
            temp_user.save()
        return temp_user
