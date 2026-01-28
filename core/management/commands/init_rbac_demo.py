from django.core.management.base import BaseCommand
import bcrypt

from core.models import Role, BusinessElement, AccessRoleRule, User, UserRole


class Command(BaseCommand):
    help = "Инициализация демо-данных для RBAC и создание администратора"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Создание ролей..."))

        admin_role, _ = Role.objects.get_or_create(
            name="admin", defaults={"description": "Администратор системы"}
        )
        user_role, _ = Role.objects.get_or_create(
            name="user", defaults={"description": "Обычный пользователь"}
        )

        self.stdout.write(self.style.SUCCESS("Роли созданы/обновлены."))

        self.stdout.write(self.style.MIGRATE_HEADING("Создание бизнес-элементов..."))

        users_el, _ = BusinessElement.objects.get_or_create(
            code="users", defaults={"description": "Пользователи"}
        )
        products_el, _ = BusinessElement.objects.get_or_create(
            code="products", defaults={"description": "Товары"}
        )
        orders_el, _ = BusinessElement.objects.get_or_create(
            code="orders", defaults={"description": "Заказы"}
        )
        access_rules_el, _ = BusinessElement.objects.get_or_create(
            code="access_rules", defaults={"description": "Правила доступа"}
        )

        self.stdout.write(self.style.SUCCESS("Бизнес-элементы созданы/обновлены."))

        self.stdout.write(self.style.MIGRATE_HEADING("Создание правил доступа..."))

        # admin: полный доступ ко всем элементам
        for el in (users_el, products_el, orders_el, access_rules_el):
            AccessRoleRule.objects.get_or_create(
                role=admin_role,
                element=el,
                defaults={
                    "read_permission": True,
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_permission": True,
                    "update_all_permission": True,
                    "delete_permission": True,
                    "delete_all_permission": True,
                },
            )

        # user: может читать продукты и работать только со своими заказами
        AccessRoleRule.objects.get_or_create(
            role=user_role,
            element=products_el,
            defaults={
                "read_all_permission": True,
                "read_permission": False,
                "create_permission": False,
                "update_permission": False,
                "update_all_permission": False,
                "delete_permission": False,
                "delete_all_permission": False,
            },
        )

        AccessRoleRule.objects.get_or_create(
            role=user_role,
            element=orders_el,
            defaults={
                "read_permission": True,
                "read_all_permission": False,
                "create_permission": True,
                "update_permission": True,
                "update_all_permission": False,
                "delete_permission": True,
                "delete_all_permission": False,
            },
        )

        self.stdout.write(self.style.SUCCESS("Правила доступа созданы/обновлены."))

        self.stdout.write(self.style.MIGRATE_HEADING("Создание администратора..."))

        admin_email = "admin@example.com"
        admin_password = "adminpass"

        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "password_hash": bcrypt.hashpw(
                    admin_password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8"),
                "is_active": True,
            },
        )

        UserRole.objects.get_or_create(user=admin_user, role=admin_role)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Администратор создан: {admin_email} / {admin_password}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Администратор уже существовал: {admin_email}. Пароль не изменён."
                )
            )

        self.stdout.write(self.style.SUCCESS("Инициализация демо-данных завершена."))
