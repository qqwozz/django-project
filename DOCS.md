# 📖 Документация для разработчиков ENF

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-green?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Last%20Update-March%202026-lightgrey?style=flat-square" alt="Last Update">
</p>

## 📋 Содержание

- [🏗️ Архитектура](#архитектура)
- [🗄️ Модели данных](#модели-данных)
- [🔌 API эндпоинты](#api-эндпоинты)
- [💻 Разработка](#разработка)
- [🐳 Docker и деплой](#docker-и-деплой)
- [🧪 Тестирование](#тестирование)
- [🔧 Troubleshooting](#troubleshooting)
- [📚 Полезные ссылки](#полезные-ссылки)

---

## 🏗️ Архитектура

### 📁 Структура проекта

```
django-project/
├── 📁 app/                    # Django-приложения
│   ├── 📁 enf/               # Конфигурация проекта
│   │   ├── settings/         # Настройки (base, local, prod)
│   │   ├── urls.py           # Корневые маршруты
│   │   └── celery.py         # Celery конфигурация
│   ├── 📁 main/              # Каталог товаров
│   │   ├── models.py         # Модели товаров
│   │   ├── views.py          # Представления каталога
│   │   ├── services.py       # Бизнес-логика
│   │   └── templates/        # Шаблоны
│   ├── 📁 cart/              # Корзина
│   │   ├── cart.py           # Класс корзины
│   │   ├── context_processors.py
│   │   └── templatetags/     # Кастомные теги
│   ├── 📁 users/             # Пользователи
│   │   ├── models.py         # Кастомная модель User
│   │   ├── forms.py          # Формы аутентификации
│   │   └── views.py          # Профиль и регистрация
│   ├── 📁 orders/            # Заказы
│   │   ├── models.py         # Модели заказов
│   │   ├── views.py          # Оформление заказа
│   │   ├── signals.py        # Обработка событий
│   │   └── webhooks.py       # Stripe webhooks
│   └── 📁 payment/           # Платежи
│       ├── models.py         # Платежные операции
│       └── views.py          # Stripe интеграция
├── 📁 enf-docker/            # Docker-конфигурация
│   ├── docker-compose.yml    # Мультиконтейнерная сборка
│   ├── Dockerfile            # Web-сервер
│   ├── nginx.conf            # Прокси-сервер
│   └── .env.example          # Переменные окружения
├── 📄 requirements.txt       # Python зависимости
└── 📄 .gitignore             # Игнорируемые файлы
```

### 🔄 Схема взаимодействия

```mermaid
graph TB
    A[Пользователь] --> B[Nginx<br/>80/443]
    B --> C[Gunicorn<br/>8000]
    C --> D[Django<br/>WSGI]
    
    D --> E[PostgreSQL<br/>5432]
    D --> F[Redis<br/>6379]
    D --> G[Stripe API]
    
    E --> H[Модели данных]
    F --> I[Кэширование]
    G --> J[Платежи]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

### 🏗️ Паттерны проектирования

- **MVC (Model-View-Controller)** — Django архитектура
- **Service Layer** — бизнес-логика в `services.py`
- **Repository Pattern** — работа с моделями через менеджеры
- **Observer Pattern** — Django signals для событий
- **Factory Pattern** — создание заказов и платежей

---

## 🗄️ Модели данных

### 📦 Основные модели

#### Product — Товар
```python
class Product(models.Model):
    """Модель товара для интернет-магазина"""
    
    name = models.CharField(
        max_length=200, 
        verbose_name="Название",
        help_text="Название товара"
    )
    slug = models.SlugField(
        unique=True, 
        db_index=True,
        help_text="URL-friendly идентификатор"
    )
    category = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Цена"
    )
    description = models.TextField(
        blank=True, 
        verbose_name="Описание"
    )
    main_image = models.ImageField(
        upload_to='products/%Y/%m/',
        verbose_name="Главное изображение"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Активен"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('main:product_detail', kwargs={'slug': self.slug})
    
    @property
    def discounted_price(self):
        """Рассчитывает цену со скидкой"""
        if hasattr(self, 'discount'):
            return self.price * (1 - self.discount.percentage / 100)
        return self.price
```

#### Cart — Корзина
```python
class Cart(models.Model):
    """Корзина пользователя"""
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='carts',
        verbose_name="Пользователь"
    )
    session_key = models.CharField(
        max_length=40, 
        db_index=True,
        verbose_name="Ключ сессии"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
    
    def __str__(self):
        return f"Cart {self.id}"
    
    @property
    def total(self):
        """Общая стоимость корзины"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        """Количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())
    
    def add_item(self, product, size, quantity=1):
        """Добавить товар в корзину"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
    
    def remove_item(self, item_id):
        """Удалить товар из корзины"""
        self.items.filter(id=item_id).delete()
```

### 📊 Диаграмма отношений

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : contains
    PRODUCT ||--o{ PRODUCT_SIZE : has
    PRODUCT ||--o{ PRODUCT_IMAGE : has
    PRODUCT ||--o{ CART_ITEM : in
    CART ||--o{ CART_ITEM : contains
    USER ||--o{ CART : owns
    USER ||--o{ ORDER : creates
    CART_ITEM ||--o{ ORDER_ITEM : becomes
    ORDER ||--|| PAYMENT : has
    
    CATEGORY {
        string name
        string slug
        boolean is_active
    }
    
    PRODUCT {
        string name
        string slug
        decimal price
        text description
        boolean is_active
    }
    
    CART {
        string session_key
        datetime created_at
    }
    
    ORDER {
        string order_number
        decimal total
        string status
        datetime created_at
    }
```

---

## 🔌 API эндпоинты

### 🌐 RESTful API

| Метод | Эндпоинт | Описание | Параметры |
|-------|----------|----------|-----------|
| `GET` | `/api/catalog/` | Список товаров | `?category=, ?size=, ?price_min=, ?price_max=` |
| `GET` | `/api/catalog/{slug}/` | Детали товара | - |
| `POST` | `/api/cart/add/` | Добавить в корзину | `{product_id, size_id, quantity}` |
| `PUT` | `/api/cart/update/{id}/` | Обновить количество | `{quantity}` |
| `DELETE` | `/api/cart/remove/{id}/` | Удалить из корзины | - |
| `POST` | `/api/orders/create/` | Создать заказ | `{address, phone, payment_method}` |
| `GET` | `/api/orders/{id}/` | Получить заказ | - |
| `POST` | `/api/webhooks/stripe/` | Stripe webhook | `{...}` |

### 📝 Примеры запросов

#### Добавление товара в корзину (HTMX)
```html
<form hx-post="/api/cart/add/" 
      hx-target="#cart-summary"
      hx-swap="outerHTML"
      hx-trigger="submit">
    
    <input type="hidden" name="product_id" value="{{ product.id }}">
    
    <div class="form-group">
        <label for="size">Размер:</label>
        <select name="size_id" id="size" required>
            {% for size in product.sizes.all %}
                <option value="{{ size.id }}">{{ size.name }}</option>
            {% endfor %}
        </select>
    </div>
    
    <div class="form-group">
        <label for="quantity">Количество:</label>
        <input type="number" name="quantity" value="1" min="1" max="10">
    </div>
    
    <button type="submit" class="btn btn-primary">
        Добавить в корзину
    </button>
</form>
```

#### Фильтрация каталога (JavaScript)
```javascript
// Фильтрация товаров по категориям и цене
async function filterProducts() {
    const filters = {
        category: document.getElementById('category-filter').value,
        min_price: document.getElementById('min-price').value,
        max_price: document.getElementById('max-price').value,
        size: document.getElementById('size-filter').value
    };
    
    const url = new URL('/api/catalog/', window.location.origin);
    Object.entries(filters).forEach(([key, value]) => {
        if (value) url.searchParams.append(key, value);
    });
    
    const response = await fetch(url);
    const data = await response.json();
    
    // Обновление UI
    updateProductList(data.products);
    updatePagination(data.pagination);
}
```

#### Stripe Checkout (JavaScript)
```javascript
// Инициализация Stripe Checkout
const stripe = Stripe('{{ STRIPE_PUBLISHABLE_KEY }}');

async function createCheckoutSession() {
    const response = await fetch('/api/payment/create-checkout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            items: cartItems,
            success_url: window.location.origin + '/orders/success/',
            cancel_url: window.location.origin + '/cart/'
        })
    });
    
    const session = await response.json();
    
    // Перенаправление на Stripe Checkout
    const result = await stripe.redirectToCheckout({
        sessionId: session.id
    });
    
    if (result.error) {
        console.error(result.error.message);
    }
}
```

---

## 💻 Разработка

### 🚀 Настройка окружения

#### 1. Клонирование и установка
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/django-project.git
cd django-project

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Установка dev-зависимостей
pip install -r requirements-dev.txt
```

#### 2. Переменные окружения
Создайте файл `.env` в корне проекта:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/enf

# Redis
REDIS_URL=redis://localhost:6379/1

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (для уведомлений)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
```

#### 3. База данных
```bash
# Запуск PostgreSQL через Docker
docker run --name enf-postgres \
  -e POSTGRES_DB=enf \
  -e POSTGRES_USER=enf_user \
  -e POSTGRES_PASSWORD=enf_password \
  -p 5432:5432 \
  -d postgres:14-alpine

# Миграции
cd app
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Загрузка тестовых данных
python manage.py loaddata fixtures/categories.json
python manage.py loaddata fixtures/products.json
```

### 🛠️ Полезные команды

#### Django команды
```bash
# Запуск сервера разработки
python manage.py runserver

# Создание суперпользователя
python manage.py createsuperuser

# Миграции
python manage.py makemigrations
python manage.py migrate

# Загрузка фикстур
python manage.py loaddata fixtures/products.json

# Выгрузка фикстур
python manage.py dumpdata main.Product --indent 2 > fixtures/products.json

# Проверка миграций
python manage.py makemigrations --dry-run --verbosity 3

# Очистка кэша
python manage.py clear_cache

# Генерация секретного ключа
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### DevOps команды
```bash
# Форматирование кода
black app/
isort app/

# Проверка кода
flake8 app/
mypy app/
bandit -r app/

# Запуск тестов
pytest
pytest --cov=app --cov-report=html

# Сбор статики
python manage.py collectstatic --noinput

# Проверка URL
python manage.py check --deploy
```

### 🎨 Frontend разработка

#### Структура статики
```
app/
├── static/
│   ├── css/
│   │   ├── main.css          # Основные стили
│   │   ├── cart.css          # Стили корзины
│   │   └── responsive.css    # Адаптивные стили
│   ├── js/
│   │   ├── main.js           # Основной JS
│   │   ├── cart.js           # Логика корзины
│   │   ├── catalog.js        # Фильтрация каталога
│   │   └── stripe.js         # Stripe интеграция
│   └── images/               # Статичные изображения
└── media/                    # Загружаемые файлы
```

#### Hot Reload для статики
```bash
# Установка livereload
pip install livereload

# Запуск сервера с автообновлением
livereload --port 35729 app/static/
```

---

## 🐳 Docker и деплой

### 📦 Docker Compose конфигурация

```yaml
version: '3.8'

services:
  # PostgreSQL база данных
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis для кэширования
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django приложение
  web:
    build: .
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/1
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    volumes:
      - ./app:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn enf.wsgi:application --bind 0.0.0.0:8000"

  # Nginx прокси
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/static
      - media_volume:/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 🐳 Dockerfile

```dockerfile
# Многоступенчатая сборка
FROM python:3.11-slim as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN groupadd --system --gid 1000 appgroup && \
    adduser --system --uid 1000 --gid 1000 appuser

# Копирование зависимостей
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Настройка приложения
WORKDIR /app
COPY app/ .
RUN chown -R appuser:appgroup /app
USER appuser

# Запуск приложения
EXPOSE 8000
CMD ["gunicorn", "enf.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 🌐 Nginx конфигурация

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Перенаправление на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # Настройки безопасности
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Статические файлы
    location /static/ {
        alias /static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Медиа файлы
    location /media/ {
        alias /media/;
        expires 1y;
    }
    
    # Django приложение
    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

### 🚀 Production деплой

#### 1. Настройка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка SSL сертификатов (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

#### 2. Запуск приложения
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/django-project.git
cd django-project/enf-docker

# Настройка переменных окружения
cp .env.example .env
nano .env

# Запуск сервисов
docker-compose up -d

# Проверка состояния
docker-compose ps
docker-compose logs -f
```

#### 3. Мониторинг и логи
```bash
# Просмотр логов
docker-compose logs -f web
docker-compose logs -f nginx

# Мониторинг ресурсов
docker stats

# Резервное копирование БД
docker-compose exec db pg_dump -U enf_user enf > backup_$(date +%Y%m%d).sql

# Восстановление БД
docker-compose exec -T db psql -U enf_user -d enf < backup.sql
```

---

## 🧪 Тестирование

### 📋 Структура тестов

```
app/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # Тесты моделей
│   ├── test_views.py       # Тесты представлений
│   ├── test_api.py         # Тесты API
│   ├── test_forms.py       # Тесты форм
│   ├── test_services.py    # Тесты сервисов
│   └── fixtures/           # Тестовые данные
│       ├── users.json
│       ├── products.json
│       └── orders.json
└── conftest.py             # Общие фикстуры
```


---


## 🔧 Troubleshooting

### ❌ Частые проблемы и решения

#### 1. Проблемы с миграциями
```bash
# Ошибка: "django.db.migrations.exceptions.InconsistentMigrationHistory"
# Решение: Сброс миграций
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

python manage.py makemigrations
python manage.py migrate --fake-initial

# Ошибка: "relation already exists"
# Решение: Проверка существующих таблиц
python manage.py dbshell
\d  # Просмотр таблиц в PostgreSQL
```

#### 2. Проблемы с Docker
```bash
# Контейнер не запускается
docker-compose logs web
docker-compose down
docker-compose up --build

# Проблемы с volumes
docker-compose down -v
docker-compose up

# Проблемы с сетью
docker network ls
docker network prune
```

#### 3. Проблемы со статикой
```bash
# Статические файлы не загружаются
python manage.py collectstatic --clear --noinput
chmod -R 755 static/ media/

# Ошибки в production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
STATIC_ROOT = '/app/staticfiles/'
MEDIA_ROOT = '/app/media/'
```

#### 4. Проблемы с базой данных
```bash
# Подключение к PostgreSQL
docker-compose exec db psql -U enf_user -d enf

# Проверка таблиц
\dt

# Проверка данных
SELECT * FROM main_product LIMIT 5;

# Восстановление из дампа
psql -U enf_user -d enf < backup.sql
```

#### 5. Проблемы с Stripe
```bash
# Ошибки вебхуков
# Проверка секрета вебхука
STRIPE_WEBHOOK_SECRET=whsec_...

# Тестирование вебхука
stripe listen --forward-to localhost:8000/webhooks/stripe/

# Проверка ключей
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 🐛 Отладка

#### Django Debug Toolbar
```python
# settings/local.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

#### Логирование
```python
# settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

#### Shell для отладки
```bash
# Django shell
python manage.py shell

# IPython shell
python manage.py shell_plus

# С доступом к переменным окружения
python manage.py shell -- --env
```

---

## 📚 Полезные ссылки

### 📖 Официальная документация
- [Django Documentation](https://docs.djangoproject.com/) — официальная документация Django
- [Django REST Framework](https://www.django-rest-framework.org/) — REST API фреймворк
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) — документация PostgreSQL
- [Redis Documentation](https://redis.io/documentation) — документация Redis

### 🔧 Инструменты и библиотеки
- [HTMX Documentation](https://htmx.org/docs/) — современный подход к frontend
- [Stripe API Reference](https://stripe.com/docs/api) — документация Stripe API
- [Docker Documentation](https://docs.docker.com/) — документация Docker
- [Nginx Documentation](https://nginx.org/en/docs/) — документация Nginx

### 🛠️ DevOps и деплой
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/) — чек-лист деплоя Django
- [Gunicorn Documentation](https://docs.gunicorn.org/) — WSGI сервер
- [Let's Encrypt](https://letsencrypt.org/) — бесплатные SSL сертификаты
- [GitHub Actions](https://docs.github.com/en/actions) — CI/CD

### 📊 Тестирование
- [pytest Documentation](https://docs.pytest.org/) — фреймворк для тестирования
- [Factory Boy](https://factoryboy.readthedocs.io/) — фабрики для тестовых данных
- [Coverage.py](https://coverage.readthedocs.io/) — измерение покрытия кода

### 🎨 Frontend
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/) — CSS фреймворк
- [Tailwind CSS](https://tailwindcss.com/docs) — utility-first CSS
- [Alpine.js](https://alpinejs.dev/) — реактивный JavaScript фреймворк

---

<p align="center">
  <img src="https://img.shields.io/badge/Documentation-Complete-brightgreen?style=for-the-badge" alt="Documentation Complete">
  <img src="https://img.shields.io/badge/Last%20Updated-March%202026-lightgrey?style=for-the-badge" alt="Last Updated">
</p>

<p align="center">
  <em>Документация создана с ❤️ для разработчиков</em>
</p>