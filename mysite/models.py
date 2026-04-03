from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid


# ─────────────────────────────────────────────
#  BLOG
# ─────────────────────────────────────────────

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Blog Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title           = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True, blank=True)
    category        = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    excerpt         = models.TextField(max_length=300, blank=True, help_text="Short summary shown in listings")
    content         = models.TextField()
    featured_image  = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    published       = models.BooleanField(default=False)
    published_at    = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    # SEO
    meta_title       = models.CharField(max_length=60, blank=True, help_text="Defaults to post title if empty")
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=255, blank=True, help_text="Comma-separated, e.g. EMR, Django, Nigeria")

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        if not self.meta_title:
            self.meta_title = self.title[:60]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────
#  CLIENTS
# ─────────────────────────────────────────────

class Client(models.Model):
    name        = models.CharField(max_length=200)
    company     = models.CharField(max_length=200, blank=True)
    email       = models.EmailField(blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    address     = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


# ─────────────────────────────────────────────
#  DOCUMENT SHARED PIECES
# ─────────────────────────────────────────────

class LineItem(models.Model):
    """Reusable line item — attached to Invoice or Quotation via FK."""
    description = models.CharField(max_length=300)
    quantity    = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2)

    # Generic FK targets — set only one
    invoice    = models.ForeignKey('Invoice',   on_delete=models.CASCADE, null=True, blank=True, related_name='items')
    quotation  = models.ForeignKey('Quotation', on_delete=models.CASCADE, null=True, blank=True, related_name='items')

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description


# ─────────────────────────────────────────────
#  INVOICE
# ─────────────────────────────────────────────

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft',   'Draft'),
        ('sent',    'Sent'),
        ('paid',    'Paid'),
        ('overdue', 'Overdue'),
        ('void',    'Void'),
    ]

    client           = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    invoice_number   = models.CharField(max_length=50, unique=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date       = models.DateField(default=timezone.now)
    due_date         = models.DateField(null=True, blank=True)
    tax_percent      = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="e.g. 7.5 for 7.5% VAT")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes            = models.TextField(blank=True)
    terms            = models.TextField(blank=True, help_text="Payment terms and conditions")
    created_at       = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            count = Invoice.objects.count() + 1
            self.invoice_number = f"INV-{timezone.now().year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())

    @property
    def discount_amount(self):
        return self.subtotal * (self.discount_percent / 100)

    @property
    def tax_amount(self):
        return (self.subtotal - self.discount_amount) * (self.tax_percent / 100)

    @property
    def total(self):
        return self.subtotal - self.discount_amount + self.tax_amount

    def __str__(self):
        return f"{self.invoice_number} — {self.client}"


# ─────────────────────────────────────────────
#  QUOTATION
# ─────────────────────────────────────────────

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('sent',     'Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired',  'Expired'),
    ]

    client            = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='quotations')
    quotation_number  = models.CharField(max_length=50, unique=True, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date        = models.DateField(default=timezone.now)
    valid_until       = models.DateField(null=True, blank=True)
    tax_percent       = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_percent  = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes             = models.TextField(blank=True)
    terms             = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            count = Quotation.objects.count() + 1
            self.quotation_number = f"QUO-{timezone.now().year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())

    @property
    def discount_amount(self):
        return self.subtotal * (self.discount_percent / 100)

    @property
    def tax_amount(self):
        return (self.subtotal - self.discount_amount) * (self.tax_percent / 100)

    @property
    def total(self):
        return self.subtotal - self.discount_amount + self.tax_amount

    def __str__(self):
        return f"{self.quotation_number} — {self.client}"


# ─────────────────────────────────────────────
#  PROPOSAL
# ─────────────────────────────────────────────

class Proposal(models.Model):
    STATUS_CHOICES = [
        ('draft',    'Draft'),
        ('sent',     'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    SERVICE_CHOICES = [
        ('emr',       'Electronic Medical Records'),
        ('edms',      'Document Management'),
        ('hrms',      'Human Resources'),
        ('inventory', 'Inventory Management'),
        ('pharmacy',  'Pharmacy Management'),
        ('erp',       'Enterprise Resource Planning'),
        ('custom',    'Custom Solution'),
    ]

    client          = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='proposals')
    proposal_number = models.CharField(max_length=50, unique=True, blank=True)
    service_type    = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='custom')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subject         = models.CharField(max_length=300)
    executive_summary   = models.TextField(help_text="High-level overview of the proposal")
    problem_statement   = models.TextField(help_text="What problem are you solving for this client?")
    proposed_solution   = models.TextField(help_text="Your approach and solution")
    deliverables        = models.TextField(help_text="What you will deliver, one per line")
    timeline            = models.TextField(blank=True, help_text="Project phases and timeline")
    budget_estimate     = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    validity_days       = models.PositiveIntegerField(default=30)
    terms               = models.TextField(blank=True)
    issue_date          = models.DateField(default=timezone.now)
    created_at          = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.proposal_number:
            count = Proposal.objects.count() + 1
            self.proposal_number = f"PROP-{timezone.now().year}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.proposal_number} — {self.subject}"


# ─────────────────────────────────────────────
#  COVER LETTER
# ─────────────────────────────────────────────

class CoverLetter(models.Model):
    client      = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cover_letters')
    subject     = models.CharField(max_length=300)
    body        = models.TextField()
    closing     = models.TextField(blank=True, default="We look forward to your positive response.")
    issue_date  = models.DateField(default=timezone.now)
    created_at  = models.DateTimeField(auto_now_add=True)
    reference   = models.CharField(max_length=100, blank=True, help_text="e.g. Re: EMR Implementation Proposal")

    def __str__(self):
        return f"Cover Letter — {self.client} ({self.issue_date})"


# ─────────────────────────────────────────────
#  RECEIPT
# ─────────────────────────────────────────────

class Receipt(models.Model):
    invoice         = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='receipt')
    amount_paid     = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method  = models.CharField(max_length=100, blank=True, help_text="e.g. Bank Transfer, Cash")
    payment_date    = models.DateField(default=timezone.now)
    receipt_number  = models.CharField(max_length=50, unique=True, blank=True)
    notes           = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            count = Receipt.objects.count() + 1
            self.receipt_number = f"REC-{timezone.now().year}-{count:04d}"
        # Mark invoice as paid
        self.invoice.status = 'paid'
        self.invoice.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} — {self.invoice}"


# ─────────────────────────────────────────────
#  SITE SEO (per-service pages)
# ─────────────────────────────────────────────

class ServiceSEO(models.Model):
    """Manage SEO meta for each service page dynamically."""
    service_slug     = models.SlugField(unique=True, help_text="e.g. emr, edms, hrms, inventory")
    service_name     = models.CharField(max_length=100)
    meta_title       = models.CharField(max_length=60)
    meta_description = models.CharField(max_length=160)
    meta_keywords    = models.CharField(max_length=255)
    og_title         = models.CharField(max_length=100, blank=True, help_text="Open Graph title for social sharing")
    og_description   = models.TextField(blank=True)
    schema_type      = models.CharField(max_length=50, default='SoftwareApplication')
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service SEO"
        verbose_name_plural = "Service SEO"

    def __str__(self):
        return f"SEO: {self.service_name}"