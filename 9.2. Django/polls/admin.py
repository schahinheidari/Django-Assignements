from django.contrib import admin
from .models import Question, Choice
import jdatetime

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    verbose_name_plural = "Choices"


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date Information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]

    list_display = ["question_text", "get_jalali_pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]
    ordering = ["-pub_date"]  # New: Order by publication date descending

    def get_jalali_pub_date(self, obj):
        """Convert publication date to Jalali format."""
        jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.pub_date)
        return jalali_date.strftime("%Y/%m/%d")

    get_jalali_pub_date.short_description = "Publication date (شمسی)"

    def has_add_permission(self, request):
        """Prevent adding new questions directly from admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of questions directly from admin."""
        return False

admin.site.register(Question, QuestionAdmin)