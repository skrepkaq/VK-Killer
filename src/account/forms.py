from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from .models import Account
from django import forms


class AccountCreateForm(UserCreationForm):
    class Meta:
        model = Account
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super(AccountCreateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'Пароль'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'Подтверждение пароля'})


class AccountLoginForm(AuthenticationForm):
    class Meta:
        model = Account

    def __init__(self, *args, **kwargs):
        super(AccountLoginForm, self).__init__(*args, **kwargs)
    username = UsernameField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин или email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
