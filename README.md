# RestockIQ

**RestockIQ** is a full-stack inventory management system commissioned by **Angel's Liquor**, a local family-owned store in **Plano, Texas**, to replace manual spreadsheet tracking with a modern web application. It combines a FastAPI + PostgreSQL backend with a React dashboard for real-time stock visibility across spirits, beer, mixers, wine, and ready-to-drink products.

Built by **Siddarth Morthala**.

## Why this project exists
Angel's Liquor needed a better way to:
- track on-hand inventory across hundreds of SKUs
- log sales and receive shipments from any device
- flag low-stock items before shelves go empty
- rotate perishables using FIFO sell-by tracking
- make smarter reorder decisions using supplier lead-time data
- review weekly sales and shrinkage metrics in Tableau without learning a new interface

## Stack
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, pytest
- **Frontend:** React (Vite), Recharts
- **Infra:** Docker Compose, GitHub Actions CI, AWS deployment notes
- **Analytics:** Tableau-ready PostgreSQL reporting view

## Core features
- Real-time stock updates for liquor-store inventory across multiple beverage categories
- Sale logging with oversell prevention and concurrency-safe stock updates
- Shipment receiving with lot-level sell-by dates for FIFO expiration tracking
- Auto-reorder suggestion engine using a sliding-window average and configurable par levels
- Supplier contact manager with average lead-time tracking and reorder context
- Weekly sales and shrinkage view that plugs directly into Tableau

## Demo data
The seeded demo environment includes realistic liquor-store inventory and fictional distributors inspired by the North Texas beverage market, such as large Texas distributors and specialty craft/spirits wholesalers.

Included sample categories:
- spirits
- beer
- craft beer
- RTD cocktails
- mixers
- wine

## Quick start
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

docker compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Local development
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Seed data
```bash
cd backend
python -m app.seed
```

## Running tests
```bash
cd backend
pytest
```

The CI pipeline includes integration coverage for:
- oversell prevention
- concurrent stock update correctness

## Architecture
```text
React dashboard
   ↓
FastAPI service layer
   ↓
PostgreSQL inventory, lot, sales, shipment, and supplier tables
   ↓
Tableau-connected reporting view
```

## AWS deployment
This repo includes a Dockerized setup designed for AWS deployment.

Suggested production architecture:
- Frontend on **S3 + CloudFront** or **AWS Amplify**
- Backend on **ECS/Fargate** or **App Runner**
- PostgreSQL on **Amazon RDS**
- Secrets in **AWS Secrets Manager**
- Images stored in **ECR**

See `infra/aws-deploy-notes.md` for deployment guidance.

## Tableau reporting
See `sql/tableau_weekly_sales_shrinkage_view.sql` for the PostgreSQL view that powers the weekly sales and shrinkage dashboard.

## Suggested resume entry
**RestockIQ | React, FastAPI, PostgreSQL, Docker, AWS**  
- Built a full-stack inventory management system commissioned by a local family-owned liquor store in Plano, TX to replace spreadsheet-based stock tracking.  
- Developed FastAPI services and a React dashboard for sales logging, shipment intake, low-stock alerts, FIFO expiration tracking, and supplier management across hundreds of SKUs.  
- Implemented an auto-reorder engine using sliding-window sales averages and supplier lead times to improve replenishment decisions and reduce stockouts.  
- Containerized the app with Docker, added pytest integration coverage for oversell prevention and concurrent stock updates, and exposed a Tableau-ready PostgreSQL reporting view.
