from django import forms
from django.forms import inlineformset_factory
from .models import (
    BlogPost, Client,
    Invoice, Quotation, Proposal, CoverLetter, Receipt, LineItem,
)


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'category', 'excerpt', 'content',
            'featured_image', 'published',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'content':         forms.Textarea(attrs={'rows': 20}),
            'excerpt':         forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'company', 'email', 'phone', 'address']
        widgets = {'address': forms.Textarea(attrs={'rows': 3})}


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'client', 'status', 'issue_date', 'due_date',
            'tax_percent', 'discount_percent', 'notes', 'terms',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date':   forms.DateInput(attrs={'type': 'date'}),
            'notes':      forms.Textarea(attrs={'rows': 3}),
            'terms':      forms.Textarea(attrs={'rows': 3}),
        }


class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        fields = ['description', 'quantity', 'unit_price']


# Invoice line items
LineItemFormSet = inlineformset_factory(
    Invoice, LineItem,
    form=LineItemForm,
    fields=['description', 'quantity', 'unit_price'],
    extra=3,
    can_delete=True,
)

# Quotation line items
QuotationLineItemFormSet = inlineformset_factory(
    Quotation, LineItem,
    form=LineItemForm,
    fields=['description', 'quantity', 'unit_price'],
    extra=3,
    can_delete=True,
)


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'client', 'status', 'issue_date', 'valid_until',
            'tax_percent', 'discount_percent', 'notes', 'terms',
        ]
        widgets = {
            'issue_date':  forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'notes':       forms.Textarea(attrs={'rows': 3}),
            'terms':       forms.Textarea(attrs={'rows': 3}),
        }


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = [
            'client', 'service_type', 'status', 'subject',
            'executive_summary', 'problem_statement', 'proposed_solution',
            'deliverables', 'timeline', 'budget_estimate',
            'validity_days', 'terms', 'issue_date',
        ]
        widgets = {
            'issue_date':          forms.DateInput(attrs={'type': 'date'}),
            'executive_summary':   forms.Textarea(attrs={'rows': 4}),
            'problem_statement':   forms.Textarea(attrs={'rows': 4}),
            'proposed_solution':   forms.Textarea(attrs={'rows': 6}),
            'deliverables':        forms.Textarea(attrs={'rows': 5}),
            'timeline':            forms.Textarea(attrs={'rows': 4}),
            'terms':               forms.Textarea(attrs={'rows': 3}),
        }


class CoverLetterForm(forms.ModelForm):
    class Meta:
        model = CoverLetter
        fields = ['client', 'reference', 'subject', 'body', 'closing', 'issue_date']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'body':       forms.Textarea(attrs={'rows': 10}),
            'closing':    forms.Textarea(attrs={'rows': 3}),
        }


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['amount_paid', 'payment_method', 'payment_date', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes':        forms.Textarea(attrs={'rows': 3}),
        }