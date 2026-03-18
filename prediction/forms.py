from django import forms

class PredictionForm(forms.Form):
    fundus_image = forms.ImageField()
    sclera_image = forms.ImageField()
