# 📊 AI Sales & Customer Analytics Platform

A production-grade, full-stack business analytics application designed to convert raw sales transactional data into actionable customer intelligence, sales projections, anomaly alerts, and natural-language executive insights.

---

## 🌟 Key Features

1. **Executive Sales Dashboard**: Real-time KPI summaries (Revenue, Profit, Margins, Order Counts, Average Order Value) with interactive category and regional filter controls.
2. **Flexible CSV/Excel Upload & Mapping Wizard**: Auto-detects headers, validates column types, handles missing values/duplicates, and computes a 0–100 Data Quality Score.
3. **RFM Customer Segmentation**: Quantile-based Recency, Frequency, and Monetary scoring (1–5) paired with transparent business segment rules (Champions, At Risk, Loyal, Churned).
4. **Unsupervised K-Means Clustering + PCA**: Automatically scales features, evaluates optimal cluster counts ($K$) via Elbow and Silhouette scores, and projects 2D coordinates using Principal Component Analysis for interactive scatter plot rendering.
5. **Sales Forecasting Engine**: Time-series aggregation combined with a Random Forest Regressor and calendar features to project 30, 60, or 90-day sales along with 95% confidence bounds and MAE/RMSE/MAPE evaluation metrics.
6. **Isolation Forest Anomaly Detection**: Unsupervised detection of transaction-level outliers (excessive discounts, input errors) and daily aggregate sales spikes or server crashes.
7. **Groq-Powered AI Business Analyst**: Controlled natural-language Q&A layer where user queries trigger deterministic Python analytics routines first; pre-calculated statistical facts are then passed to Groq (LLaMA 3.3 70B) for executive explanations.
8. **Stateless JWT Authentication**: Passwords hashed with `bcrypt`, user-isolated row-level dataset security, and safe `.env` secret management.

---

## 🏗️ Architecture

```
[ Business User ]
       │
       ▼
[ React 18 SPA (Vite + TypeScript + Tailwind CSS + Recharts) ]
       │
       │ (REST APIs with JWT Bearer Token)
       ▼
[ FastAPI Backend Gateway (Python 3.11) ]
       │
   ┌───┴──────────────────────────────────────────┐
   │ Analytics & ML Engine (Pandas, Scikit-learn) │
   └───┬──────────────────────────────────────────┘
       │
       ├───────────────────────┬───────────────────────┐
       ▼                       ▼                       ▼
[(Trusted Metrics)]    [(Outlier/Cluster)]     [(SQLite Database)]
       │                       │               (Users, Datasets, Runs)
       ▼                       │
[ Groq API (LLaMA 3.3) ] ◄─────┘
(Natural Language Reasoning)
```

> **Product Principle**: The LLM is **never** allowed to calculate raw business data or run arbitrary SQL. Python + Pandas is the primary source of truth; the LLM merely translates pre-calculated facts into natural-language business guidance.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Recharts, Lucide React, Axios.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy ORM, SQLite.
- **Data Analytics & ML**: Pandas, NumPy, Scikit-learn (KMeans, StandardScaler, PCA, Random Forest Regressor, Isolation Forest).
- **AI / LLM**: Groq API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`).
- **Security**: PyJWT, Bcrypt password hashing.

---

## 🚀 Quickstart & Local Setup

### 1. Backend Setup

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Ensure `.env` contains:
```env
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET=your_super_secret_key
DATABASE_URL=sqlite:///./app.db
FRONTEND_URL=http://localhost:5173
```

Run FastAPI backend:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend API documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Install node dependencies
npm install

# Create .env file
cp .env.example .env
```

Ensure frontend `.env` contains:
```env
VITE_API_URL=http://localhost:8000
```

Run frontend dev server:
```bash
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

```bash
cd backend
.venv/Scripts/python -m pytest ../tests
```

---

## 🎓 Technical Interview Q&A Guide

### Beginner Questions

**Q1: Why did you choose FastAPI over Flask or Django for this project?**
> *Answer*: FastAPI offers built-in async support, automatic request/response data validation via Pydantic, and instant interactive Swagger UI generation (`/docs`). For an analytics API where data schemas are strictly enforced, FastAPI provides superior developer ergonomics and speed compared to Flask (which requires manual validation extensions) andDjango (which includes unnecessary monolithic overhead like admin templates).

**Q2: What is RFM Analysis and why is it useful?**
> *Answer*: RFM stands for Recency (how recently a customer bought), Frequency (how often they buy), and Monetary value (how much they spend). It is a classic marketing segmentation framework that ranks customers into quintiles (scores 1–5). It enables businesses to quickly identify high-value "Champions" versus churn-risk accounts without complex machine learning.

### Intermediate Questions

**Q3: How did you determine the number of clusters ($K$) for K-Means?**
> *Answer*: We implemented an automated evaluation pipeline (`run_kmeans_evaluation`) that iterates $K$ from 2 to 8. For each $K$, we calculate WCSS (inertia) for the Elbow Method and the Silhouette Score (which measures how well-separated clusters are). The user can inspect these charts or let the system fit $K$ dynamically based on peak silhouette scores.

**Q4: Why is feature scaling mandatory before running K-Means and PCA?**
> *Answer*: K-Means relies on Euclidean distance measurements, and PCA calculates orthogonal variance vectors. If features are on unscaled ranges—for instance, Monetary spend in thousands ($10,000) versus Frequency in single digits (5)—the Monetary feature will completely dominate the distance calculations. Using `StandardScaler` (Z-score normalization) ensures every feature contributes equally.

### Advanced Questions

**Q5: Why shouldn't the LLM calculate raw business metrics directly from raw data?**
> *Answer*: LLMs are probabilistic language pattern matchers, not deterministic mathematical calculators. Allowing an LLM to aggregate numbers or write raw SQL directly over user datasets introduces hallucination risk, computational inefficiency, and severe security vulnerabilities (SQL injection / prompt injection). By enforcing a strict pipeline (Data -> Python Pandas -> Pre-calculated Json -> LLM Context), we guarantee 100% mathematical accuracy while retaining natural language fluency.

**Q6: How do you prevent cross-user data leaks in multi-tenant mode?**
> *Answer*: We enforce strict row-level authorization dependencies in FastAPI (`get_user_dataset`). Every dataset and generated artifact is bound to a `user_id`. When a user requests any dataset endpoint (`/api/analytics/{dataset_id}`), the dependency checks `dataset.user_id == current_user.id`. If unauthorized, a `403 Forbidden` error is returned immediately before reading any file off disk.
