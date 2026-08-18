.PHONY: up down restart build logs logs-web logs-celery ps \
        migrate makemigrations shell superuser collectstatic manage \
        dbshell reset-db backup restore \
        test lint bash-web bash-db clean prune

## --- Docker Compose ---

up: ## بالا آوردن همه سرویس‌ها
	docker compose up -d

down: ## پایین آوردن همه سرویس‌ها
	docker compose down

restart: ## ری‌استارت همه سرویس‌ها
	docker compose restart

build: ## بیلد و بالا آوردن مجدد
	docker compose up -d --build

logs: ## نمایش لاگ همه سرویس‌ها
	docker compose logs -f

logs-web: ## نمایش لاگ فقط سرویس web
	docker compose logs -f web

logs-celery: ## نمایش لاگ فقط سرویس celery
	docker compose logs -f celery

ps: ## نمایش وضعیت کانتینرها
	docker compose ps

## --- Django ---

migrate: ## اجرای مایگریشن‌ها
	docker compose exec web python manage.py migrate

makemigrations: ## ساخت فایل‌های مایگریشن جدید
	docker compose exec web python manage.py makemigrations

shell: ## باز کردن Django shell
	docker compose exec web python manage.py shell

superuser: ## ساخت یوزر ادمین
	docker compose exec web python manage.py createsuperuser

collectstatic: ## جمع‌آوری فایل‌های استاتیک
	docker compose exec web python manage.py collectstatic --noinput

manage: ## اجرای هر دستور دلخواه manage.py -> make manage cmd="showmigrations"
	docker compose exec web python manage.py $(cmd)

## --- دیتابیس ---

dbshell: ## باز کردن psql shell
	docker compose exec db psql -U postgres -d lms_db

reset-db: ## پاک کردن کامل دیتابیس و ساخت مجدد + migrate
	docker compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS lms_db;"
	docker compose exec -T db psql -U postgres -c "CREATE DATABASE lms_db;"
	docker compose exec web python manage.py migrate

backup: ## گرفتن بک‌آپ از دیتابیس با نام تاریخ‌دار
	docker compose exec -T db pg_dump -U postgres -d lms_db > backup_$$(date +%Y%m%d_%H%M%S).sql

restore: ## ریستور کردن بک‌آپ -> make restore file=backup_xxx.sql
	docker compose exec -T db psql -U postgres -d lms_db < $(file)

## --- تست و کیفیت کد ---

test: ## اجرای تست‌ها
	docker compose exec web python manage.py test

lint: ## بررسی کیفیت کد با flake8
	docker compose exec web flake8 .

## --- دسترسی مستقیم به کانتینر ---

bash-web: ## باز کردن bash داخل کانتینر web
	docker compose exec web bash

bash-db: ## باز کردن bash داخل کانتینر db
	docker compose exec db bash

## --- پاکسازی ---

clean: ## پایین آوردن سرویس‌ها + پاک کردن volume ها (دیتا از بین می‌ره!)
	docker compose down -v

prune: ## پاکسازی ایمیج/کانتینرهای بلااستفاده داکر
	docker system prune -f

## --- راهنما ---

help: ## نمایش این راهنما
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
````