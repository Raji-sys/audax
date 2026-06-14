from django.contrib import admin
from .models import *


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'published', 'published_at']
    list_filter   = ['published', 'category']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ['name', 'company', 'email', 'phone']
    search_fields = ['name', 'company', 'email']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'status', 'issue_date', 'due_date']
    list_filter  = ['status']
    inlines      = [LineItemInline]


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'client', 'status', 'issue_date', 'valid_until']
    list_filter  = ['status']
    inlines      = [LineItemInline]


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display  = ['proposal_number', 'client', 'service_type', 'status', 'issue_date']
    list_filter   = ['status', 'service_type']
    search_fields = ['subject', 'client__name']


@admin.register(CoverLetter)
class CoverLetterAdmin(admin.ModelAdmin):
    list_display = ['subject', 'client', 'issue_date']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'invoice', 'amount_paid', 'payment_date']


@admin.register(ServiceSEO)
class ServiceSEOAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'service_slug', 'updated_at']



@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'organisation', 'email', 'phone', 'system_type', 'created_at', 'is_read')
    list_filter = ('is_read', 'system_type', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'organisation', 'details')
    readonly_fields = ('created_at','details','system_type','phone','email','organisation','first_name','last_name')