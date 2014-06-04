from django import forms

from .models import Member
from .models import SPECIALIZATION, PAYMENTS

class MemberForm(forms.ModelForm):
  
  class Meta:
    model = Member
    exclude = ('courses',)