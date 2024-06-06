from django.contrib import admin
from .models import Company, Person, User, Pledge, OtherContract, Box, Paid, RechargePersonalBox, PersonalBox, BlackList, VehicleInspection

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'slang', 'created_at', 'updated_at')

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('ci', 'name', 'last_name', 'address', 'phone_number')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'last_login')
    search_fields = ('username', 'email')

@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'client', 'company', 'article', 'type', 'loan_date', 'status')
    list_filter = ('company', 'status')

@admin.register(OtherContract)
class OtherContractAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'contract_type', 'currency', 'initial_date', 'end_date')

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('company', 'employee', 'amount', 'type', 'created_at')
    list_filter = ('company', 'type')

@admin.register(Paid)
class PaidAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'type_paid', 'amount', 'created_at')
    list_filter = ('type_paid',)

@admin.register(RechargePersonalBox)
class RechargePersonalBoxAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'employee', 'amount', 'type', 'created_at')

@admin.register(PersonalBox)
class PersonalBoxAdmin(admin.ModelAdmin):
    list_display = ('employee', 'in_week_amount', 'out_week_amount', 'week_amount', 'in_global_amount', 'out_global_amount', 'global_amount', 'created_at')

@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = ('client', 'company', 'reason', 'is_active', 'created_at')

@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'plate', 'chassis', 'motor', 'motor_status', 'bodywork_status', 'taxes', 'infractions', 'created_at', 'updated_at')
