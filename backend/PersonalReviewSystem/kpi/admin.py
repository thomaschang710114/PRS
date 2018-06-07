from django.contrib import admin
from .models import Employee, Retrospective, ProfessionReadinessLevel, Evaluation

# Register your models here.
#admin.site.register(Snippet) 只顯示一欄位太單調，改下面
#告訴 DJ 在 admin 中註冊 Snippet 這個 model，並使用 SnippetAdmin 來顯示
#@admin.register(Snippet)
#class SnippetAdmin(admin.ModelAdmin):
#    list_display = ('title', 'code', 'language', 'style', 'owner',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee_number', 'ad_account', 'role', 'owner',)


@admin.register(Retrospective)
class RetrospectiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'wentwell_myself', 'wentwell_review', 'wentwell_approval', 'owner', 'current_duration',)

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'type', 'done', 'eval_by', 'retro',)

@admin.register(ProfessionReadinessLevel)
class ProfessionReadinessLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'prl', 'status', 'supervisor_feedback', 'owner', 'current_duration',)



