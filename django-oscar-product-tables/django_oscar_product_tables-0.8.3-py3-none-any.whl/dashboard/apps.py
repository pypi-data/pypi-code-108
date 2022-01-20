from django.urls import path
from oscar.core.application import OscarDashboardConfig


class ProductTablesDashboardConfig(OscarDashboardConfig):

    name = 'oscar_product_tables.dashboard'
    label = 'product_tables_dashboard'

    namespace = 'product_tables_dashboard'

    default_permissions = ['is_staff']

    def ready(self):
        from . import views
        self.product_table_view = views.ProductTableView
        self.product_table_view_ajax = views.ProductTableAjaxView


    def get_urls(self):
        urls =[
            path(
                'product_table/',
                self.product_table_view.as_view(),
                name='product-table'
            ),

            # Trick to set product_id and slug later:
            path(
                'product_table/',
                self.product_table_view_ajax.as_view(),
                name='product-table-ajax'
            ),
            path(
                'product_table/<int:product_id>/<slug:code>/',
                self.product_table_view_ajax.as_view()
            ),
            path(
                'product_table/<int:product_id>/<slug:code>/<slug:action>/',
                self.product_table_view_ajax.as_view()
            ),
        ]
        return self.post_process_urls(urls)
