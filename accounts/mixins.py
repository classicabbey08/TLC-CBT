from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Base mixin: set `allowed_roles = ['TEACHER', ...]` on the subclass.
    """
    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You do not have permission to access that page.")
            return redirect('accounts:dashboard_redirect')
        return super().handle_no_permission()


class SuperAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['SUPER_ADMIN']


class TeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['TEACHER']


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['STUDENT']
