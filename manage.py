import os
import sys


def main():
    """
    Точка входа для всех команд Django (runserver, migrate, custom-команды и т.д.).
    Здесь мы указываем Django, какой settings-модуль использовать.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. "
            "Убедитесь, что он установлен и доступен в виртуальном окружении."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
