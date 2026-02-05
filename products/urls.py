from django.urls import path
from .views import ProductListCreateView, ProductDetailView,ProductCreateListView

urlpatterns = [
    path('create', ProductCreateListView.as_view(), name='create'),
    path('list', ProductListCreateView.as_view(), name='product-list'),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]