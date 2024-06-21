from django.contrib import admin
from .models import Company, Person, User, Pledge, OtherContract, Box, Paid, RechargePersonalBox, BlackList, VehicleInspection, IndividualBox, UserBox, CompanyBox

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

@admin.register(IndividualBox)
class IndividualBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'in_week_amount', 'out_week_amount', 'week_amount', 'in_global_amount', 'out_global_amount', 'global_amount', 'start_date', 'end_date', 'created_at', 'updated_at')
    search_fields = ('id',)
    list_filter = ('start_date', 'end_date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserBox)
class UserBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'individual_box')
    search_fields = ('employee__username', 'individual_box__id')
    list_filter = ('employee',)

@admin.register(CompanyBox)
class CompanyBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'individual_box')
    search_fields = ('company__name', 'individual_box__id')
    list_filter = ('company',)

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
    list_display = ('pledge', 'type_paid', 'box')
    list_filter = ('type_paid',)

@admin.register(RechargePersonalBox)
class RechargePersonalBoxAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'box')

@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = ('client', 'company', 'reason', 'is_active', 'created_at')

@admin.register(VehicleInspection)
class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = ('pledge', 'plate', 'chassis', 'motor', 'motor_status', 'bodywork_status', 'taxes', 'infractions', 'created_at', 'updated_at')
