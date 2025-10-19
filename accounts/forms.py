# accounts/forms.py
from django import forms
from .models import User

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'input-field'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password', 'phone', 'address', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class':'input-field'}),
            'email': forms.EmailInput(attrs={'class':'input-field'}),
            'role': forms.Select(attrs={'class':'input-field'}),
            'phone': forms.TextInput(attrs={'class':'input-field'}),
            'address': forms.Textarea(attrs={'class':'input-field', 'rows':3}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # hash password
        if commit:
            user.save()
        return user
