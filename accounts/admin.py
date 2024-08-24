

from django import forms
from django.contrib import admin
from .models import TemporaryUser

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class CustomUserAdmin(BaseUserAdmin):
    form = UserAdminForm

    # If you want to add email to the list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

print("CustomUserAdmin is being registered")

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class TemporaryUserAdminForm(forms.ModelForm):
    class Meta:
        model = TemporaryUser
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if TemporaryUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if TemporaryUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

class TemporaryUserAdmin(admin.ModelAdmin):
    form = TemporaryUserAdminForm
    list_display = ('id', 'username', 'email', 'verification_code', 'created_at')

    def save_model(self, request, obj, form, change):
        if not obj.email:
            raise ValueError("Email is required")
        super().save_model(request, obj, form, change)

admin.site.register(TemporaryUser, TemporaryUserAdmin)