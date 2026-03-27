# 🧩 S2O API — Backend Service (FastAPI · MVC Architecture)
This project provides the backend API for the SaaS Smart Restaurant Management Platform (S2O).
It follows a FastAPI + MVC + Clean Architecture approach to ensure scalability, maintainability, and modular development.
---

## 🏗 Project Structure
```
s2o-api/
│── app/
│   ├── main.py            # Entry point FastAPI
│   ├── controllers/       # Controller (route handlers)
│   ├── models/            # Database models (SQLAlchemy)
│   ├── schemas/           # Pydantic request/response
│   ├── views/             # Response formatting / view logic
│   ├── utils/             # Helper functions
│   └── db/                # Database connections
│
├── run.ps1                # Script chạy nhanh cho Windows
├── run.sh                 # Script chạy nhanh cho Linux/macOS
├── requirements.txt       # Danh sách thư viện Python
└── README.md              # Tài liệu dự án
```
## 🔧 Create Virtual Environment
    python -m venv .venv
    .\.venv\Scripts\activate
## 📦Install Dependencies
    pip install -r requirements.txt

## ✅ Test And Quality Gate
Run the local quality flow with:

```bash
pytest
pytest --cov=. --cov-report=xml
ruff check .
```

For test isolation, use `.env.test.example` as the reference test environment.

## 📖 Full System Documentation

Complete documentation of the system architecture, modules, and workflows:

🔗 https://github.com/huytran2005/s2o-docs/blob/master/README.md
