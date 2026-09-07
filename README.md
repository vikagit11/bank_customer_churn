# Bank Customer Churn Prediction API
ML-сервис для прогнозирования вероятности ухода клиентов банка.

Проект работает с табличными данными о 10 000 клиентах и решает задачу бинарной классификации — прогнозирует, уйдёт клиент из банка или нет.

Датасет: https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn/data

Проект использует модель CatBoost для предсказания churn, SHAP для объяснения предсказаний, PostgreSQL для хранения данных о клиентах и Redis для кэширования результатов.

## Technologies

- Python
- FastAPI
- CatBoost
- SHAP
- PostgreSQL
- Redis
- Docker
- Docker Compose

## Запуск проекта

1. Клонировать репозиторий.

```bash
git clone https://github.com/vikagit11/bank_customer_churn.git
cd bank_customer_churn
```

2. Создать файл `.env`.

```env
DB_HOST=localhost
DB_NAME=bank_churn
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5433

REDIS_HOST=redis
REDIS_PORT=6379

POSTGRES_DB=bank_churn
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

3. Запустить Docker Compose.

```bash
docker compose up --build
```

После запуска API будет доступно по адресу:

`http://localhost:8000`

Swagger-документация:

`http://localhost:8000/docs`


## Architecture

```text
Client
   │
   ▼
FastAPI
   │
   ├──► Redis ──► cached prediction
   │
   └──► PostgreSQL
          │
          ▼
       CatBoost
          │
          ▼
         SHAP
          │
          ▼
       Prediction


## Как работает проект

1. Пользователь отправляет запрос в FastAPI с `customer_id`.

2. FastAPI сначала проверяет Redis:
   есть ли уже сохранённый результат для этого клиента.

3. Если результат есть в Redis, API сразу возвращает его.
   Модель повторно не запускается.

4. Если результата в Redis нет, FastAPI получает данные клиента из PostgreSQL.

5. CatBoost использует данные клиента и предсказывает вероятность его ухода из банка.

6. SHAP определяет, какие признаки сильнее всего повлияли на предсказание.

7. Готовый результат сохраняется в Redis на 1 час.

8. FastAPI возвращает клиенту:
   - вероятность ухода;
   - предсказание (`0` — не уйдёт, `1` — уйдёт);
   - 5 наиболее значимых факторов;
   - источник результата (`model` или `redis`).


## Модель и результаты

Для задачи прогнозирования оттока клиентов были сравнены:

1. Logistic Regression
2.  Random Forest
3. Gradient Boosting
4. CatBoost

Для финального решения был выбран CatBoost.Модель хорошо показала себя по метрикам, важным для задачи прогнозирования оттока клиентов.
Лучшие параметры CatBoost:

- `depth`: 6
- `learning_rate`: 0.05
- `iterations`: 300

Результаты на тестовой выборке:

| Метрика | Значение |
|---------|----------|
| Accuracy | 0.818 |
| Precision | 0.538 |
| Recall | 0.770 |
| F1-score | 0.633 |
| ROC-AUC | 0.878 |

CatBoost был выбран как финальная модель, поскольку для задачи churn особенно важен Recall — необходимо находить как можно больше клиентов, которые могут уйти.
ROC-AUC 0.878 — модель хорошо разделяет клиентов, которые уйдут, и которые не уйдут.

## Возможные улучшения

1.  Настроить threshold для определения клиентов с высоким риском оттока с учётом бизнес-задачи.
2.  Добавить рекомендации для клиентов с высоким риском ухода(персональное предложение).
3.  Добавить Alembic для управления изменениями структуры базы данных.
4.  Добавить тесты и CI/CD.
