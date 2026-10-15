from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors never see or fill this field, simple bots do.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))

    class Meta:
        model = ContactMessage
        fields = ('full_name', 'email', 'subject', 'message')
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'autocomplete': 'email'}),
            'subject': forms.TextInput(attrs={'placeholder': 'How can we help?'}),
            'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Write your message here'}),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Please write at least 10 characters.')
        return message

    def clean_subject(self):
        subject = self.cleaned_data['subject'].strip()
        if '\n' in subject or '\r' in subject:
            raise forms.ValidationError('The subject must be a single line.')
        return subject


class ReplyForm(forms.Form):
    reply_text = forms.CharField(
        label='Your reply', max_length=10000, min_length=2,
        widget=forms.Textarea(attrs={'rows': 8}),
    )
