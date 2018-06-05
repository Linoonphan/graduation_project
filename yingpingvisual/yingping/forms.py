from django import forms
class MovieForm(forms.Form):
    moviename = forms.CharField(max_length=100)
class MovieTypeForm(forms.Form):
    movietype = forms.CharField(max_length=100)