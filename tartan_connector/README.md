# ADP → Tartan Connector (Django REST Framework)

This project is a **mock connector** that simulates the ADP API and converts ADP employee data into **Tartan Unified HRMS JSON format**.
It uses **Django + Django REST Framework (DRF)** and implements **OAuth 2.0 (Client Credentials flow)** for authentication.

---

## Project Structure

```
tartan_connector/
├── manage.py
├── requirements.txt
├── README.md
├── tartan_connector/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── connector/
    ├── models.py
    ├── serializers.py
    ├── permissions.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

---

## Setup Instructions

### 1. Clone the project and install dependencies

```terminal
git clone https://github.com/divyachaudhary0210/adp_to_tartan_connector.git
cd tartan_connector
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run migrations

```terminal
python manage.py migrate
```

### 3. Create an OAuth client (needed for authentication)

```terminal
python manage.py shell
```

Inside the shell:

```python
from connector.models import OAuthClient
OAuthClient.objects.create(client_id="client1", client_secret="secret_key_1", name="testclient1")
exit()
```

This will create one valid client with:

* **client_id:** `client1`
* **client_secret:** `secret_key_1`

---

### 4. Start the server

```bash
python manage.py runserver
```

Server runs on **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## API Endpoints

### 1. `/api/token/` — Get Access Token

**Method:** `POST`
**Auth:** No authentication required
**Description:** Issues an OAuth2-style token using the `client_credentials` grant type.

**URL:**

```
http://127.0.0.1:8000/api/token/
```

**Body:**
In Postman → Body → **x-www-form-urlencoded**:

| KEY           | VALUE              |
| ------------- | ------------------ |
| client_id     | client1            |
| client_secret | secret_key_1       |
| grant_type    | client_credentials |

**Example Response:**

```json
{
  "access_token": "b7d7f20ffb4a4c61a4b0a41775ad9093",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

### 2. `/api/mock-adp/employees/` — Get Mock ADP Employees

**Method:** `GET`
**Auth:** No authentication required
**Description:** Returns mock ADP employee information (since real ADP API is unavailable).

**URL:**

```
http://127.0.0.1:8000/api/mock-adp/employees/
```

**Example Response:**

```json
[
  {
    "id": "adp-1001",
    "employeeId": "EMP-1042",
    "firstName": "John",
    "lastName": "Doe",
    "workEmail": "john.doe@acmecorp.com",
    "employmentStatus": "Active",
    "department": "Engineering",
    "company": {"legalName": "Acme Corporation Inc."}
  }
]
```

---

### 3. `/api/transform/` — Transform ADP → Tartan Format

**Method:** `POST`
**Auth:** Requires Bearer token
**Description:**

* Fetches mock ADP employees internally
* Converts them to **Tartan Unified HRMS JSON** (field mapping as per the assignment PDF)
* Saves both raw and transformed data into DB
* Returns the unified Tartan format JSON

**URL:**

```
http://127.0.0.1:8000/api/transform/
```

**Headers:**

| KEY           | VALUE                   |
| ------------- | ----------------------- |
| Authorization | Bearer `<the_access_token_we_got>` |
| Content-Type  | application/json        |

**Example Response:**

```json
[
  {
    "employee_number": "EMP-1042",
    "first_name": "John",
    "middle_name": "M.",
    "last_name": "Doe",
    "preferred_name": "Johnny",
    "display_full_name": "John M. Doe",
    "work_email": "john.doe@acmecorp.com",
    "employment_status": "Active",
    "department": "Engineering",
    "company": {
      "legalName": "Acme Corporation Inc.",
      "displayName": "Acme Corp"
    },
    "employments": [
      {
        "jobTitle": "Senior Software Engineer",
        "payRate": "9500.0000"
      }
    ],
    "salaries": [
      {
        "payDate": "2025-09-30T00:00:00Z",
        "grossPayDetails": {"base": 9500, "bonus": 500}
      }
    ]
  }
]
```

## WORKFLOW

1. Create OAuth client (`client1`, `secret_key_1`)
2. Obtain access token → `/api/token/`
3. Test mock data → `/api/mock-adp/employees/`
4. Transform to Tartan format → `/api/transform/`

---

## Tech Stack

* **Django 4.2**
* **Django REST Framework 3.14**
* **SQLite (default)**
