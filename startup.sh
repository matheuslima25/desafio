#!/bin/bash

#restart this script as root, if not already root
[ `whoami` = root ] || exec sudo $0 $*

python manage.py migrate
python manage.py shell -c "from core.models import Perfil; perfil=perfil=Perfil.objects.get_or_create(name='Anunciante')"
python manage.py shell -c "from core.models import Perfil; Perfil.objects.get_or_create(name='Administrador')"
python manage.py shell -c "from core.models import User; User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')"
python manage.py shell -c "from core.models import User; User.objects.create_user(username='usuario', email='usuario@example.com', password='mudar123')"

python manage.py runserver 0.0.0.0:8000