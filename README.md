# Event Planner Project

A modular Django-based event management system utilizing a type-safe EAV (Entity-Attribute-Value) pattern for dynamic attributes, REST Framework API, and PostgreSQL.

## Prerequisites
- Docker & Docker Desktop installed and running on your system.

## Environment Variables (.env)
Create a `.env` file in the root directory of the project with the following configuration variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=eventplanet_db
DB_USER=postgres
DB_PASSWORD=1234post
DB_HOST=db
DB_PORT=5432docker 