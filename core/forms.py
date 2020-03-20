from django import forms


class ReportForm(forms.Form):
    points_file = forms.FileField()
    infected_at = forms.DateField()
    is_verified = forms.BooleanField(required=False)


class CheckForm(forms.Form):
    points_file = forms.FileField()
