from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from dog_shelter.models import Dog, DogImages


class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class DogCreateForm(forms.ModelForm):
    photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Dog
        fields = ('name', 'description', 'breed', 'age', 'size', 'disease_info')

    def __init__(self, *args, **kwargs):
        super(DogCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['breed'].widget.attrs.update({'class': 'form-control'})
        self.fields['age'].widget.attrs.update({'class': 'form-control'})
        self.fields['disease_info'].widget.attrs.update({'class': 'form-control'})
        self.fields['size'].widget.attrs.update({'class': 'form-control'})


class DogUpdateForm(forms.ModelForm):
    class Meta:
        model = Dog
        fields = ('name', 'description', 'breed', 'age', 'size', 'disease_info')

    def __init__(self, *args, **kwargs):
        super(DogUpdateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['breed'].widget.attrs.update({'class': 'form-control'})
        self.fields['age'].widget.attrs.update({'class': 'form-control'})
        self.fields['disease_info'].widget.attrs.update({'class': 'form-control'})
        self.fields['size'].widget.attrs.update({'class': 'form-control'})
