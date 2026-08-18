from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'student')

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'teacher')

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'admin')

class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'admin' or 'teacher')

class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user == obj.teacher or request.user.obj)