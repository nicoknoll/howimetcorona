from django import forms


class BaseFileForm(forms.Form):
    # we try to minify the file to only submit the data
    points_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'required': 'required'}),
        label="Location History File (.json)"
    )
    points_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        points_file = self.cleaned_data.get('points_file')
        points_data = self.cleaned_data.get('points_data')

        if not points_file and not points_data:
            raise forms.ValidationError({'points_file': 'File is required.'})

        return self.cleaned_data


class ReportForm(BaseFileForm):
    infected_at = forms.DateField(widget=forms.TextInput(attrs={
        'placeholder': 'YYYY-MM-DD',
        'pattern': '[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}',
        'title': 'YYYY-MM-DD'
    }))
    is_verified = forms.BooleanField(required=False)


class CheckForm(BaseFileForm):
    pass