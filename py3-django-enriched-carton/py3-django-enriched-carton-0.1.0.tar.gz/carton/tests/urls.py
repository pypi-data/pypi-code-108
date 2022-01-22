from django.conf.urls import url

from .views import (
    add,
    clear,
    remove,
    remove_single,
    set_quantity,
    show
)


urlpatterns = [
    url(r'^show/$', show, name='carton-tests-show'),
    url(r'^add/$', add, name='carton-tests-add'),
    url(r'^remove/$', remove, name='carton-tests-remove'),
    url(r'^remove-single/$', remove_single, name='carton-tests-remove-single'),
    url(r'^clear/$', clear, name='carton-tests-clear'),
    url(r'^set-quantity/$', set_quantity, name='carton-tests-set-quantity'),
]
