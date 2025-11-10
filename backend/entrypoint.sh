#!/usr/bin/env sh
set -e

# DB待機（Postgres）: psycopg2で接続確認
if [ -n "${POSTGRES_HOST:-}" ]; then
  echo "Waiting for database ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  python - <<'PY'
import os, time, sys
import psycopg2

host = os.getenv('POSTGRES_HOST', 'db')
port = int(os.getenv('POSTGRES_PORT', '5432'))
dbname = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')

for i in range(60):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        conn.close()
        print('Database is ready')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting for database... ({i+1}/60) {e!r}')
        time.sleep(1)

print('Database not ready, exiting', file=sys.stderr)
sys.exit(1)
PY
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 初回の管理ユーザー自動作成（環境変数で制御）
if [ "${DJANGO_CREATE_SUPERUSER:-true}" = "true" ]; then
  python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {username}")
else:
    print("Superuser already exists. Skipping.")
PYCODE
fi

exec "$@"

# --- Dynamic Gunicorn configuration injection ---------------------------------
# CMD から "gunicorn" が渡された場合、環境変数でチューニングできるように
# 引数を再構築する。これにより長時間の LLM 呼び出しで 30s デフォルト timeout
# でワーカーが強制終了する問題を回避する。
if [ "$1" = "gunicorn" ]; then
  HOST="${GUNICORN_BIND_HOST:-0.0.0.0}"
  PORT="${GUNICORN_BIND_PORT:-8000}"
  WORKERS="${GUNICORN_WORKERS:-2}"
  TIMEOUT="${GUNICORN_TIMEOUT:-180}"           # ハードキルまでの秒数
  GRACEFUL="${GUNICORN_GRACEFUL_TIMEOUT:-30}"  # graceful shutdown の猶予
  KEEPALIVE="${GUNICORN_KEEPALIVE:-5}"         # keep-alive ソケット保持秒数
  MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-0}"   # メモリリーク対策（0=未使用）
  MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-0}"

  # 付与オプションの組み立て
  EXTRA_OPTS=""
  if [ "$MAX_REQUESTS" != "0" ]; then
    EXTRA_OPTS="$EXTRA_OPTS --max-requests $MAX_REQUESTS"
  fi
  if [ "$MAX_REQUESTS_JITTER" != "0" ]; then
    EXTRA_OPTS="$EXTRA_OPTS --max-requests-jitter $MAX_REQUESTS_JITTER"
  fi

  echo "Starting gunicorn: workers=$WORKERS timeout=$TIMEOUT graceful=$GRACEFUL keepalive=$KEEPALIVE $EXTRA_OPTS"
  exec gunicorn lecture_system.wsgi:application \
    --bind "${HOST}:${PORT}" \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}" \
    --graceful-timeout "${GRACEFUL}" \
    --keep-alive "${KEEPALIVE}" $EXTRA_OPTS
fi
