from django import forms
from .models import HistoryRecord,TransferRecord

class HistoryRecordForm(forms.ModelForm):
    class Meta:
        model = HistoryRecord
        exclude = ['created_date', 'updated_date', 'username']

class TransferRecordForm(forms.ModelForm):
    class Meta:
        model = TransferRecord
        exclude = ['created_date', 'updated_date', 'currency', 'username']