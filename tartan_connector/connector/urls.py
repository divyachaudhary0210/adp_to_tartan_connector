from django.urls import path
from .views import TokenView, MockADPEmployeesView, TransformEmployeesView

urlpatterns = [
    path("token/", TokenView.as_view(), name="token"),
    path("mock-adp/employees/", MockADPEmployeesView.as_view(), name="mock_adp_employees"),
    path("transform/", TransformEmployeesView.as_view(), name="transform"),
]

