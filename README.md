# Student Management API

A REST API built with **FastAPI**, **SQLAlchemy** (ORM), and **PostgreSQL** for managing student records. Supports CRUD operations, course filtering, sorting, and pagination.

## Features

- Create, read, update, and delete student records
- Filter students by course
- Sort students by any field (ascending/descending)
- Paginated list endpoint
- Pydantic request/response validation with custom field validators
- Computed `grade` field derived from marks (A–F)

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL (via psycopg2)
- Pydantic
- python-dotenv

## Project Structure

```
backend/
├── main.py          # FastAPI app: models, schemas, and all routes
├── playground.py    # Quick DB connection test script
├── TESTING.py       # Minimal DB connection test
├── students.json    # Sample student data (seed reference)
├── .env             # Database URL (keep secret in real projects)
└── venv/            # Virtual environment
```

## Setup

1. Install dependencies (already in the virtual environment):

```bash
pip install fastapi sqlalchemy pydantic psycopg2 python-dotenv uvicorn
```

2. Make sure PostgreSQL is running and create the database `students_db`.

3. Configure your database connection in `.env`:

```env
DATABASE_URL= postgresql://postgres:YOUR_PASSWORD@localhost:5432/students_db
```

4. Run the server:

```bash
uvicorn main:app --reload
```

The app auto-creates the `student_records` table on startup.

## API Endpoints

| Method | Path                  | Description                              |
|--------|-----------------------|------------------------------------------|
| GET    | `/student/{student_id}` | Get a single student by ID              |
| POST   | `/students`           | Create a new student                     |
| PUT    | `/student/{student_id}` | Update a student (partial update)       |
| DELETE | `/student/{student_id}` | Delete a student                        |
| GET    | `/students`           | List all students (filter/sort/paginate) |

### Query parameters (`GET /students`)

| Parameter  | Description                                | Default |
|------------|--------------------------------------------|---------|
| `course`   | Filter by course name                      | none    |
| `sort_by`  | Field to sort by (`id`, `name`, `age`, `email`, `course`, `marks`) | `id` |
| `order`    | Sort order (`asc` / `desc`)                | `asc`   |
| `page`     | Page number (≥ 1)                          | `1`     |
| `limit`    | Records per page (1–100)                   | `10`    |

## Example requests

**Create a student**
```bash
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{
    "id": "S001",
    "name": "Arun Kumar",
    "age": 21,
    "email": "arun@gmail.com",
    "course": "Computer Engineering",
    "marks": 85.5
  }'
```

**List students (page 1, sorted by marks descending)**
```bash
curl "http://localhost:8000/students?sort_by=marks&order=desc&page=1&limit=10"
```

## Notes

- `StudentUpdate` uses `exclude_unset=True`, so only fields present in the request body are applied — send partial updates safely.
- Names are validated to contain only alphabetic characters and are title-cased on write.
- Marks are clamped to 0–100 and ages to 0–100 by the Pydantic schemas.
- The `grade` computed field is returned automatically in responses based on marks.

## License

MIT