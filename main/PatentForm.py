from django.forms import ModelForm
import django.forms as forms
from main.models import Patent

class PatentForm(ModelForm):
    class Meta:
        model=Patent
        fields='__all__'
        widgets={
            'pub_date':forms.TextInput(attrs={'pattern':'\d{4}-\d{2}-\d{2}'}),
            'title':forms.TextInput(),
            'title_cn':forms.TextInput(),
            'pdf_file':forms.ClearableFileInput(attrs={'multiple':True}),
            'patent_type':forms.Select(attrs={'class':'form-control'})
        }

