from django.contrib import admin

from .models import User
from .models import CarType
from .models import Company
from .models import Coverage
from .models import Claim
from .models import Payment
from .models import History
from .models import Support

# Register your models here.

@admin.register(User)
class AllUserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "mobile", "world_zone")

@admin.register(CarType)
class AllCarTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_per_year_usd", "price_per_year_eur")

@admin.register(Company)
class AllCompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "address")

@admin.register(Coverage)
class AllCoverageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "starting_at", "ending_at")

@admin.register(Claim)
class AllClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "what_happened", "date_time_happened")

@admin.register(Payment)
class AllPaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "currency")

@admin.register(History)
class AllHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "content")

@admin.register(Support)
class AllSupportAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number")