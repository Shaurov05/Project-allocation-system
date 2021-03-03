from django import forms
from django.contrib.auth.models import User
from .models import Student

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    Confirm_Password = forms.CharField(label='confirm your password',widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):
        cleaned_data = super(StudentForm, self).clean()
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



class StudentProfileInfoForm(forms.ModelForm):
    class Meta():
        model = Student
        fields = ('ID_Number', 'supervisor', 'session', 'department', 'profile_pic')

    def __init__(self, *args, **kwargs):
        super(StudentProfileInfoForm, self).__init__(*args, **kwargs)
        self.fields['department'].label = "Division"

