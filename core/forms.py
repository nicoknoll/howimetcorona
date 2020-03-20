from django import forms


class ReportForm(forms.Form):
    points_file = forms.FileField()
    infected_at = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    is_verified = forms.BooleanField(required=False)


class CheckForm(forms.Form):
    points_file = forms.FileField()
