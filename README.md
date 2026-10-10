\# Bulk Certificate Generator API



A REST API built with FastAPI and PostgreSQL that accepts bulk certificate-generation requests, validates recipient information, generates individual PDF certificates, and tracks job progress and failures.



\## Features



\- Bulk certificate-generation requests for up to 500 recipients per job

\- Email validation using Pydantic

\- PostgreSQL database with SQLAlchemy ORM

\- Background certificate generation using FastAPI BackgroundTasks

\- Individual PDF certificates generated using ReportLab

\- Job status and success/failure tracking

\- Certificate listing and PDF download endpoints

\- Per-recipient error handling

\- Automated API tests using pytest



\## Tech Stack



\- Python

\- FastAPI

\- PostgreSQL

\- SQLAlchemy

\- Pydantic

\- ReportLab

\- pytest



\## Project Structure



```text

bulk-certificate-generator/

├── app/

│   ├── main.py

│   ├── database.py

│   ├── models.py

│   ├── schemas.py

│   ├── create\_tables.py

│   ├── routers/

│   │   ├── jobs.py

│   │   └── certificates.py

│   └── services/

│       ├── certificate\_generator.py

│       └── job\_processor.py

├── tests/

│   └── test\_api.py

├── templates/

├── generated/

├── requirements.txt

└── README.md

```



\## Prerequisites



\- Python installed

\- PostgreSQL installed and running

\- A PostgreSQL database named `certificate\_generator`



\## Setup



\### 1. Clone or download the project



Open a terminal in the project directory.



\### 2. Create and activate a virtual environment



On Windows:



```cmd

python -m venv venv

venv\\Scripts\\activate

```



\### 3. Install dependencies



```cmd

python -m pip install -r requirements.txt

```



\### 4. Configure the database



Ensure PostgreSQL is running and create the database if it does not exist:



```sql

CREATE DATABASE certificate\_generator;

```



Configure `app/database.py` with the appropriate PostgreSQL connection URL for your local environment. Do not commit database passwords or other secrets to Git.



\### 5. Create the database tables



```cmd

python -m app.create\_tables

```



\### 6. Start the API



```cmd

python -m uvicorn app.main:app --reload

```



The API will be available at:



`http://127.0.0.1:8000`



Interactive API documentation:



`http://127.0.0.1:8000/docs`



\## API Endpoints



| Method | Endpoint | Description |

|---|---|---|

| GET | `/` | Check API availability |

| POST | `/api/jobs/` | Create a bulk certificate-generation job |

| GET | `/api/jobs/{job\_id}` | Retrieve job status and counts |

| GET | `/api/jobs/{job\_id}/certificates` | List certificates belonging to a job |

| GET | `/api/certificates/{certificate\_id}/download` | Download an individual PDF |



\## Example: Create a Job



Send a POST request to `/api/jobs/` with this JSON body:



```json

{

&#x20; "recipients": \[

&#x20;   {

&#x20;     "name": "Aisha Khan",

&#x20;     "email": "aisha@example.com"

&#x20;   },

&#x20;   {

&#x20;     "name": "Rahul Sharma",

&#x20;     "email": "rahul@example.com"

&#x20;   }

&#x20; ]

}

```



A successful request returns HTTP `202 Accepted` with the job ID and initial status.



\## Check Job Status



Send a GET request to `/api/jobs/1`.



The response includes the job ID, status, total recipient count, successful certificate count, and failed certificate count.



\## List and Download Certificates



List certificates for a job:



`GET /api/jobs/1/certificates`



Download a certificate:



`GET /api/certificates/1/download`



Generated PDF files are saved in the `generated/` directory.



\## Run Tests



Run the automated tests with:



```cmd

python -m pytest tests\\test\_api.py -v

```



The current test suite checks the root endpoint, valid job creation, invalid email validation, missing jobs, and missing certificates.



\## Design Decisions



\### Background processing



FastAPI BackgroundTasks is used to process recipients after the job-creation response. This keeps the implementation simple and avoids requiring a separate task queue for the assignment.



\### Per-recipient failure handling



Each recipient is processed independently. A failure for one certificate is recorded without intentionally stopping processing of other recipients.



\### Database persistence



Job and certificate records are stored in PostgreSQL so status and result information remains available between API requests.



\### Certificate generation



ReportLab generates an individual landscape A4 PDF for each recipient using a predefined certificate layout.



\## Limitations and Future Improvements



\- Use a durable task queue such as Celery with Redis for reliable processing of long-running jobs.

\- Add authentication and authorization.

\- Add pagination for large certificate lists.

\- Add configurable certificate templates.

\- Add retry policies and structured logging.

\- Add integration tests for database persistence, background processing, and PDF contents.



\## License



Add the license required by your assignment or repository.



