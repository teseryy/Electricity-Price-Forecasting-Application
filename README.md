# Electricity Price Forecasting

This project is a web application for forecasting electricity prices. It
combines historical electricity prices with temperature data and presents
forecasts for the next month in both daily and hourly time intervals.

The application was developed as a bachelor thesis project. Its main goal is
to provide an understandable way to explore price trends: users can request a
period, compare historical data with forecasts, inspect temperature values, and
view the results as charts and tables.

## Features

- Daily and hourly electricity-price forecasts for up to 30 days ahead.
- Historical daily and hourly price data for comparison.
- Price forecasts with lower and upper prediction bounds.
- Temperature data displayed together with price data.
- Interactive charts and tables in a web interface.
- Automatic data collection, transformation, storage, and model retraining.
- REST API for clients and asynchronous event-driven communication between
  backend services.
- Docker-based deployment of the complete system.

## How the system works

The application uses a hybrid client-server and microservice architecture.
The main data flow is:

1. **Data collection** obtains electricity prices and weather data from external
   services.
2. **Data processing** converts the responses to tabular time-series data and
   aggregates hourly data when daily values are needed.
3. **Storage** persists time-series data in ClickHouse. Generated forecasts are
   cached in Redis for fast access.
4. **Forecasting** trains a Prophet model on historical prices. The model uses
   yearly, weekly, and daily seasonality, Czech holidays, and temperature as an
   additional regressor.
5. **Scheduling and messaging** use Apache Airflow to schedule data updates and
   Apache Kafka to notify services about processing tasks.
6. **Presentation** exposes the results through a FastAPI REST service and a
   Next.js frontend.

Open-Meteo provides weather forecasts for only a limited horizon. For the
remaining days of the monthly forecast, the data collection service estimates
temperatures from climate normals calculated from historical meteorological
data.

## Architecture

The repository contains the following main components:

- `DCS` — **Data Collection System**, a FastStream service that fetches
  electricity-price and weather data, transforms it with Pandas, and writes it
  to ClickHouse.
- `PS` — **Prediction Service**, a FastAPI service that reads data, trains the
  Prophet forecasting model, serves forecast and historical-data endpoints, and
  caches forecasts in Redis.
- `UI/electricity-forecasting` — Next.js and React frontend with interactive
  date-range and interval selection, charts, and forecast tables.
- `infra/airflow` — Apache Airflow scheduler and DAGs for initialization and
  recurring data updates.
- `infra/clickhouse` — ClickHouse image and database initialization scripts.
- `infra/kafka` — Kafka image and topic initialization scripts.

The services communicate over a Docker bridge network. Kafka is used for
asynchronous events, ClickHouse is the analytical time-series database, and
Redis stores the most recently generated forecasts.

## API

The Prediction Service is available at `http://localhost:8000` after startup.
Interactive API documentation is available at
`http://localhost:8000/docs`.

| Endpoint | Description |
| --- | --- |
| `GET /forecast/daily` | Return all available daily forecasts. |
| `GET /forecast/hourly` | Return all available hourly forecasts. |
| `GET /forecast/daily/date` | Return the daily forecast for a requested date. |
| `GET /forecast/hourly/date` | Return the hourly forecast for a requested date. |
| `GET /forecast/daily/oldData` | Return historical daily data for `start_date` and `end_date`. |
| `GET /forecast/hourly/oldData` | Return historical hourly data for `start_date` and `end_date`. |

Date parameters use the `YYYY-MM-DD` format. The date-specific endpoints use
the `datetime` request parameter; historical-data endpoints use `start_date`
and `end_date`.

## Running the application

### Requirements

- Docker and Docker Compose
- Internet access for the external price and weather data providers

### Start all services

From the repository root, build and start the complete application:

```bash
docker compose build
docker compose up -d
```

The first startup can take several minutes because the images install Python
and frontend dependencies and the services wait for their health checks.

The main services are available at:

| Service | URL or port |
| --- | --- |
| Web UI | `http://localhost:3000` |
| FastAPI and Swagger UI | `http://localhost:8000/docs` |
| Airflow | `http://localhost:8081` |
| Kafka UI | `http://localhost:8888` |
| ClickHouse HTTP interface | `http://localhost:8123` |
| Redis | `localhost:6379` |

To follow service logs or stop the application:

```bash
docker compose logs -f
docker compose down
```

The Compose configuration uses development credentials and local service
addresses. Change them before using the application in a shared or production
environment.

## Testing

The backend Docker images run their pytest suites before starting the
corresponding service. Tests include unit checks and integration checks for
Kafka, ClickHouse, and external data providers.

The backend tests can also be run locally from their respective directories:

```bash
cd DCS
pytest

cd ../PS
pytest
```

## Technology stack

- **Backend:** Python 3.10, FastAPI, FastStream, Pandas, NumPy, Prophet
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Recharts
- **Data storage:** ClickHouse and Redis
- **Messaging:** Apache Kafka
- **Orchestration:** Apache Airflow
- **Deployment:** Docker and Docker Compose

## Project status

This repository contains the implemented prototype described in the bachelor
thesis. It is intended for local demonstration and further development rather
than for production deployment without additional security, monitoring,
scaling, and secret-management configuration.
