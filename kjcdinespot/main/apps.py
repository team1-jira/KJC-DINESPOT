from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
# from django.apps import AppConfig
# from django.db.models.signals import post_migrate
# from django.contrib.auth.models import Group, Permission
# from django.db.models import Q
# from django.utils.translation import gettext_lazy as _

# class MainConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'main'

#     def ready(self):
#         post_migrate.connect(create_roles, sender=self)

# def create_roles(sender, **kwargs):
#     # Create Admin Role
#     admin_group, created = Group.objects.get_or_create(name='Admin')
#     if created:
#         permissions = Permission.objects.filter(Q(codename__in=['add_user', 'update_user', 'delete_user', 'view_user','add_canteen', 'change_canteen', 'delete_canteen', 'view_canteen']))
#         admin_group.permissions.set(permissions)
    
#     # Create Caterer Role
#     caterer_group, created = Group.objects.get_or_create(name='Caterer')
#     if created:
#         permissions = Permission.objects.filter(Q(codename__in=['add_item', 'update_item', 'delete_item', 'view_item']))
#         caterer_group.permissions.set(permissions)

#     # Create User Role
#     user_group, created = Group.objects.get_or_create(name='User')
#     if created:
#         permissions = Permission.objects.filter(Q(codename__in=['add_order', 'update_order', 'delete_order', 'view_order']))
#         user_group.permissions.set(permissions)
