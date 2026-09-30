# 📖 Technical Walkthrough & Interview Guide

This walkthrough provides an in-depth, line-by-line explanation of the architecture, data flows, machine learning pipelines, and design decisions behind the **AI Sales & Customer Analytics Platform**. Use this guide to prepare for technical deep-dives in software engineering and AI/ML interviews.

---

## 1. System Overview & Data Flow

```
1. File Upload (CSV/XLSX)
   └──> Saved to disk (`data_store/user_{id}/raw/`)
        └──> Header Fuzzy Matching (`data_loader.py`)

2. Column Mapping & Cleaning
   └──> Type Coercion & Null Handling (`data_cleaner.py`)
        └──> Saved clean CSV (`data_store/user_{id}/cleaned/`)
        └──> Data Quality Score (0 - 100)

3. Python Analytics Engine
   ├──> Sales KPIs & Growth Comparison (`sales_analytics.py`)
   ├──> RFM Quintile Scoring (`rfm_analysis.py`)
   ├──> K-Means + PCA (`customer_segmentation.py`)
   ├──> Random Forest Forecast (`forecasting_service.py`)
   └──> Isolation Forest Outliers (`anomaly_detection.py`)

4. AI Reasoning & Natural Language Layer
   └──> Intent Classifier (`ai_analyst.py`)
        └──> Fact Prompt Formulation
             └──> Groq LLaMA 3.3 70B Response
```

---

## 2. Core Technical Components

### A. Data Loader & Fuzzy Column Mapper (`data_loader.py`)
- Uses synonym dictionaries (`COLUMN_SYNONYMS`) covering standard headers (`order_id`, `order_date`, `customer_id`, `sales`, `quantity`, `profit`).
- Performs string normalization (stripping non-alphanumeric characters, converting to lowercase) to match uploaded headers automatically.
- Evaluates feature availability (`REQUIRED_GROUPS`) so optional features like RFM or Forecasting degrade gracefully if specific fields are missing.

### B. Data Cleaner & Quality Assurer (`data_cleaner.py`)
- Coerces dates using `pd.to_datetime(errors='coerce')` and drops invalid rows.
- Computes profit margin fallback (`sales * 0.3`) if profit is unmapped.
- Deduplicates rows using `df.drop_duplicates()`.
- Calculates a dynamic **Data Quality Score** starting at 100 with penalties for dropped rows, missing values, duplicate ratios, and negative sales values.

### C. RFM Analysis Engine (`rfm_analysis.py`)
- Groups transactions per customer and computes Recency (days since max date), Frequency (count of unique orders), and Monetary (sum of sales).
- Applies `pd.qcut` with `rank(method='first')` to assign quintile scores (1–5).
- Maps scores to transparent business segments (Champions, Loyal, Potential Loyalists, New, Promising, At Risk, Lost).

### D. Unsupervised Customer Clustering (`customer_segmentation.py`)
- Applies `np.log1p()` transformation to handle right-skewed financial data.
- Normalizes features using `StandardScaler`.
- Fits `KMeans` across $K \in [2, 8]$ and computes Silhouette Scores and WCSS (inertia) for Elbow analysis.
- Projects 3D RFM space onto 2D plane using `PCA(n_components=2)` for front-end rendering.

### E. Time-Series Sales Forecasting (`forecasting_service.py`)
- Resamples data daily to ensure uniform spacing (`resample('D').asfreq().fillna(0)`).
- Engineers calendar features (`trend`, `day_of_week`, `day_of_month`, `month`, `year`).
- Performs an 80/20 chronological train-test split.
- Fits a `Random Forest Regressor` model and computes MAE, RMSE, and MAPE.
- Generates 30/60/90-day future projections with 95% confidence intervals ($\hat{y} \pm 1.96 \cdot \sigma_{\text{residuals}}$).

### F. Anomaly Detection Engine (`anomaly_detection.py`)
- Trains an `Isolation Forest` model on normalized transaction features (`sales`, `quantity`, `profit`, `discount`).
- Flags the top 1.5% most extreme statistical outliers.
- Groups data by date to detect temporal sales crashes or abnormal spikes.

### G. AI Analyst Chat Engine (`ai_analyst.py`)
- Classifies user questions into deterministic intents using keyword pattern matching.
- Executes Python analytics routines first to extract factual metrics.
- Formulates a system prompt forcing Groq LLaMA 3.3 to act strictly as an explanation layer over pre-calculated numbers.

---

## 3. Lessons Learned & System Trade-offs

1. **SQLite to PostgreSQL Scalability**: While SQLite is ideal for local development, SQLAlchemy ORM abstractions allow seamlessly switching to PostgreSQL by simply updating the `DATABASE_URL` environment variable.
2. **Deterministic Intent Classification**: Relying on regex/keyword intent classification before passing data to the LLM guarantees sub-second response times and 0% risk of LLM code execution vulnerabilities.
3. **Bcrypt 72-Byte Limit**: Using `bcrypt` directly with safe 72-byte string encoding truncation ensures robust, cross-platform password hashing compatibility on Python 3.12.
