# ENF — Интернет-магазин одежды

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-4.2+-green?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-14+-blue?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-24.0+-blue?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/HTMX-1.9+-orange?style=for-the-badge&logo=html5&logoColor=white" alt="HTMX">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-green?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Type-Full%20Stack%20Web%20App-lightgrey?style=flat-square" alt="Type">
</p>

<p align="center">
  <strong>Современный интернет-магазин одежды с адаптивным дизайном и Stripe-интеграцией</strong>
</p>

<p align="center">
  <a href="#-особенности">Особенности</a> •
  <a href="#-технологии">Технологии</a> •
  <a href="#-установка">Установка</a> •
  <a href="#-использование">Использование</a> •
  <a href="#-документация">Документация</a>
</p>

---

## ✨ Особенности

🛍️ **Каталог товаров**  
- Фильтрация по категориям, размерам и цене  
- Поиск по названию и описанию  
- Сортировка по популярности и дате  

🛒 **Интеллектуальная корзина**  
- Выбор размера для каждого товара  
- Быстрое добавление без перезагрузки страницы  
- Автоматическое обновление стоимости  

👤 **Личный кабинет**  
- История заказов  
- Редактирование профиля  
- Сохраненные адреса доставки  

💳 **Платежи**  
- Интеграция со Stripe (тестовый режим)  
- Безопасная обработка платежей  
- Поддержка различных способов оплаты  

📱 **Адаптивность**  
- Полностью адаптивный дизайн  
- Поддержка всех современных браузеров  
- Оптимизация для мобильных устройств  

🐳 **DevOps**  
- Готовое Docker-развертывание  
- Nginx + Gunicorn production setup  
- Автоматическая сборка статики  

## 🛠️ Технологии

### Backend
![Python](https://img.shields.io/badge/Python-3.10+-4B8BBE?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-6+-DC382D?style=flat-square&logo=redis&logoColor=white)

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![HTMX](https://img.shields.io/badge/HTMX-1.9+-FF3860?style=flat-square&logo=html5&logoColor=white)

### DevOps
![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.20+-009639?style=flat-square&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-20.1+-FECB2E?style=flat-square&logo=python&logoColor=black)

### Интеграции
![Stripe](https://img.shields.io/badge/Stripe-API-008CDD?style=flat-square&logo=stripe&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-9.0+-F0C040?style=flat-square&logo=python&logoColor=black)

## 🚀 Установка

### Быстрый старт (Docker)

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/django-project.git
cd django-project

# Запуск с помощью Docker Compose
cd enf-docker
cp .env.example .env

# Настройка переменных окружения
nano .env  # или используйте любой текстовый редактор

# Запуск сервисов
docker-compose up -d

# Инициализация базы данных
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Загрузка тестовых данных (опционально)
docker-compose exec web python manage.py loaddata fixtures/categories.json
```

### Локальная разработка

```bash
# Клонирование и настройка окружения
git clone https://github.com/yourusername/django-project.git
cd django-project/app

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r ../requirements.txt

# Настройка базы данных (PostgreSQL)
# Убедитесь, что PostgreSQL запущен
createdb enf

# Миграции и запуск
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 📖 Использование

### Основные URL

| Эндпоинт | Описание |
|----------|----------|
| `/` | Главная страница |
| `/catalog/` | Каталог товаров |
| `/catalog/{slug}/` | Детали товара |
| `/cart/` | Корзина |
| `/orders/` | Заказы |
| `/profile/` | Личный кабинет |
| `/admin/` | Админка Django |

### Переменные окружения

Создайте файл `.env` в директории `enf-docker/`:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=enf
POSTGRES_USER=enf_user
POSTGRES_PASSWORD=enf_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Stripe (тестовый режим)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### Docker команды

```bash
# Просмотр логов
docker-compose logs -f web

# Остановка сервисов
docker-compose down

# Пересборка образов
docker-compose build --no-cache

# Очистка volumes
docker-compose down -v

# Запуск shell в контейнере
docker-compose exec web python manage.py shell
```

## 📚 Документация

- **[Разработка](DOCS.md#разработка)** — настройка окружения и разработка
- **[API](DOCS.md#api-эндпоинты)** — RESTful API и HTMX endpoints
- **[Архитектура](DOCS.md#архитектура)** — структура проекта и модели данных
- **[Docker](DOCS.md#docker-и-деплой)** — production развертывание
- **[Тестирование](DOCS.md#тестирование)** — unit-тесты и покрытие