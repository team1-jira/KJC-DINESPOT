from django import forms
from main.models import User,Block,Canteen,Contact
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'pieces', 'category', 'instructions', 'image', 'labels']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            # 'instructions': forms.Textarea(attrs={'rows': 2}),
        }
class CanteenForm(forms.ModelForm):
    class Meta:
        model = Canteen
        fields = ['canteen_name', 'block', 'caterer']  # Fields that should be updated or added

    block = forms.ModelChoiceField(queryset=Block.objects.all(), required=True)
    caterer = forms.ModelChoiceField(queryset=User.objects.filter(role='caterer'), required=True)




from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'maxlength': '10'}),
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be exactly 10 digits.',
                code='invalid_phone'
            )
        ]
    )

    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=6,
        help_text="Password must be at least 6 characters."
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'role', 'phone']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        import re
        if not re.match(r'^[A-Za-z ]+$', name):
            raise ValidationError("Name must contain only letters and spaces.")
        return name
    


    def clean_email(self):
        email = self.cleaned_data.get('email')
        validator = EmailValidator(message="Enter a valid email address.")
        validator(email)

        qs = User.objects.filter(email=email)
        if self.instance.pk:
           qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
           raise ValidationError("This email is already in use.")

        return email
    


    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters.")
        return password

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise ValidationError("Role is required.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['name', 'email', 'password', 'role', 'phone']

#     password = forms.CharField(widget=forms.PasswordInput())

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = ['block_name', 'description']
        
   
    block_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'px-4 py-2 border border-gray-400 rounded w-full', 'placeholder': 'Enter Block Name'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'px-4 py-2 border border-gray-400 rounded w-full', 'placeholder': 'Enter Block Description', 'rows': 4}),
        required=False
    )