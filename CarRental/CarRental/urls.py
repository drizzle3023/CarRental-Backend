"""CarRental URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

import CarRentalApp.views as car_rental_app

urlpatterns = [

    path(r'', admin.site.urls),
    path('admin/', admin.site.urls),
    path('api/sign-up', car_rental_app.SignUpView.as_view()),
    path('api/sign-in', car_rental_app.SignInView.as_view()),
    path('api/sign-verify', car_rental_app.SignVerifyView.as_view()),
    path('api/get-payment-methods', car_rental_app.GetPaymentMethodsView.as_view()),
    path('api/do-payment', car_rental_app.PaymentView.as_view()),
    path('api/get-user-profile', car_rental_app.GetUserProfileView.as_view()),
    path('api/add-coverage', car_rental_app.AddCoverageView.as_view()),
    path('api/get-company-list', car_rental_app.GetCompanyListView.as_view()),
    path('api/get-active-coverage', car_rental_app.GetActiveCoverageView.as_view()),
    path('api/cancel-coverage', car_rental_app.CancelCoverage.as_view()),
    path('api/add-claim', car_rental_app.AddClaimView.as_view()),
    path('api/get-history-list', car_rental_app.GetHistoryListView.as_view())

]
