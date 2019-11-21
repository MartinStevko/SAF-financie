from django.contrib.admin.apps import AdminConfig


class AdminSiteConfig(AdminConfig):
    default_site = 'app.admin.OrderedAdminSite'
