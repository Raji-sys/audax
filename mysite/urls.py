from django.urls import path
from . import views

urlpatterns = [

    # ── PUBLIC ──────────────────────────────────────────
    path('', views.index, name='index'),

    # Blog (public)
    path('blog/',              views.blog_list,   name='blog_list'),
    path('blog/<slug:slug>/',  views.blog_detail, name='blog_detail'),

    # ── HIDDEN PORTAL ───────────────────────────────────
    # Change 'x' to anything secret — visitors won't find it
    path('x/login/',   views.portal_login,  name='portal_login'),
    path('x/logout/',  views.portal_logout, name='portal_logout'),
    path('x/',         views.portal_dashboard, name='portal_dashboard'),

    # Blog management
    path('x/blog/',               views.blog_manage, name='blog_manage'),
    path('x/blog/new/',           views.blog_create, name='blog_create'),
    path('x/blog/<int:pk>/edit/', views.blog_edit,   name='blog_edit'),
    path('x/blog/<int:pk>/del/',  views.blog_delete, name='blog_delete'),

    # Clients
    path('x/clients/',               views.client_list,   name='client_list'),
    path('x/clients/new/',           views.client_create, name='client_create'),
    path('x/clients/<int:pk>/edit/', views.client_edit,   name='client_edit'),

    # Invoices
    path('x/invoices/',                    views.invoice_list,   name='invoice_list'),
    path('x/invoices/new/',                views.invoice_create, name='invoice_create'),
    path('x/invoices/<int:pk>/',           views.invoice_detail, name='invoice_detail'),
    path('x/invoices/<int:pk>/edit/',      views.invoice_edit,   name='invoice_edit'),
    path('x/invoices/<int:pk>/del/',       views.invoice_delete, name='invoice_delete'),
    path('x/invoices/<int:invoice_pk>/receipt/', views.receipt_create, name='receipt_create'),

    # Quotations
    path('x/quotations/',               views.quotation_list,   name='quotation_list'),
    path('x/quotations/new/',           views.quotation_create, name='quotation_create'),
    path('x/quotations/<int:pk>/',      views.quotation_detail, name='quotation_detail'),
    path('x/quotations/<int:pk>/edit/', views.quotation_edit,   name='quotation_edit'),
    path('x/quotations/<int:pk>/del/',  views.quotation_delete, name='quotation_delete'),

    # Proposals
    path('x/proposals/',               views.proposal_list,   name='proposal_list'),
    path('x/proposals/new/',           views.proposal_create, name='proposal_create'),
    path('x/proposals/<int:pk>/',      views.proposal_detail, name='proposal_detail'),
    path('x/proposals/<int:pk>/edit/', views.proposal_edit,   name='proposal_edit'),
    path('x/proposals/<int:pk>/del/',  views.proposal_delete, name='proposal_delete'),

    # Cover Letters
    path('x/coverletters/',               views.coverletter_list,   name='coverletter_list'),
    path('x/coverletters/new/',           views.coverletter_create, name='coverletter_create'),
    path('x/coverletters/<int:pk>/',      views.coverletter_detail, name='coverletter_detail'),
    path('x/coverletters/<int:pk>/edit/', views.coverletter_edit,   name='coverletter_edit'),
    path('x/coverletters/<int:pk>/del/',  views.coverletter_delete, name='coverletter_delete'),
]