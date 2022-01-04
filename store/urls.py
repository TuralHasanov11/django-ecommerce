from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (cart, processOrder, register, signin, signout, store, checkout, updateItem)

urlpatterns = [
    path('', store, name='store'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('update-item/', updateItem, name='update_item'),
    path('process-order/', processOrder, name='process_order'),
    path('logout/', signout, name='logout'),
    path('login/', signin, name='login'),
    path('register/', register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)