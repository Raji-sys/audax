from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.forms import inlineformset_factory
from django.http import HttpResponse
from .models import (
    BlogPost, BlogCategory,
    Client, Invoice, Quotation, Proposal, CoverLetter, Receipt,
    LineItem, ServiceSEO,
)
from .forms import (
    BlogPostForm, ClientForm,
    InvoiceForm, LineItemFormSet,
    QuotationForm, QuotationLineItemFormSet,
    ProposalForm, CoverLetterForm, ReceiptForm,
)


# ─────────────────────────────────────────────
#  PUBLIC — INDEX
# ─────────────────────────────────────────────

def index(request):
    posts = BlogPost.objects.filter(published=True).order_by('-published_at')[:3]
    seo   = ServiceSEO.objects.all()
    return render(request, 'mysite/index.html', {'posts': posts, 'seo': seo})


# ─────────────────────────────────────────────
#  PUBLIC — BLOG
# ─────────────────────────────────────────────

def blog_list(request):
    posts = BlogPost.objects.filter(published=True).order_by('-published_at')
    categories = BlogCategory.objects.all()
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    return render(request, 'mysite/blog/list.html', {
        'posts': posts,
        'categories': categories,
        'active_category': category_slug,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    related = BlogPost.objects.filter(
        published=True, category=post.category
    ).exclude(pk=post.pk)[:3]
    return render(request, 'mysite/blog/detail.html', {
        'post': post,
        'related': related,
    })


# ─────────────────────────────────────────────
#  HIDDEN LOGIN — no link shown publicly
#  Access via /x/login/  (change this to whatever secret path you want)
# ─────────────────────────────────────────────

def portal_login(request):
    if request.user.is_authenticated:
        return redirect('portal_dashboard')
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user:
            login(request, user)
            return redirect('portal_dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'mysite/portal/login.html')


def portal_logout(request):
    logout(request)
    return redirect('index')


# ─────────────────────────────────────────────
#  PORTAL — DASHBOARD
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def portal_dashboard(request):
    return render(request, 'mysite/portal/dashboard.html', {
        'invoice_count':   Invoice.objects.count(),
        'quotation_count': Quotation.objects.count(),
        'proposal_count':  Proposal.objects.count(),
        'post_count':      BlogPost.objects.count(),
        'client_count':    Client.objects.count(),
        'recent_invoices': Invoice.objects.order_by('-created_at')[:5],
        'draft_posts':     BlogPost.objects.filter(published=False).order_by('-created_at')[:5],
    })


# ─────────────────────────────────────────────
#  PORTAL — BLOG CRUD
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def blog_manage(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'mysite/portal/blog/list.html', {'posts': posts})


@login_required(login_url='portal_login')
def blog_create(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Post created.')
        return redirect('blog_manage')
    return render(request, 'mysite/portal/blog/form.html', {'form': form, 'title': 'New Post'})


@login_required(login_url='portal_login')
def blog_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    form = BlogPostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        messages.success(request, 'Post updated.')
        return redirect('blog_manage')
    return render(request, 'mysite/portal/blog/form.html', {'form': form, 'title': 'Edit Post'})


@login_required(login_url='portal_login')
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('blog_manage')
    return render(request, 'mysite/portal/confirm_delete.html', {'object': post, 'type': 'Blog Post'})


# ─────────────────────────────────────────────
#  PORTAL — CLIENTS
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def client_list(request):
    clients = Client.objects.all().order_by('-created_at')
    return render(request, 'mysite/portal/clients/list.html', {'clients': clients})


@login_required(login_url='portal_login')
def client_create(request):
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Client saved.')
        return redirect('client_list')
    return render(request, 'mysite/portal/clients/form.html', {'form': form, 'title': 'New Client'})


@login_required(login_url='portal_login')
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, 'Client updated.')
        return redirect('client_list')
    return render(request, 'mysite/portal/clients/form.html', {'form': form, 'title': 'Edit Client'})


# ─────────────────────────────────────────────
#  PORTAL — INVOICE CRUD
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def invoice_list(request):
    invoices = Invoice.objects.select_related('client').order_by('-created_at')
    return render(request, 'mysite/portal/invoices/list.html', {'invoices': invoices})


@login_required(login_url='portal_login')
def invoice_create(request):
    form = InvoiceForm(request.POST or None)
    formset = LineItemFormSet(request.POST or None, prefix='items')
    if form.is_valid() and formset.is_valid():
        invoice = form.save()
        items = formset.save(commit=False)
        for item in items:
            item.invoice = invoice
            item.save()
        messages.success(request, f'{invoice.invoice_number} created.')
        return redirect('invoice_list')
    return render(request, 'mysite/portal/invoices/form.html', {
        'form': form, 'formset': formset, 'title': 'New Invoice'
    })


@login_required(login_url='portal_login')
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'mysite/portal/invoices/detail.html', {'invoice': invoice})


@login_required(login_url='portal_login')
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(request.POST or None, instance=invoice)
    formset = LineItemFormSet(request.POST or None, prefix='items', instance=invoice)
    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, 'Invoice updated.')
        return redirect('invoice_list')
    return render(request, 'mysite/portal/invoices/form.html', {
        'form': form, 'formset': formset, 'title': 'Edit Invoice'
    })


@login_required(login_url='portal_login')
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Invoice deleted.')
        return redirect('invoice_list')
    return render(request, 'mysite/portal/confirm_delete.html', {'object': invoice, 'type': 'Invoice'})


# ─────────────────────────────────────────────
#  PORTAL — QUOTATION CRUD
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def quotation_list(request):
    quotations = Quotation.objects.select_related('client').order_by('-created_at')
    return render(request, 'mysite/portal/quotations/list.html', {'quotations': quotations})


@login_required(login_url='portal_login')
def quotation_create(request):
    form = QuotationForm(request.POST or None)
    formset = QuotationLineItemFormSet(request.POST or None, prefix='items')
    if form.is_valid() and formset.is_valid():
        quotation = form.save()
        items = formset.save(commit=False)
        for item in items:
            item.quotation = quotation
            item.save()
        messages.success(request, f'{quotation.quotation_number} created.')
        return redirect('quotation_list')
    return render(request, 'mysite/portal/quotations/form.html', {
        'form': form, 'formset': formset, 'title': 'New Quotation'
    })


@login_required(login_url='portal_login')
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    return render(request, 'mysite/portal/quotations/detail.html', {'quotation': quotation})


@login_required(login_url='portal_login')
def quotation_edit(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    form = QuotationForm(request.POST or None, instance=quotation)
    formset = QuotationLineItemFormSet(request.POST or None, prefix='items', instance=quotation)
    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, 'Quotation updated.')
        return redirect('quotation_list')
    return render(request, 'mysite/portal/quotations/form.html', {
        'form': form, 'formset': formset, 'title': 'Edit Quotation'
    })


@login_required(login_url='portal_login')
def quotation_delete(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == 'POST':
        quotation.delete()
        messages.success(request, 'Quotation deleted.')
        return redirect('quotation_list')
    return render(request, 'mysite/portal/confirm_delete.html', {'object': quotation, 'type': 'Quotation'})


# ─────────────────────────────────────────────
#  PORTAL — PROPOSAL CRUD
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def proposal_list(request):
    proposals = Proposal.objects.select_related('client').order_by('-created_at')
    return render(request, 'mysite/portal/proposals/list.html', {'proposals': proposals})


@login_required(login_url='portal_login')
def proposal_create(request):
    form = ProposalForm(request.POST or None)
    if form.is_valid():
        proposal = form.save()
        messages.success(request, f'{proposal.proposal_number} created.')
        return redirect('proposal_list')
    return render(request, 'mysite/portal/proposals/form.html', {'form': form, 'title': 'New Proposal'})


@login_required(login_url='portal_login')
def proposal_detail(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    return render(request, 'mysite/portal/proposals/detail.html', {'proposal': proposal})


@login_required(login_url='portal_login')
def proposal_edit(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    form = ProposalForm(request.POST or None, instance=proposal)
    if form.is_valid():
        form.save()
        messages.success(request, 'Proposal updated.')
        return redirect('proposal_list')
    return render(request, 'mysite/portal/proposals/form.html', {'form': form, 'title': 'Edit Proposal'})


@login_required(login_url='portal_login')
def proposal_delete(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    if request.method == 'POST':
        proposal.delete()
        messages.success(request, 'Proposal deleted.')
        return redirect('proposal_list')
    return render(request, 'mysite/portal/confirm_delete.html', {'object': proposal, 'type': 'Proposal'})


# ─────────────────────────────────────────────
#  PORTAL — COVER LETTER CRUD
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def coverletter_list(request):
    letters = CoverLetter.objects.select_related('client').order_by('-created_at')
    return render(request, 'mysite/portal/coverletters/list.html', {'letters': letters})


@login_required(login_url='portal_login')
def coverletter_create(request):
    form = CoverLetterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cover letter created.')
        return redirect('coverletter_list')
    return render(request, 'mysite/portal/coverletters/form.html', {'form': form, 'title': 'New Cover Letter'})


@login_required(login_url='portal_login')
def coverletter_detail(request, pk):
    letter = get_object_or_404(CoverLetter, pk=pk)
    return render(request, 'mysite/portal/coverletters/detail.html', {'letter': letter})


@login_required(login_url='portal_login')
def coverletter_edit(request, pk):
    letter = get_object_or_404(CoverLetter, pk=pk)
    form = CoverLetterForm(request.POST or None, instance=letter)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cover letter updated.')
        return redirect('coverletter_list')
    return render(request, 'mysite/portal/coverletters/form.html', {'form': form, 'title': 'Edit Cover Letter'})


@login_required(login_url='portal_login')
def coverletter_delete(request, pk):
    letter = get_object_or_404(CoverLetter, pk=pk)
    if request.method == 'POST':
        letter.delete()
        messages.success(request, 'Cover letter deleted.')
        return redirect('coverletter_list')
    return render(request, 'mysite/portal/confirm_delete.html', {'object': letter, 'type': 'Cover Letter'})


# ─────────────────────────────────────────────
#  PORTAL — RECEIPT
# ─────────────────────────────────────────────

@login_required(login_url='portal_login')
def receipt_create(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    form = ReceiptForm(request.POST or None)
    if form.is_valid():
        receipt = form.save(commit=False)
        receipt.invoice = invoice
        receipt.save()
        messages.success(request, f'Receipt {receipt.receipt_number} recorded.')
        return redirect('invoice_detail', pk=invoice.pk)
    return render(request, 'mysite/portal/receipts/form.html', {
        'form': form, 'invoice': invoice, 'title': 'Record Payment'
    })