# Viot

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


[![ci](https://github.com/tuanvumaihuynh/viot/actions/workflows/viot-test.yml/badge.svg)](https://github.com/tuanvumaihuynh/viot/actions/workflows/viot-test.yml)
[![codecov](https://codecov.io/gh/tuanvumaihuynh/viot/graph/badge.svg?token=SR54J5DMWD)](https://codecov.io/gh/tuanvumaihuynh/viot)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=tuanvumaihuynh_viot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=tuanvumaihuynh_viot)

> `Viot` is a project aimed at practicing the development of an IoT application.

## Technologies and frameworks

- Python 3.11
- FastAPI
- Celery
- Pytest
- Testcontainers
- EMQX MQTT
- TimescaleDB
- Redis
- Github Actions

## Architecture

![Architecture](./docs/architecture.png)

## Getting started

1. Clone the repository
2. Add the following records to your `/etc/hosts` file:
    ```
    127.0.0.1 api.viot.local
    127.0.0.1 flower
    127.0.0.1 mailpit
    127.0.0.1 emqx
    ```

3. Go to the project directory and run the following command to start the application:
    ```
    docker compose up -d
    ```

4. Run the following command to migrate the database:
    ```
    chmod +x ./scripts/migrate.sh
    ./scripts/migrate.sh
    ```

5. The application should now be running and accessible at:
- API: `http://api.viot.local/docs` (Swagger UI)
- Celery Flower: `http://flower/` (Account login: `admin/admin`)
- Mailpit: `http://mailpit/` (Account login: `admin/admin`)
- EMQX: `http://emqx/` (Account login: `admin/admin`)

## Documentation

## Development
See [DEVELOPMENT.md](DEVELOPMENT.md) for details.

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.
