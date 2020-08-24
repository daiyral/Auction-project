from django.forms import ModelForm
from django import forms
from .models import Listing,Bid,Comment


class NewListForm(forms.ModelForm):
    class Meta:
        model=Listing
        fields=[
            'name',
            'price',
            'description',
            'tag',
            'condition',
            'image'
        ]
        widgets= {
           'name':forms.TextInput(attrs={'class':'form-control'}),
           'price':forms.TextInput(attrs={'class':'form-control'}),
          'description':forms.Textarea(attrs={'class':'form-control'}),
           'tag':forms.SelectMultiple(attrs={'class':'form-control'}),
           'condition':forms.Select(attrs={'class':'form-control'}),
           'image':forms.FileInput(attrs={'class':'custom-file'})
       }

    



       