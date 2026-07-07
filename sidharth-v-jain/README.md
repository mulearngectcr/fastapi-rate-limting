# Todo CRUD API — v5: Rate Limiting

This iteration adds **rate limiting** on top of the authenticated,
validated Todo API from the previous version. Auth, CRUD, and validation
behavior are unchanged — requests now also have to stay under a request
quota, or they're rejected before reaching the endpoint logic.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set the API key:

```
API_KEY=my_secret_key
```

## Run

```bash
uvicorn main:app --reload
```

## Testing in /docs


| Test | Expected result |
|------|------------------|
| Call `GET /todos` 10 times within a minute | All succeed (`200`) |
| Call `GET /todos` an 11th time in the same minute | `429 Too Many Requests` |
| Call `POST /todos` 3 times within a minute | All succeed (`201`) |
| Call `POST /todos` a 4th time in the same minute | `429 Too Many Requests` |
| Wait for the minute to roll over | Limits reset, requests succeed again |


