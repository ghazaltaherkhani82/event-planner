#  Event Planet

> **Event Planning & Management Platform**

Event Planet is a modular, API-first event planning and management platform built with **Django**, **Django REST Framework**, and **PostgreSQL**.

The platform supports multiple user roles, event lifecycle management, multi-stage events, dynamic type-safe attributes using an **EAV (Entity-Attribute-Value)** design, event registrations, participant feedback, and event results.

The project is designed around a RESTful API architecture and can be run consistently using **Docker Compose**.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Key Features](#-key-features)
* [Architecture](#-architecture)
* [Technology Stack](#-technology-stack)
* [User Roles](#-user-roles)
* [Event Lifecycle](#-event-lifecycle)
* [Multi-Stage Events](#-multi-stage-events)
* [Dynamic Attributes](#-dynamic-attributes)
* [Registrations](#-registrations)
* [Feedback](#-feedback)
* [Results](#-results)
* [API Structure](#-api-structure)
* [Authentication](#-authentication)
* [API Endpoints](#-api-endpoints)
* [Project Structure](#-project-structure)
* [Database Design](#-database-design)
* [Business Rules](#-business-rules)
* [Docker Setup](#-docker-setup)
* [Environment Variables](#-environment-variables)
* [Running the Project](#-running-the-project)
* [Creating a Superuser](#-creating-a-superuser)
* [API Usage Examples](#-api-usage-examples)
* [Testing](#-testing)
* [Security Notes](#-security-notes)
* [Development Notes](#-development-notes)
* [Future Improvements](#-future-improvements)
* [Author](#-author)

---

# 🎯 Overview

Event Planet was designed as an **API-first event management system** where different types of users can interact with events according to their roles and permissions.

The platform provides two main user roles:

* 👤 **Participant** — discovers published events, registers for them, views registrations, and submits feedback after an event is finished.
* 🧑‍💼 **Organizer** — creates and manages events, controls event status, manages stages and dynamic attributes, views registered participants, and manages event results.

The system also provides a flexible dynamic attribute architecture so that different event types can have their own custom properties without modifying the database schema or adding a new column for every attribute.

---

# ✨ Key Features

## 👤 User Management

* User registration
* User login
* Token-based authentication
* Custom Django User model
* Role-based users
* User profile endpoint
* Participant and Organizer roles
* Optional phone number

## 📅 Event Management

* Create events
* Retrieve events
* Update events
* Delete events
* Event ownership
* Event capacity management
* Event start/end time
* Event status management
* Event lifecycle validation
* Registered participant count
* Remaining capacity calculation

## 🔄 Event Lifecycle

Events support multiple states:

* `Draft`
* `Published`
* `Closed`
* `Finished`
* `Cancelled`

Valid status transitions are enforced by the application.

## 🧩 Multi-Stage Events

An event can contain multiple stages.

Each stage can have:

* Title
* Description
* Order
* Capacity
* Start time
* End time
* Stage roles

Stages are automatically ordered by their `order` field.

## 🏷️ Dynamic Attributes

Event Planet uses a type-safe **EAV architecture** for event-specific attributes.

Supported attribute types include:

* `TEXT`
* `INTEGER`
* `BOOLEAN`
* `FLOAT`

The implementation does **not** use `JSONField` for dynamic attributes.

## 📝 Registrations

Participants can:

* View available events
* Register for published events
* View their registrations
* Cancel registrations when allowed

The system prevents:

* Duplicate registrations
* Registration for unpublished events
* Registration when the event is full

## ⭐ Feedback

Registered participants can submit feedback after an event has finished.

Feedback includes:

* Rating from 1 to 5
* Comment
* Participant
* Event
* Creation timestamp

Duplicate feedback for the same event by the same participant is prevented.

## 🏆 Results

Organizers can manage event results containing:

* Participant
* Score
* Rank
* Remarks
* Publication timestamp

Each participant can have only one result per event.

---

# 🏗️ Architecture

Event Planet follows a modular Django architecture.

The project is divided into independent applications based on business responsibilities:

```text
accounts
    └── Authentication, users and roles

events
    └── Events, stages and results

attributes
    └── Dynamic event attributes

relations
    └── Registrations and feedback

config
    └── Django project configuration
```

The API is organized under the `/api/` namespace:

```text
/api/accounts/
/api/events/
/api/relations/
/api/attributes/
```

The project also contains a lightweight Django template-based home page.

---

# 🛠️ Technology Stack

| Technology                  | Purpose                       |
| --------------------------- | ----------------------------- |
| Python                      | Programming language          |
| Django                      | Backend web framework         |
| Django REST Framework       | REST API development          |
| PostgreSQL                  | Relational database           |
| psycopg2                    | PostgreSQL database adapter   |
| Django Token Authentication | API authentication            |
| django-cors-headers         | CORS configuration            |
| python-dotenv               | Environment configuration     |
| Docker                      | Containerization              |
| Docker Compose              | Multi-container orchestration |

The project's dependencies are defined in `requirements.txt`.

---

# 👥 User Roles

Event Planet currently supports two primary roles.

## Participant

Participants are regular users who can interact with published events.

Typical capabilities include:

* Registering an account
* Logging in
* Viewing published events
* Viewing event details
* Registering for an event
* Viewing their registrations
* Cancelling a registration
* Submitting feedback after a finished event

## Organizer

Organizers are responsible for managing events.

They can:

* Create events
* Update events
* Manage their own events
* Change event status
* Create event stages
* Manage dynamic attributes
* View event participants
* Create/manage event results

The custom user model defines `ORGANIZER` and `PARTICIPANT` roles.

---

# 🔐 Authentication & Authorization

The project uses **Django REST Framework Token Authentication**.

Authentication is configured globally through:

```text
TokenAuthentication
```

Protected API requests should include the token using the following HTTP header:

```http
Authorization: Token <your-token>
```

Users receive a token during registration or login.

### Registration

```http
POST /api/accounts/register/
```

### Login

```http
POST /api/accounts/login/
```

### Profile

```http
GET /api/accounts/profile/
```

The registration and login endpoints return the authentication token together with user information.

---

# 🔄 Event Lifecycle

An Event Planet event supports the following statuses:

```text
Draft
  │
  ├──────────────► Cancelled
  │
  ▼
Published
  │
  ├──────────────► Cancelled
  │
  ├──────────────► Finished
  │
  ▼
Closed
  │
  ├──────────────► Published
  │
  ├──────────────► Cancelled
  │
  ▼
Finished
```

The implemented transition rules are:

| Current Status | Allowed Next Status                  |
| -------------- | ------------------------------------ |
| `Draft`        | `Published`, `Cancelled`             |
| `Published`    | `Closed`, `Finished`, `Cancelled`    |
| `Closed`       | `Finished`, `Published`, `Cancelled` |
| `Finished`     | None                                 |
| `Cancelled`    | None                                 |

Invalid transitions raise a validation error.

The lifecycle is implemented in the `Event.transition_to()` method.

---

# 🧩 Multi-Stage Events

Events can contain multiple stages through the `EventStage` model.

Each stage belongs to one event and contains:

```text
EventStage
├── event
├── title
├── description
├── order
├── capacity
├── start_time
├── end_time
└── stage_roles
```

Stages are ordered using the `order` field.

Examples of possible event structures include:

```text
Workshop
├── Introduction
├── Practical Session
└── Final Project
```

or:

```text
Tournament
├── Qualifying Round
├── Semi Final
└── Final
```

### Registration Architecture Decision

Registration is implemented at the **event level**, rather than at the stage level.

A participant registers for an event through:

```text
Registration
    └── Event
    └── Participant
```

Stage-level registration is not implemented as a separate registration entity.

### Capacity Architecture Decision

The primary registration capacity is defined at the **event level**.

Each stage also has an optional `capacity` field for stage-specific information, but the implemented registration validation checks the event's capacity.

---

# 🏷️ Dynamic Attributes

One of the main architectural features of Event Planet is the implementation of dynamic event attributes using a **type-safe EAV pattern**.

Instead of adding database columns such as:

```text
webinar_platform
difficulty_level
number_of_rounds
court_type
```

for every possible event type, attributes are stored independently.

## Attribute Definition

An attribute contains:

```text
Attribute
├── name
├── label
├── data_type
└── description
```

Supported data types are:

```text
TEXT
INTEGER
BOOLEAN
FLOAT
```

## Event Attribute Value

Each event can have a value for an attribute:

```text
Event
   │
   └── EventAttributeValue
          ├── event
          ├── attribute
          ├── value_text
          ├── value_int
          ├── value_bool
          └── value_float
```

Only the appropriate typed value is used according to the attribute's declared data type.

For example:

```text
Attribute:
name = difficulty
data_type = TEXT
```

could be assigned to an event as:

```text
Event: Python Workshop
Attribute: difficulty
Value: Intermediate
```

Another event could reuse the same attribute:

```text
Event: Django Workshop
Attribute: difficulty
Value: Advanced
```

This design provides:

* Reusable attribute definitions
* Event-specific values
* Type-safe storage
* No `JSONField`
* No schema modification for every new event property
* Separation between attribute metadata and attribute values

The implementation stores typed values in dedicated columns and uses validation/conversion logic when values are assigned.

---

# 📝 Registrations

Registration is represented by the `Registration` model.

Each registration connects:

```text
Participant
      │
      ▼
Registration
      │
      ▼
Event
```

Registration statuses are:

```text
CONFIRMED
CANCELLED
```

## Registration Rules

The API enforces the following rules:

### 1. Event must be published

Participants can only register for events whose status is:

```text
Published
```

### 2. Capacity is checked

Before creating a confirmed registration, the system counts confirmed registrations and compares the result with the event capacity.

### 3. Duplicate registration is prevented

The database and serializer validation prevent the same participant from registering for the same event more than once.

### 4. Registration ownership

When a participant creates a registration, the participant is taken from the authenticated user rather than being freely supplied by the client.

These rules are implemented both at the serializer/model level.

---

# ❌ Registration Cancellation

Participants can cancel their registration through:

```http
POST /api/relations/events/<event_id>/cancel/
```

Cancellation is not allowed if the event has already:

* Finished
* Been cancelled

When cancellation is allowed, the registration is removed from the system.

---

# ⭐ Feedback

Feedback is represented by the `Feedback` model.

Each feedback contains:

```text
event
participant
rating
comment
created_at
```

The rating must be between:

```text
1 - 5
```

## Feedback Rules

Feedback can only be submitted when:

1. The event is `Finished`.
2. The authenticated user has a confirmed registration for that event.
3. The participant has not already submitted feedback for the event.

The model also enforces a unique relationship between an event and participant for feedback.

---

# 🏆 Event Results

Event results are represented by the `EventResult` model.

Each result contains:

```text
event
participant
score
rank
remarks
published_at
```

A participant can have only one result for a specific event.

This is enforced through:

```text
unique_together = ('event', 'participant')
```

Results are exposed through the event-specific results endpoint.

---

# 🌐 API Structure

The API is divided into four main modules:

```text
/api/accounts/
/api/events/
/api/relations/
/api/attributes/
```

The project's root URL configuration maps these application APIs accordingly.

---

# 📡 API Endpoints

## 👤 Accounts API

Base URL:

```text
/api/accounts/
```

| Method | Endpoint     | Description              | Authentication |
| ------ | ------------ | ------------------------ | -------------- |
| `POST` | `/register/` | Register a new user      | Public         |
| `POST` | `/login/`    | Login and receive token  | Public         |
| `GET`  | `/profile/`  | Get current user profile | Token          |

The registration endpoint accepts username, email, password, role and optional phone number.

---

## 📅 Events API

Base URL:

```text
/api/events/
```

| Method      | Endpoint                    | Description             |
| ----------- | --------------------------- | ----------------------- |
| `GET`       | `/`                         | List events             |
| `POST`      | `/`                         | Create an event         |
| `GET`       | `/<id>/`                    | Retrieve an event       |
| `PUT/PATCH` | `/<id>/`                    | Update an event         |
| `DELETE`    | `/<id>/`                    | Delete an event         |
| `POST`      | `/<id>/status/`             | Change event status     |
| `GET`       | `/<event_id>/stages/`       | List stages             |
| `POST`      | `/<event_id>/stages/`       | Create stage            |
| `GET`       | `/<event_id>/results/`      | List results            |
| `POST`      | `/<event_id>/results/`      | Create/update result    |
| `GET`       | `/<event_id>/participants/` | View event participants |

The event list endpoint exposes non-draft events publicly while allowing organizers to access their own events. Event creation automatically associates the authenticated user as the organizer.

---

## 🏷️ Attributes API

Base URL:

```text
/api/attributes/
```

| Method      | Endpoint                             | Description                  |
| ----------- | ------------------------------------ | ---------------------------- |
| `GET`       | `/definitions/`                      | List attribute definitions   |
| `POST`      | `/definitions/`                      | Create attribute definition  |
| `GET`       | `/definitions/<id>/`                 | Retrieve attribute           |
| `PUT/PATCH` | `/definitions/<id>/`                 | Update attribute             |
| `DELETE`    | `/definitions/<id>/`                 | Delete attribute             |
| `GET`       | `/events/<event_id>/`                | List event attribute values  |
| `POST`      | `/events/<event_id>/`                | Create event attribute value |
| `GET`       | `/events/<event_id>/<attribute_id>/` | Retrieve event attribute     |
| `PUT/PATCH` | `/events/<event_id>/<attribute_id>/` | Update event attribute       |
| `DELETE`    | `/events/<event_id>/<attribute_id>/` | Delete event attribute       |

Organizers are required for attribute creation and modification operations.

---

## 🔗 Relations API

Base URL:

```text
/api/relations/
```

| Method | Endpoint                     | Description           |
| ------ | ---------------------------- | --------------------- |
| `GET`  | `/registrations/`            | List registrations    |
| `POST` | `/registrations/`            | Register for an event |
| `GET`  | `/feedbacks/`                | List feedback         |
| `POST` | `/feedbacks/`                | Submit feedback       |
| `POST` | `/events/<event_id>/cancel/` | Cancel registration   |

Participants see their own registrations, while organizers can retrieve registrations associated with their events.

---

# 🔑 API Request Examples

## Register

```http
POST /api/accounts/register/
Content-Type: application/json
```

```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "PARTICIPANT",
  "phone_number": "09123456789"
}
```

A successful response contains the user's profile and an authentication token.

---

## Login

```http
POST /api/accounts/login/
Content-Type: application/json
```

```json
{
  "username": "john",
  "password": "securepassword"
}
```

Example response:

```json
{
  "token": "YOUR_AUTH_TOKEN",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "PARTICIPANT"
  }
}
```

---

## Authenticated Request

```http
GET /api/accounts/profile/
Authorization: Token YOUR_AUTH_TOKEN
```

---

## Create an Event

```http
POST /api/events/
Authorization: Token ORGANIZER_TOKEN
Content-Type: application/json
```

```json
{
  "title": "Django Workshop",
  "description": "Advanced Django REST Framework workshop",
  "capacity": 50,
  "start_time": "2026-10-01T09:00:00Z",
  "end_time": "2026-10-01T17:00:00Z",
  "status": "Draft"
}
```

The organizer is assigned automatically from the authenticated user.

---

## Publish an Event

```http
POST /api/events/1/status/
Authorization: Token ORGANIZER_TOKEN
Content-Type: application/json
```

```json
{
  "status": "Published"
}
```

The status transition is validated by the event lifecycle rules.

---

## Register for an Event

```http
POST /api/relations/registrations/
Authorization: Token PARTICIPANT_TOKEN
Content-Type: application/json
```

```json
{
  "event": 1
}
```

---

## Submit Feedback

```http
POST /api/relations/feedbacks/
Authorization: Token PARTICIPANT_TOKEN
Content-Type: application/json
```

```json
{
  "event": 1,
  "rating": 5,
  "comment": "Great event and very useful workshop."
}
```

Feedback is accepted only after the event is finished and only for a participant with a confirmed registration.

---

# 🗂️ Project Structure

```text
event-planner/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── attributes/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── events/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── relations/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/
├── templates/
│
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

The repository currently contains the four main Django applications plus the project configuration, Docker files, templates, static files, migrations, and dependency configuration.

---

# 🗄️ Database Design

The application uses PostgreSQL as its primary relational database.

The main entities can be represented conceptually as:

```text
                        ┌───────────────┐
                        │     User      │
                        │               │
                        │ Organizer     │
                        │ Participant   │
                        └───────┬───────┘
                                │
                    organizes   │
                                ▼
                        ┌───────────────┐
                        │     Event     │
                        ├───────────────┤
                        │ title         │
                        │ description   │
                        │ capacity      │
                        │ start_time    │
                        │ end_time      │
                        │ status        │
                        │ organizer     │
                        └───┬─────┬─────┘
                            │     │
              ┌─────────────┘     └──────────────┐
              ▼                                  ▼
      ┌───────────────┐                  ┌────────────────────┐
      │ EventStage    │                  │ Registration       │
      └───────────────┘                  └─────────┬──────────┘
                                                   │
                                                   ▼
                                                 User

              ┌───────────────────┐
              │ EventAttribute    │
              │ Value             │
              └─────────┬─────────┘
                        │
                        ▼
                   Attribute

              ┌───────────────────┐
              │     Feedback      │
              └───────────────────┘

              ┌───────────────────┐
              │   EventResult     │
              └───────────────────┘
```

### Main Relationships

* One Organizer → Many Events
* One Event → Many Stages
* One Event → Many Registrations
* One Participant → Many Registrations
* One Event → Many Feedback records
* One Event → Many Results
* One Event → Many Dynamic Attribute Values
* One Attribute Definition → Many Event Attribute Values

---

# 📏 Business Rules

The project implements important business rules at the serializer, model, view, and permission levels.

| Rule                                         | Implementation                   |
| -------------------------------------------- | -------------------------------- |
| Only published events can be registered for  | Registration validation          |
| Event capacity must not be exceeded          | Registration validation          |
| Duplicate registrations are forbidden        | Serializer + database constraint |
| Only authenticated users can register        | DRF permissions                  |
| Feedback requires a finished event           | Feedback validation              |
| Feedback requires confirmed registration     | Feedback validation              |
| Duplicate feedback is forbidden              | Serializer + database constraint |
| Event status transitions are validated       | `Event.transition_to()`          |
| Only the event organizer can change status   | View-level authorization         |
| Only the organizer can create stages         | View-level authorization         |
| Only the organizer can manage event results  | View-level authorization         |
| Attribute values are type-safe               | EAV validation                   |
| JSONField is not used for dynamic attributes | Dedicated typed columns          |
| Results are unique per participant/event     | Database constraint              |

---

# 🐳 Docker Setup

The project includes:

* `Dockerfile`
* `docker-compose.yml`

Docker Compose defines two main services:

```text
web
│
└── Django application

db
│
└── PostgreSQL 15
```

The PostgreSQL service uses the official:

```text
postgres:15-alpine
```

image.

The Django container runs:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

automatically when the container starts.

---

# ⚙️ Environment Variables

Create a `.env` file in the project root.

Example:

```env
DEBUG=True

SECRET_KEY=change-this-secret-key

DB_NAME=event_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

The Django settings read database configuration from environment variables.

### Environment Variable Reference

| Variable      | Description              | Example                  |
| ------------- | ------------------------ | ------------------------ |
| `DEBUG`       | Django debug mode        | `True`                   |
| `SECRET_KEY`  | Django secret key        | `change-this-secret-key` |
| `DB_NAME`     | PostgreSQL database name | `event_db`               |
| `DB_USER`     | PostgreSQL username      | `postgres`               |
| `DB_PASSWORD` | PostgreSQL password      | `postgres`               |
| `DB_HOST`     | PostgreSQL hostname      | `db`                     |
| `DB_PORT`     | PostgreSQL port          | `5432`                   |

> **Important:** Never commit production secrets, database passwords, or private credentials to a public repository.

---

# 🚀 Running the Project

## Prerequisites

Make sure you have installed:

* Docker
* Docker Desktop
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/ghazaltaherkhani82/event-planner.git
```

Move into the project directory:

```bash
cd event-planner
```

---

## 2. Create the Environment File

Create:

```text
.env
```

in the project root.

Example:

```env
DEBUG=True
SECRET_KEY=change-this-secret-key
DB_NAME=event_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

---

## 3. Start the Application

Run:

```bash
docker compose up --build
```

Or, depending on your Docker Compose installation:

```bash
docker-compose up --build
```

Docker Compose starts both:

```text
Django
PostgreSQL
```

and exposes Django on:

```text
http://localhost:8000/
```

The Compose configuration mounts the project directory into the Django container and loads environment variables from `.env`.

---

# 🧱 Database Migrations

Migrations are executed automatically by the Docker web container startup command:

```bash
python manage.py makemigrations
python manage.py migrate
```

If you need to run them manually:

```bash
docker compose exec web python manage.py makemigrations
```

```bash
docker compose exec web python manage.py migrate
```

---

# 👑 Creating a Superuser

To create a Django admin superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Then follow the prompts.

The Django administration panel is available at:

```text
http://localhost:8000/admin/
```

---

# 🖥️ Home Page

The project also contains a lightweight Django template-based home page.

The root URL is:

```text
http://localhost:8000/
```

The API itself remains the primary interface of the application.

---

# 🧪 Testing

The project contains Django test modules in the main applications, including:

```text
accounts/tests.py
events/tests.py
attributes/tests.py
relations/tests.py
```

Tests can be executed using Django's test runner:

```bash
docker compose exec web python manage.py test
```

For a specific application:

```bash
docker compose exec web python manage.py test events
```

or:

```bash
docker compose exec web python manage.py test relations
```

---

# 🔒 Security Notes

This project is configured primarily for development and educational purposes.

Before deploying to production, the following settings should be reviewed.

## Secret Key

Do not use a hard-coded development secret key in production.

Generate and provide a secure secret through environment variables.

## Debug Mode

Set:

```env
DEBUG=False
```

in production.

## Allowed Hosts

Replace:

```python
ALLOWED_HOSTS = ['*']
```

with a restricted list of trusted domains.

## CORS

The current configuration allows all origins:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

For production, restrict CORS to trusted frontend origins.

## Database Credentials

Database credentials should always be supplied through environment variables or a secure secret-management system.

---

# 🧠 Architectural Decisions

## Why EAV?

Events can have completely different characteristics depending on their type.

For example:

```text
Tournament
├── Number of rounds
└── Elimination type

Webinar
├── Platform
└── Recording available

Workshop
├── Difficulty
└── Prerequisites
```

Creating a new database column for every possible attribute would make the Event model increasingly complex.

The EAV architecture separates attribute definitions from event-specific values while keeping values type-safe.

---

## Why Event-Level Registration?

Registration is intentionally attached to the Event rather than individual stages.

This means:

```text
Participant
      │
      ▼
Registration
      │
      ▼
Event
      │
      ├── Stage 1
      ├── Stage 2
      └── Stage 3
```

A participant therefore registers for the overall event.

---

## Why Event-Level Capacity?

The main capacity belongs to the Event because registration is event-based.

The event's confirmed registration count is compared against its capacity before a new registration is accepted.

Stages may still define their own optional capacity metadata, but the main registration constraint is applied at the Event level.

---

# 📋 Example User Flow

## Participant Flow

```text
Register
   │
   ▼
Login
   │
   ▼
Receive Token
   │
   ▼
Browse Published Events
   │
   ▼
View Event Details
   │
   ▼
Register
   │
   ▼
Attend Event
   │
   ▼
Event → Finished
   │
   ▼
Submit Feedback
```

## Organizer Flow

```text
Register as Organizer
        │
        ▼
      Login
        │
        ▼
Create Event
        │
        ▼
      Draft
        │
        ▼
    Add Stages
        │
        ▼
Add Dynamic Attributes
        │
        ▼
    Published
        │
        ▼
Manage Registrations
        │
        ▼
      Closed
        │
        ▼
     Finished
        │
        ▼
 Publish / Manage Results
```

---

# 📦 Application Responsibilities

## `accounts`

Responsible for:

* Custom User model
* Authentication
* Registration
* Login
* User profile
* User roles
* Role permissions

## `events`

Responsible for:

* Events
* Event lifecycle
* Event stages
* Event results
* Participant listing

## `attributes`

Responsible for:

* Attribute definitions
* Dynamic event attributes
* Type-safe attribute values
* EAV implementation

## `relations`

Responsible for:

* Event registrations
* Registration cancellation
* Feedback
* Participant-event relationships

## `config`

Responsible for:

* Django settings
* URL routing
* WSGI
* ASGI
* REST Framework configuration

---

# 📈 Future Improvements

Possible future improvements include:

* API documentation using OpenAPI/Swagger
* Automated test coverage expansion
* Pagination and filtering for large event lists
* Search functionality
* More advanced stage-level permissions
* Dedicated result publication status
* Email notifications
* Event reminders
* Attendance tracking
* More dynamic attribute data types
* Production-ready CORS configuration
* Production deployment configuration
* CI/CD pipeline
* Rate limiting
* More granular object-level permissions
* Dedicated frontend application

---

# 🤝 Development Philosophy

Event Planet was designed with the idea that an event management system should be treated as a **software architecture problem**, not only as a collection of CRUD endpoints.

The project focuses on:

* Separation of responsibilities
* Modular Django applications
* API-first design
* Role-based access control
* Business-rule enforcement
* Relational data modeling
* Type-safe dynamic attributes
* Containerized development
* PostgreSQL-based persistence

---

# 📚 Main API Prefixes

For quick reference:

```text
Accounts:
    /api/accounts/

Events:
    /api/events/

Relations:
    /api/relations/

Attributes:
    /api/attributes/

Admin:
    /admin/
```

---

# 🌐 Repository

GitHub repository:

https://github.com/ghazaltaherkhani82/event-planner

---

# 👩‍💻 Author

**Ghazal Taherkhani**

GitHub:

https://github.com/ghazaltaherkhani82

---

# 📄 License

This project was created as an educational/software engineering project.

Unless a separate license is added to the repository, usage and redistribution should be considered subject to the repository owner's terms.

---

## ⭐ Event Planet

**A modular, API-first platform for planning, managing, and participating in events.**

> Build the event.
> Manage the experience.
> Connect the participants.
