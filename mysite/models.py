from django.db import models
from django.utils.text import slugify
from django.utils import timezone


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
    title            = models.CharField(max_length=200)
    slug             = models.SlugField(unique=True, blank=True)
    category         = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    excerpt          = models.TextField(max_length=300, blank=True)
    content          = models.TextField()
    featured_image   = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    published        = models.BooleanField(default=False)
    published_at     = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    meta_title       = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=255, blank=True)
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


class Client(models.Model):
    name       = models.CharField(max_length=200)
    company    = models.CharField(max_length=200, blank=True)
    email      = models.EmailField(blank=True)
    phone      = models.CharField(max_length=30, blank=True)
    address    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


def _make_ref(prefix, model_class):
    """Generates PRPSL/01/25 style references."""
    year  = timezone.now().strftime('%y')
    count = model_class.objects.count() + 1
    seq   = str(count).zfill(2)
    return f"{prefix}/{seq}/{year}"


class LineItem(models.Model):
    description = models.CharField(max_length=300)
    quantity    = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2)
    invoice     = models.ForeignKey('Invoice',   on_delete=models.CASCADE, null=True, blank=True, related_name='items')
    quotation   = models.ForeignKey('Quotation', on_delete=models.CASCADE, null=True, blank=True, related_name='items')
    @property
    def total(self):
        return self.quantity * self.unit_price
    def __str__(self):
        return self.description


class Invoice(models.Model):
    STATUS_CHOICES = [('draft','Draft'),('sent','Sent'),('paid','Paid'),('overdue','Overdue'),('void','Void')]
    client           = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    invoice_number   = models.CharField(max_length=50, unique=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date       = models.DateField(default=timezone.now)
    due_date         = models.DateField(null=True, blank=True)
    tax_percent      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes            = models.TextField(blank=True)
    terms            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = _make_ref('INV', Invoice)
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


class Quotation(models.Model):
    STATUS_CHOICES = [('draft','Draft'),('sent','Sent'),('accepted','Accepted'),('declined','Declined'),('expired','Expired')]
    client           = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='quotations')
    quotation_number = models.CharField(max_length=50, unique=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date       = models.DateField(default=timezone.now)
    valid_until      = models.DateField(null=True, blank=True)
    tax_percent      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes            = models.TextField(blank=True)
    terms            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = _make_ref('QUO', Quotation)
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


class Proposal(models.Model):
    STATUS_CHOICES  = [('draft','Draft'),('sent','Sent'),('accepted','Accepted'),('rejected','Rejected')]
    SERVICE_CHOICES = [
        ('emr','Electronic Medical Records'),('edms','Document Management'),
        ('hrms','Human Resources'),('inventory','Inventory Management'),
        ('pharmacy','Pharmacy Management'),('erp','Enterprise Resource Planning'),
        ('custom','Custom Solution'),
    ]
    client            = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='proposals')
    proposal_number   = models.CharField(max_length=50, unique=True, blank=True)
    service_type      = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='custom')
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subject           = models.CharField(max_length=300)
    executive_summary = models.TextField()
    problem_statement = models.TextField()
    proposed_solution = models.TextField()
    deliverables      = models.TextField(help_text="One deliverable per line")
    timeline          = models.TextField(blank=True)
    budget_estimate   = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    validity_days     = models.PositiveIntegerField(default=30)
    terms             = models.TextField(blank=True)
    issue_date        = models.DateField(default=timezone.now)
    created_at        = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.proposal_number:
            self.proposal_number = _make_ref('PRPSL', Proposal)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.proposal_number} — {self.subject}"


class CoverLetter(models.Model):
    client     = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cover_letters')
    reference  = models.CharField(max_length=100, blank=True)
    letter_ref = models.CharField(max_length=50, unique=True, blank=True)
    subject    = models.CharField(max_length=300)
    body       = models.TextField()
    closing    = models.TextField(blank=True, default="We look forward to your positive response.")
    issue_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.letter_ref:
            self.letter_ref = _make_ref('CVL', CoverLetter)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Cover Letter — {self.client} ({self.issue_date})"


class Receipt(models.Model):
    invoice        = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='receipt')
    amount_paid    = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=100, blank=True)
    payment_date   = models.DateField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    notes          = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = _make_ref('REC', Receipt)
        self.invoice.status = 'paid'
        self.invoice.save()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.receipt_number} — {self.invoice}"


class ServiceSEO(models.Model):
    service_slug     = models.SlugField(unique=True)
    service_name     = models.CharField(max_length=100)
    meta_title       = models.CharField(max_length=60)
    meta_description = models.CharField(max_length=160)
    meta_keywords    = models.CharField(max_length=255)
    og_title         = models.CharField(max_length=100, blank=True)
    og_description   = models.TextField(blank=True)
    updated_at       = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "Service SEO"
    def __str__(self):
        return f"SEO: {self.service_name}"
