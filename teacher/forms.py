from django import forms
from django.contrib.auth.models import User
from .models import Teacher

class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    Confirm_Password = forms.CharField(label='confirm your password',widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):
        cleaned_data = super(TeacherForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("Confirm_Password")

        if password == '':
            raise forms.ValidationError(
                "Please, Enter a valid password"
            )

        if password != confirm_password:
            print(password)
            print(confirm_password)
            print("do not match")
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

        if not cleaned_data.get("email"):
            raise forms.ValidationError(
                "Please Enter valid Email address"
            )


class TeacherProfileInfoForm(forms.ModelForm):
    class Meta():
        model = Teacher
        fields = ('ID_Number', 'department', 'academic_rank', 'portfolio_site', 'profile_pic')

    def __init__(self, *args, **kwargs):
        super(TeacherProfileInfoForm, self).__init__(*args, **kwargs)
        self.fields['department'].label = "Division"

