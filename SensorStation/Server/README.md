# DJANGO SERVER
### Dependências
```
pip install django
pip install django-cors-headers
pip install djangorestframework
pip install orjson
```


### Configuração de CORS
No arquivo settings.py, inserir:
```python
# ALLOW ORIGIN *
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']
```

### Criando Login Administrativo
```
python manage.py createsuperuser
```

### Criando Novos Apps (Tabelas)
```
python manage.py startapp myapp
```
- Crie a Pasta "Tables", mova o app "myapp" (nome escolhido) para a pasta Tables
- Em "models.py" (dentro da pasta onde se encontra a tabela), é necessário inserir a classe do modelo (tabela), exemplo simples:
```python
from django.db import models

class Tabela1(models.Model):
    id   = models.AutoField(primary_key=True, unique=True, editable=False)
    data = models.JSONField(default={})
```

- Em admin.py, insira o modelo para visualização
```python
from django.contrib import admin
from .models import Tabela1

admin.site.register(Tabela1)
```

- Assim, agora em "apps.py", insirao caminho do modelo com o nome da pasta de apps, exemplo
```python
from django.apps import AppConfig

class Tabela1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Tables.Tabela1' # mude aqui (pasta + pasta do app)
```

- Em settings.py, insira em "INSTALLED_APPS", exemplo
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'Tables.Tabela1',
    'Tables.Tabela2',
]
```

### Aplicando Migrações (Mudanças nas Tabelas)
Sempre que for alterar algo na estrutura das tabelas, mesmo que seja a criação ou remoção delas, aplique as migrações
```python
python manage.py makemigrations
python manage.py migrate
```

### Iniciando Server
- O site encontra-se em localhost:8000/admin
- No arquivo db.sqlite3 encontram-se todas as tabelas, faça backups
```python
python manage.py runserver (local)
python manage.py runserver 0.0.0.0:8000 (global)
python manage.py runserver 0.0.0.0:8000 --nothreading --noreload (produção)
```
obs: (para encontrar o endereço vá em ipconfig ipv4)

### (Extra) Debug em Shell
```python
python manage.py shell
``` 

