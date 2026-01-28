auth_project/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── core/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── authentication.py
    ├── permissions.py
    ├── views_auth.py
    ├── views_user.py
    ├── views_rbac_admin.py
    ├── views_mock.py
    ├── utils.py
    ├── migrations/
    │   └── 0001_initial.py (создаётся миграцией)
    └── management/
        └── commands/
            └── init_rbac_demo.py   # наша команда инициализации данных
