from django import forms

OSD_CHOICES = ((0,'osd.0'),(1,'osd.1'),(2,'osd.2'),(3,'osd.3'),(4,'osd.4'),(5,'osd.5') )
FILTER_CHOICES = ((0,'all'),(5,'last 5'),(10,'last 10'),(20,'last 20'),(30,'last 30'),(50, 'last 50'),(100, 'last 100') )
class LoginForm(forms.Form):
    """ Login form """
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ChangePasswordForm(forms.Form):
    oldpassword = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    verifypassword = forms.CharField(widget=forms.PasswordInput)

class ReweightOsdForm(forms.Form):
    osd_id = forms.ChoiceField(required=True, choices=OSD_CHOICES,widget = forms.Select( ))
    new_weight = forms.DecimalField(required=True ,min_value =0.0, max_value=1.0, decimal_places=2,max_digits=3 )

class ChartForm(forms.Form):
    filter_choice = forms.ChoiceField(required=True, choices=FILTER_CHOICES,widget = forms.Select( ))

