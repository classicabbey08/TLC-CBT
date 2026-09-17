from django.contrib import admin

from .models import ExamAttempt, StudentAnswer


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choice')
    can_delete = False


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'status', 'score', 'started_at', 'submitted_at')
    list_filter = ('status', 'exam')
    search_fields = ('student__username', 'exam__title')
    inlines = [StudentAnswerInline]
