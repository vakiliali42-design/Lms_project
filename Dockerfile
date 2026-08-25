FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# دادن permission اجرا
RUN chmod +x /app/entrypoint.sh

# اجرای entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

# دستور پیش‌فرض اجرا
CMD ["gunicorn", "lms_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]