from .models import SimParamsModel
from django import forms

class SimParamsForm(forms.ModelForm):
    class Meta:
        model = SimParamsModel
        fields = ("__all__")
