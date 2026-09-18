"""
The three DSN Research programme shells, aligned to the skills that South
African public sector, municipal and parastatal data and AI tenders are
buying: assurance data analytics, cloud-native data products, and applied
ML with MLOps.

Each module becomes a Section with an overview, core concepts and guided
lab lesson, a knowledge-check quiz and a graded practical. Each programme
ends with a capstone assignment. Loaded by `manage.py seed_programmes`.

Question tuples are (text, question_type, [(choice_text, is_correct), ...]).
"""

CATEGORY = {
    "name": "Data Science & AI",
    "description": "Data analytics, machine learning and AI engineering programmes",
}


def q(text, choices, question_type=None):
    """Shorthand: question_type is inferred as single unless more than one choice is correct."""
    correct = sum(1 for _, ok in choices if ok)
    if question_type is None:
        question_type = "multiple" if correct > 1 else "single"
    return {"text": text, "question_type": question_type, "choices": choices}


def tf(text, answer):
    return q(text, [("True", answer), ("False", not answer)], "true_false")


PROGRAMMES = [
    # ------------------------------------------------------------------
    {
        "slug": "data-analytics-bi-foundation",
        "title": "Data Analytics & BI Foundation",
        "level": "beginner",
        "duration_months": 3,
        "tags": "sql,excel,python,pandas,power bi,data cleaning",
        "short_description": (
            "Three months from spreadsheets to SQL, Python and Power BI, ending with an "
            "automated operational dashboard built on a data cleaning pipeline."
        ),
        "description": (
            "This 12-week programme builds the analyst skill set that state entities, "
            "municipalities and utilities are actively procuring: querying operational data "
            "with SQL, cleaning and exploring it with Python, and reporting it through Power BI. "
            "Every module ends with a knowledge check and a graded practical, and the programme "
            "closes with a capstone that mirrors an internal audit or operations reporting brief."
        ),
        "requirements": (
            "Comfortable using a computer and spreadsheets. No programming experience required. "
            "A laptop able to run Power BI Desktop (Windows) or a browser-based alternative."
        ),
        "what_you_learn": (
            "Write SQL queries and joins against relational databases\n"
            "Clean, reshape and summarise data with pandas\n"
            "Run exploratory data analysis and communicate findings\n"
            "Model data for reporting and build Power BI dashboards\n"
            "Automate a repeatable cleaning and reporting pipeline"
        ),
        "target_audience": (
            "Career starters, administrators and finance or operations staff moving into "
            "analyst roles, and graduates who need a portfolio piece."
        ),
        "modules": [
            {
                "title": "Data foundations and Excel for analysis",
                "weeks": "Weeks 1 to 2",
                "overview": (
                    "What data analysts do in public sector and enterprise settings, how data flows "
                    "from operational systems into reports, and the Excel skills that remain the "
                    "entry point for most analysis work."
                ),
                "concepts": (
                    "Structured versus unstructured data. Tables, rows, columns and keys. Data types. "
                    "Excel tables, lookups (XLOOKUP, INDEX/MATCH), pivot tables, conditional "
                    "aggregation (SUMIFS, COUNTIFS) and basic charts. Documenting assumptions."
                ),
                "lab": (
                    "Take a municipal service-request export, build a pivot-based summary of requests "
                    "by ward and category, and produce a one-page summary with two charts."
                ),
                "quiz": [
                    q("Which Excel feature summarises a large table by category without formulas?",
                      [("Pivot table", True), ("Conditional formatting", False), ("Freeze panes", False), ("Data validation", False)]),
                    q("Which functions return a value from another table by matching a key?",
                      [("XLOOKUP", True), ("INDEX with MATCH", True), ("SUM", False), ("TRIM", False)]),
                    tf("A primary key must be unique for every row in a table.", True),
                ],
                "practical": {
                    "title": "Service request summary workbook",
                    "instructions": (
                        "Using the supplied service-request dataset, build a workbook with a cleaned data "
                        "table, a pivot summary by ward and category, and a short written interpretation "
                        "(max 300 words). Submit the .xlsx and your write-up."
                    ),
                },
            },
            {
                "title": "SQL fundamentals",
                "weeks": "Weeks 3 to 4",
                "overview": (
                    "Relational databases and the SQL you will use daily: selecting, filtering, "
                    "sorting, aggregating and joining tables."
                ),
                "concepts": (
                    "SELECT, WHERE, ORDER BY, LIMIT. Aggregates and GROUP BY with HAVING. INNER, LEFT "
                    "and FULL joins. NULL handling. Reading an entity relationship diagram."
                ),
                "lab": (
                    "Query a PostgreSQL copy of a procurement ledger to answer ten business questions, "
                    "from total spend by supplier to suppliers with no purchase orders."
                ),
                "quiz": [
                    q("Which clause filters groups after aggregation?",
                      [("HAVING", True), ("WHERE", False), ("ORDER BY", False), ("LIMIT", False)]),
                    q("A LEFT JOIN from orders to suppliers returns:",
                      [("All orders, with supplier columns NULL where no match exists", True),
                       ("Only orders that have a matching supplier", False),
                       ("Only suppliers with no orders", False)]),
                    q("Which statements are true about NULL in SQL?",
                      [("NULL = NULL evaluates to unknown, not true", True),
                       ("COUNT(column) ignores NULL values", True),
                       ("NULL is the same as zero", False)]),
                ],
                "practical": {
                    "title": "Procurement ledger queries",
                    "instructions": (
                        "Submit a .sql file with your answers to the ten ledger questions plus a short "
                        "note on any data quality issues you found. Each query must be commented."
                    ),
                },
            },
            {
                "title": "Advanced SQL and data modelling",
                "weeks": "Weeks 5 to 6",
                "overview": (
                    "Moving from single queries to analytical models: subqueries, window functions, "
                    "and the star schema that reporting tools expect."
                ),
                "concepts": (
                    "Subqueries and CTEs. Window functions (ROW_NUMBER, RANK, running totals). CASE "
                    "expressions. Facts, dimensions and grain. Slowly changing attributes. Views."
                ),
                "lab": (
                    "Design a star schema for utility meter readings, load it from raw extracts, and "
                    "write window-function queries for month-on-month consumption change."
                ),
                "quiz": [
                    q("Which function assigns a sequential number within a partition?",
                      [("ROW_NUMBER()", True), ("SUM()", False), ("COALESCE()", False), ("CAST()", False)]),
                    q("In a star schema, the table that holds measurable events is the:",
                      [("Fact table", True), ("Dimension table", False), ("Lookup table", False)]),
                    tf("A CTE (WITH clause) can make a long query easier to read and reuse.", True),
                ],
                "practical": {
                    "title": "Meter readings star schema",
                    "instructions": (
                        "Submit your schema diagram, the DDL to create it, the load script, and queries "
                        "that report month-on-month change per customer segment."
                    ),
                },
            },
            {
                "title": "Python for data analysis",
                "weeks": "Weeks 7 to 8",
                "overview": (
                    "Python as the analyst's scripting language: reading files, working with pandas "
                    "DataFrames and NumPy arrays, and producing repeatable analysis in notebooks."
                ),
                "concepts": (
                    "Python basics (variables, lists, dicts, functions). Jupyter notebooks. pandas "
                    "Series and DataFrames, selection, filtering, groupby, merge and pivot. NumPy "
                    "arrays and vectorised operations. Reading CSV, Excel and SQL sources."
                ),
                "lab": (
                    "Reproduce the module 1 Excel summary in pandas, then extend it with a groupby "
                    "across three dimensions and export the result to Excel."
                ),
                "quiz": [
                    q("Which pandas method combines two DataFrames on a key column?",
                      [("merge()", True), ("append()", False), ("describe()", False), ("melt()", False)]),
                    q("Which of these read tabular data into a DataFrame?",
                      [("pd.read_csv()", True), ("pd.read_excel()", True), ("pd.read_sql()", True), ("pd.to_numpy()", False)]),
                    tf("df.groupby('ward').size() returns the number of rows per ward.", True),
                ],
                "practical": {
                    "title": "Service requests in pandas",
                    "instructions": (
                        "Submit a Jupyter notebook (.ipynb) that loads the service-request dataset, "
                        "reproduces the module 1 summary, adds a three-way groupby, and exports to Excel. "
                        "Include markdown cells explaining each step."
                    ),
                },
            },
            {
                "title": "Data cleaning and exploratory analysis",
                "weeks": "Weeks 9 to 10",
                "overview": (
                    "Public sector datasets are messy. This module covers systematic cleaning, "
                    "profiling and exploratory data analysis that stands up to audit."
                ),
                "concepts": (
                    "Missing values, duplicates, inconsistent categories, dates and encodings. "
                    "Profiling with describe, value_counts and isna. Outlier detection. Distributions "
                    "and correlations. Matplotlib and seaborn basics. Writing a data quality report."
                ),
                "lab": (
                    "Clean a supplier master file with duplicated and misspelt supplier names, "
                    "standardise it, and produce a data quality report with before and after metrics."
                ),
                "quiz": [
                    q("Which pandas call shows how many missing values each column has?",
                      [("df.isna().sum()", True), ("df.dropna()", False), ("df.fillna(0)", False), ("df.head()", False)]),
                    q("Which are reasonable ways to handle a missing numeric value?",
                      [("Impute with the median", True), ("Flag it and keep the row", True), ("Silently replace with 0 without noting it", False)]),
                    tf("Duplicate supplier records can inflate spend totals in a report.", True),
                ],
                "practical": {
                    "title": "Supplier master data quality report",
                    "instructions": (
                        "Submit the cleaning notebook and a PDF data quality report that lists each issue "
                        "found, the rule applied, and the number of records affected."
                    ),
                },
            },
            {
                "title": "Power BI dashboards and reporting",
                "weeks": "Weeks 11 to 12",
                "overview": (
                    "Turning a clean model into a dashboard decision makers use: Power Query, the data "
                    "model, DAX measures and report design."
                ),
                "concepts": (
                    "Power Query transformations. Relationships and the star schema in Power BI. "
                    "Measures with DAX (SUM, CALCULATE, time intelligence). Visual selection, filters "
                    "and slicers. Row-level security. Scheduled refresh."
                ),
                "lab": (
                    "Build a service-delivery dashboard on the module 3 star schema with KPIs, a "
                    "trend view, and drill-through to record level."
                ),
                "quiz": [
                    q("Which DAX function changes the filter context of a calculation?",
                      [("CALCULATE", True), ("SUM", False), ("RELATED", False), ("FORMAT", False)]),
                    q("Which of these belong in Power Query rather than DAX?",
                      [("Splitting a column", True), ("Removing duplicate rows", True), ("A year-to-date measure", False)]),
                    tf("Row-level security restricts which rows a viewer can see in a report.", True),
                ],
                "practical": {
                    "title": "Service-delivery dashboard",
                    "instructions": (
                        "Submit the .pbix file and a two-page design note covering the data model, the "
                        "measures you defined, and who the dashboard is for."
                    ),
                },
            },
        ],
        "capstone": {
            "title": "Capstone: automated operational dashboard and cleaning pipeline",
            "brief": (
                "Choose an operational dataset (service requests, procurement, meter readings or one "
                "you source yourself). Build a repeatable Python cleaning pipeline that loads into a "
                "SQL star schema, and a Power BI dashboard on top of it. Present it as if to a head of "
                "department who needs to trust the numbers."
            ),
            "instructions": (
                "Submit a repository link containing the pipeline code and schema, the .pbix file, a "
                "data quality report, and a five-minute recorded walkthrough. Assessment covers "
                "correctness, reproducibility, clarity of the dashboard and the quality of your "
                "explanation."
            ),
        },
    },
    # ------------------------------------------------------------------
    {
        "slug": "applied-data-science-machine-learning",
        "title": "Applied Data Science & Machine Learning",
        "level": "intermediate",
        "duration_months": 6,
        "tags": "python,scikit-learn,sql,git,streamlit,forecasting,anomaly detection",
        "short_description": (
            "Six months of applied machine learning with scikit-learn, from statistics to a "
            "predictive risk or demand-forecasting web app deployed live."
        ),
        "description": (
            "This 24-week programme takes learners who can already write basic Python and SQL and "
            "makes them job-ready data scientists. The curriculum follows the assurance analytics "
            "and insight work that utilities and metros are procuring: risk scoring, anomaly and "
            "fraud detection, and demand forecasting, with every model shipped as a working "
            "Streamlit application."
        ),
        "requirements": (
            "Basic Python and SQL (the Data Analytics & BI Foundation programme or equivalent). "
            "Comfortable with secondary school mathematics. A laptop with 8 GB RAM or more."
        ),
        "what_you_learn": (
            "Apply statistics and probability to real decisions\n"
            "Engineer features from messy operational data\n"
            "Train, tune and evaluate supervised models with scikit-learn\n"
            "Detect anomalies and segment data with unsupervised methods\n"
            "Forecast demand with time series models\n"
            "Ship a model as a live Streamlit application under version control"
        ),
        "target_audience": (
            "Analysts moving into data science, developers adding ML to their toolkit, and "
            "graduates in quantitative fields who need applied experience."
        ),
        "modules": [
            {
                "title": "Python, SQL and Git for data science",
                "weeks": "Weeks 1 to 3",
                "overview": "A fast refresher that sets the engineering habits used for the rest of the programme.",
                "concepts": (
                    "Python functions, modules and virtual environments. pandas idioms. SQL joins and "
                    "window functions. Git branches, commits, pull requests and code review. Project "
                    "structure and README conventions."
                ),
                "lab": "Set up a project repository, load a dataset from SQL into pandas, and open a pull request with a reviewed notebook.",
                "quiz": [
                    q("Which Git command records staged changes in the local repository?",
                      [("git commit", True), ("git push", False), ("git clone", False), ("git status", False)]),
                    q("Why use a virtual environment?",
                      [("To isolate a project's dependencies", True), ("To make Python run faster", False), ("To encrypt source code", False)]),
                    tf("A pull request lets a reviewer see changes before they are merged.", True),
                ],
                "practical": {"title": "Project repository and first analysis", "instructions": "Submit a link to a repository with a README, a reproducible environment file, and a merged pull request containing your first notebook."},
            },
            {
                "title": "Statistics and probability for data science",
                "weeks": "Weeks 4 to 6",
                "overview": "The statistical reasoning behind every model: distributions, uncertainty and hypothesis tests.",
                "concepts": (
                    "Descriptive statistics. Probability distributions. Sampling and the central limit "
                    "theorem. Confidence intervals. Hypothesis testing and p-values. Correlation versus "
                    "causation. Bayes' rule in plain terms."
                ),
                "lab": "Test whether a change in a billing process reduced query volumes, and report the result with an effect size and interval.",
                "quiz": [
                    q("A p-value of 0.03 at a 5% significance level means:",
                      [("The result is unlikely under the null hypothesis, so we reject it", True), ("There is a 3% chance the null hypothesis is true", False), ("The effect is large", False)]),
                    q("Which statistics describe spread?",
                      [("Standard deviation", True), ("Interquartile range", True), ("Mean", False)]),
                    tf("Correlation between two variables proves that one causes the other.", False),
                ],
                "practical": {"title": "Billing process A/B analysis", "instructions": "Submit a notebook that frames the hypothesis, checks assumptions, runs the test, and states the business recommendation in plain language."},
            },
            {
                "title": "Data wrangling and feature engineering",
                "weeks": "Weeks 7 to 9",
                "overview": "Turning raw operational records into model-ready features without leaking the future.",
                "concepts": (
                    "Encoding categoricals. Scaling. Date and time features. Aggregating transactions "
                    "to entity level. Handling imbalance. Train, validation and test splits. Data "
                    "leakage. scikit-learn pipelines and ColumnTransformer."
                ),
                "lab": "Build a feature pipeline for supplier invoices that produces entity-level risk features and is safe from leakage.",
                "quiz": [
                    q("Which scikit-learn object applies different preprocessing to different columns?",
                      [("ColumnTransformer", True), ("StandardScaler", False), ("LabelEncoder", False), ("GridSearchCV", False)]),
                    q("Which of these cause data leakage?",
                      [("Scaling using statistics computed on the full dataset before splitting", True), ("Using a feature derived from the target", True), ("Splitting data before fitting the scaler", False)]),
                    tf("One-hot encoding creates one binary column per category value.", True),
                ],
                "practical": {"title": "Invoice feature pipeline", "instructions": "Submit the pipeline code, a feature dictionary describing each feature and its rationale, and tests that show the pipeline runs on unseen data."},
            },
            {
                "title": "Supervised learning with scikit-learn",
                "weeks": "Weeks 10 to 12",
                "overview": "Regression and classification models, how they learn, and when to use which.",
                "concepts": (
                    "Linear and logistic regression. Decision trees, random forests and gradient "
                    "boosting. k-nearest neighbours. Regularisation. Hyperparameters and cross-validated "
                    "search. Probability outputs and thresholds."
                ),
                "lab": "Train three classifiers to flag high-risk invoices and compare them with cross-validation.",
                "quiz": [
                    q("Which model is appropriate for predicting a yes/no outcome?",
                      [("Logistic regression", True), ("Linear regression", False), ("k-means", False)]),
                    q("Which techniques reduce overfitting?",
                      [("Regularisation", True), ("Limiting tree depth", True), ("Training on the test set", False)]),
                    tf("Cross-validation gives a more reliable performance estimate than a single split.", True),
                ],
                "practical": {"title": "Invoice risk classifier", "instructions": "Submit a notebook comparing at least three models with cross-validation, a chosen model with justification, and the saved model artefact."},
            },
            {
                "title": "Model evaluation, validation and interpretability",
                "weeks": "Weeks 13 to 15",
                "overview": "Choosing the right metric for the decision, and explaining a model to an auditor.",
                "concepts": (
                    "Confusion matrix, precision, recall, F1, ROC and PR curves. Cost-sensitive "
                    "thresholds. Calibration. Regression metrics (MAE, RMSE, MAPE). Feature importance, "
                    "permutation importance and SHAP. Fairness checks across groups."
                ),
                "lab": "Evaluate the invoice classifier for an audit team that can only review 200 invoices a month, and explain its top drivers.",
                "quiz": [
                    q("If false negatives are far more costly than false positives, which metric matters most?",
                      [("Recall", True), ("Precision", False), ("Accuracy", False)]),
                    q("Which metrics apply to regression problems?",
                      [("MAE", True), ("RMSE", True), ("F1 score", False)]),
                    tf("A model can have high accuracy and still be useless on a heavily imbalanced dataset.", True),
                ],
                "practical": {"title": "Audit-ready model evaluation report", "instructions": "Submit a PDF report with the chosen threshold and its rationale, a confusion matrix at that threshold, calibration evidence, top drivers with SHAP plots, and a fairness check."},
            },
            {
                "title": "Unsupervised learning and anomaly detection",
                "weeks": "Weeks 16 to 18",
                "overview": "Finding structure and outliers without labels, the core of assurance analytics.",
                "concepts": (
                    "k-means and hierarchical clustering. Choosing k. DBSCAN. PCA for dimensionality "
                    "reduction. Isolation Forest and local outlier factor. Benford's law and rule-based "
                    "checks alongside models."
                ),
                "lab": "Detect anomalous payment patterns in a transactions dataset and rank them for investigation.",
                "quiz": [
                    q("Which algorithm isolates anomalies by random partitioning?",
                      [("Isolation Forest", True), ("k-means", False), ("PCA", False)]),
                    q("Which are valid ways to choose the number of clusters?",
                      [("Elbow method", True), ("Silhouette score", True), ("Always use 3", False)]),
                    tf("PCA reduces the number of features while keeping as much variance as possible.", True),
                ],
                "practical": {"title": "Payment anomaly investigation list", "instructions": "Submit the notebook and a ranked list of the top 50 anomalies with the reason each was flagged, in a format an internal audit team could act on."},
            },
            {
                "title": "Time series and demand forecasting",
                "weeks": "Weeks 19 to 21",
                "overview": "Forecasting demand, load and volumes for planning decisions.",
                "concepts": (
                    "Trend, seasonality and stationarity. Lag features. Train/test splits in time. "
                    "Baselines, exponential smoothing, ARIMA and gradient boosting on lags. Forecast "
                    "error metrics and prediction intervals. Backtesting."
                ),
                "lab": "Forecast weekly water demand per zone 12 weeks ahead and backtest against the last year.",
                "quiz": [
                    q("Why must time series data not be shuffled before splitting?",
                      [("Future observations would leak into training", True), ("It makes training slower", False), ("Shuffling changes the units", False)]),
                    q("Which components does classical decomposition separate?",
                      [("Trend", True), ("Seasonality", True), ("Residual", True), ("Precision", False)]),
                    tf("A naive forecast that repeats last week's value is a useful baseline.", True),
                ],
                "practical": {"title": "Zone demand forecast", "instructions": "Submit the notebook with backtest results against at least one baseline, prediction intervals, and a short note on how the forecast should be used for planning."},
            },
            {
                "title": "Deploying models with Streamlit",
                "weeks": "Weeks 22 to 24",
                "overview": "Shipping a model as an application that stakeholders can use, with version control and a live URL.",
                "concepts": (
                    "Saving and loading models. Streamlit widgets, layout and caching. Input validation. "
                    "Secrets and configuration. Deploying to Streamlit Community Cloud or a container. "
                    "Basic logging and usage tracking."
                ),
                "lab": "Wrap the invoice risk model in a Streamlit app that scores uploaded files and explains each score.",
                "quiz": [
                    q("Which Streamlit decorator avoids reloading a model on every interaction?",
                      [("@st.cache_resource", True), ("@st.form", False), ("@st.sidebar", False)]),
                    q("Where should API keys for a deployed app live?",
                      [("In the platform's secrets store", True), ("In an environment variable", True), ("Hard-coded in the script", False)]),
                    tf("A deployed model should validate user input before scoring it.", True),
                ],
                "practical": {"title": "Model scoring app", "instructions": "Submit the repository link and the live app URL. The app must accept a file upload, return scores with explanations, and reject malformed input gracefully."},
            },
        ],
        "capstone": {
            "title": "Capstone: predictive risk or demand-forecasting web app",
            "brief": (
                "Pick a risk-scoring or demand-forecasting problem grounded in a public sector or "
                "enterprise dataset. Deliver the full lifecycle: problem framing, feature pipeline, "
                "model selection with audit-ready evaluation, and a live Streamlit app under version "
                "control."
            ),
            "instructions": (
                "Submit the repository link, the live app URL, a technical report (max 10 pages) and a "
                "ten-minute recorded demo. Assessment covers problem framing, methodological rigour, "
                "evaluation quality, code quality and the usability of the deployed app."
            ),
        },
    },
    # ------------------------------------------------------------------
    {
        "slug": "full-stack-ai-mlops-engineering",
        "title": "Full-Stack AI & MLOps Engineering",
        "level": "advanced",
        "duration_months": 12,
        "tags": "python,pytorch,fastapi,docker,kubernetes,mlops,mlflow,llm,rag,ci/cd",
        "short_description": (
            "A one-year engineering programme that ends with a production-ready AI microservice, "
            "containerised, orchestrated and delivered through automated CI/CD."
        ),
        "description": (
            "This 48-week programme trains the engineers that AI and data professional-services "
            "tenders describe: people who can productionise models as APIs, run them in containers "
            "on Kubernetes, integrate large language models, and operate the MLOps lifecycle from "
            "experiment tracking to drift monitoring and automated retraining."
        ),
        "requirements": (
            "Solid Python and applied machine learning (the Applied Data Science programme or "
            "equivalent). Command-line comfort. A laptop with 16 GB RAM, or access to cloud credits."
        ),
        "what_you_learn": (
            "Write tested, packaged Python services\n"
            "Build data pipelines and serve models through FastAPI\n"
            "Containerise with Docker and deploy on Kubernetes\n"
            "Train deep learning models with PyTorch for vision and language tasks\n"
            "Integrate LLMs with retrieval-augmented generation\n"
            "Run MLOps: experiment tracking, CI/CD, monitoring, drift and retraining\n"
            "Apply security, governance and responsible AI practice"
        ),
        "target_audience": (
            "Data scientists moving into engineering, software developers moving into AI, and "
            "teams that need to deliver against cloud-native AI professional-services scopes."
        ),
        "modules": [
            {
                "title": "Python engineering and software craft",
                "weeks": "Weeks 1 to 4",
                "overview": "Engineering discipline for code that other people run: structure, tests, packaging and tooling.",
                "concepts": "Project layout, type hints, logging, configuration. pytest, fixtures and coverage. Packaging with pyproject. Linting and formatting. Pre-commit hooks.",
                "lab": "Refactor a notebook into a tested, installable package with a command-line entry point.",
                "quiz": [
                    q("Which tool is the standard test runner in modern Python projects?", [("pytest", True), ("pip", False), ("black", False)]),
                    q("Which practices improve code maintainability?", [("Type hints", True), ("Automated tests", True), ("Copying code between files", False)]),
                    tf("A pre-commit hook can run linters before code is committed.", True),
                ],
                "practical": {"title": "Package a model pipeline", "instructions": "Submit a repository with an installable package, at least 80% test coverage, a CLI entry point and passing lint checks."},
            },
            {
                "title": "Data engineering foundations",
                "weeks": "Weeks 5 to 8",
                "overview": "Reliable pipelines that move data from source systems into analytical stores.",
                "concepts": "Batch versus streaming. Extract, load, transform. Idempotent jobs. Orchestration (Airflow or Prefect). Data warehouses and lakehouse formats (Parquet). Data quality checks. Schema evolution.",
                "lab": "Build an orchestrated pipeline that ingests daily extracts, validates them, and loads partitioned Parquet into a warehouse.",
                "quiz": [
                    q("An idempotent pipeline step is one that:", [("Produces the same result if run more than once", True), ("Runs only once ever", False), ("Never fails", False)]),
                    q("Which are advantages of Parquet over CSV?", [("Columnar storage", True), ("Embedded schema", True), ("Human readability in a text editor", False)]),
                    tf("Data quality checks should run before downstream consumers read new data.", True),
                ],
                "practical": {"title": "Orchestrated ingestion pipeline", "instructions": "Submit the pipeline repository with DAG definitions, quality checks, a rerun demonstration and a short runbook."},
            },
            {
                "title": "Serving models with FastAPI",
                "weeks": "Weeks 9 to 12",
                "overview": "Wrapping a model in a well-designed, documented HTTP API.",
                "concepts": "REST design. FastAPI routing, Pydantic models, validation and OpenAPI docs. Dependency injection. Async basics. Authentication with tokens. Error handling. Load testing.",
                "lab": "Serve a trained model behind a /predict endpoint with input validation, auth and generated docs.",
                "quiz": [
                    q("In FastAPI, request and response schemas are defined with:", [("Pydantic models", True), ("SQL tables", False), ("YAML files", False)]),
                    q("Which HTTP status codes indicate a client error?", [("400", True), ("401", True), ("500", False)]),
                    tf("FastAPI generates interactive API documentation automatically.", True),
                ],
                "practical": {"title": "Model prediction API", "instructions": "Submit the API repository with tests, OpenAPI docs, a load test report and a README describing authentication."},
            },
            {
                "title": "Containers with Docker",
                "weeks": "Weeks 13 to 16",
                "overview": "Packaging services so they run identically everywhere.",
                "concepts": "Images, layers and the Dockerfile. Multi-stage builds. Volumes and networks. docker compose for local stacks. Image size and security scanning. Registries.",
                "lab": "Containerise the FastAPI service and its database with compose, then slim the image with a multi-stage build.",
                "quiz": [
                    q("A multi-stage Dockerfile is used mainly to:", [("Keep build tools out of the final image", True), ("Run several containers at once", False), ("Replace docker compose", False)]),
                    q("Which practices improve container security?", [("Running as a non-root user", True), ("Scanning images for vulnerabilities", True), ("Baking secrets into the image", False)]),
                    tf("docker compose can start an API and its database together with one command.", True),
                ],
                "practical": {"title": "Containerised service stack", "instructions": "Submit the Dockerfile, compose file, an image scan report and evidence that the image runs as a non-root user."},
            },
            {
                "title": "Kubernetes and cloud orchestration",
                "weeks": "Weeks 17 to 20",
                "overview": "Running containers at scale with health checks, scaling and rollouts.",
                "concepts": "Pods, Deployments, Services and Ingress. ConfigMaps and Secrets. Liveness and readiness probes. Horizontal autoscaling. Rolling updates and rollbacks. Managed Kubernetes on a cloud provider. Cost awareness.",
                "lab": "Deploy the containerised API to a cluster with probes, autoscaling and a rolling update.",
                "quiz": [
                    q("Which Kubernetes object maintains a desired number of pod replicas?", [("Deployment", True), ("ConfigMap", False), ("Ingress", False)]),
                    q("Which probes does Kubernetes use to manage pod health?", [("Liveness", True), ("Readiness", True), ("Latency", False)]),
                    tf("A rolling update replaces pods gradually to avoid downtime.", True),
                ],
                "practical": {"title": "Cluster deployment", "instructions": "Submit the manifests or Helm chart, a demonstration of a rolling update and rollback, and a short cost estimate for running the service."},
            },
            {
                "title": "Deep learning with PyTorch",
                "weeks": "Weeks 21 to 24",
                "overview": "Neural networks from tensors up, trained and evaluated properly.",
                "concepts": "Tensors and autograd. Datasets and DataLoaders. Layers, losses and optimisers. Training loops, validation and early stopping. GPUs. Transfer learning. Saving and loading models.",
                "lab": "Train a tabular and an image classifier in PyTorch with a proper validation loop and learning-rate schedule.",
                "quiz": [
                    q("Which PyTorch component computes gradients automatically?", [("autograd", True), ("DataLoader", False), ("torchvision", False)]),
                    q("Which help prevent overfitting in neural networks?", [("Dropout", True), ("Early stopping", True), ("Increasing the learning rate indefinitely", False)]),
                    tf("Transfer learning reuses a model pre-trained on a large dataset.", True),
                ],
                "practical": {"title": "PyTorch training project", "instructions": "Submit training code, experiment notes, validation curves and the saved model, with a README explaining reproducibility."},
            },
            {
                "title": "Computer vision",
                "weeks": "Weeks 25 to 28",
                "overview": "Vision models for inspection, document and monitoring use cases.",
                "concepts": "Convolutional networks. Data augmentation. Image classification, object detection and segmentation. Pre-trained backbones. Evaluation (mAP, IoU). Inference optimisation.",
                "lab": "Fine-tune a detector to find defects or objects in an infrastructure inspection image set.",
                "quiz": [
                    q("Which metric is standard for object detection?", [("Mean average precision (mAP)", True), ("RMSE", False), ("Silhouette score", False)]),
                    q("Which are common data augmentation techniques?", [("Random crop", True), ("Horizontal flip", True), ("Changing the label", False)]),
                    tf("IoU measures the overlap between a predicted and a true bounding box.", True),
                ],
                "practical": {"title": "Inspection detector", "instructions": "Submit the fine-tuning code, evaluation on a held-out set with mAP, sample predictions and an inference latency measurement."},
            },
            {
                "title": "NLP and LLM integration with RAG",
                "weeks": "Weeks 29 to 32",
                "overview": "Language models as components: embeddings, retrieval and grounded generation.",
                "concepts": "Tokenisation and embeddings. Vector stores and similarity search. Retrieval-augmented generation. Prompting and structured outputs. Evaluation of RAG systems. Cost, latency and privacy of hosted versus local models.",
                "lab": "Build a RAG service that answers questions over a corpus of policy documents with cited sources.",
                "quiz": [
                    q("In RAG, retrieved documents are used to:", [("Ground the model's answer in source material", True), ("Train the model's weights", False), ("Replace the prompt entirely", False)]),
                    q("Which improve RAG answer quality?", [("Better chunking of source documents", True), ("Returning citations for verification", True), ("Removing the retrieval step", False)]),
                    tf("Embeddings map text to vectors so similar meanings are close together.", True),
                ],
                "practical": {"title": "Policy question-answering service", "instructions": "Submit the service repository, an evaluation set with measured answer accuracy and citation correctness, and a note on data privacy choices."},
            },
            {
                "title": "MLOps: experiment tracking and model registry",
                "weeks": "Weeks 33 to 36",
                "overview": "Making model development reproducible and auditable.",
                "concepts": "Experiment tracking with MLflow. Parameters, metrics and artefacts. Model registry, stages and lineage. Data and model versioning. Reproducible training runs. Model cards.",
                "lab": "Instrument a training pipeline with MLflow, register the best model and promote it through stages.",
                "quiz": [
                    q("A model registry primarily provides:", [("Versioned models with stage transitions and lineage", True), ("Faster inference", False), ("A web front end for users", False)]),
                    q("Which should be logged for each training run?", [("Hyperparameters", True), ("Evaluation metrics", True), ("The engineer's password", False)]),
                    tf("A model card documents intended use, limitations and evaluation of a model.", True),
                ],
                "practical": {"title": "Tracked and registered model", "instructions": "Submit the MLflow tracking evidence, the registered model with lineage to its data version, and a completed model card."},
            },
            {
                "title": "CI/CD for ML systems",
                "weeks": "Weeks 37 to 40",
                "overview": "Automating tests, builds and deployments for both code and models.",
                "concepts": "GitHub Actions workflows. Testing data and model code. Building and pushing images. Environment promotion. Deployment strategies (blue/green, canary). Secrets management. Rollback.",
                "lab": "Build a pipeline that tests, builds, scans and deploys the model service to a staging cluster on every merge.",
                "quiz": [
                    q("A canary deployment:", [("Routes a small share of traffic to the new version first", True), ("Deploys to all users at once", False), ("Only runs tests", False)]),
                    q("Which belong in a CI pipeline for an ML service?", [("Unit tests", True), ("Container image build", True), ("Manual copy of files to the server", False)]),
                    tf("Secrets should be stored in the CI platform's secret store, not in the repository.", True),
                ],
                "practical": {"title": "Automated delivery pipeline", "instructions": "Submit the workflow files, a link to a successful pipeline run, and a demonstration of a rollback."},
            },
            {
                "title": "Monitoring, drift and automated retraining",
                "weeks": "Weeks 41 to 44",
                "overview": "Keeping a deployed model healthy after launch.",
                "concepts": "Service metrics and logs. Prediction logging. Data drift and concept drift detection. Performance monitoring with delayed labels. Alerting. Scheduled and triggered retraining loops. Human review gates.",
                "lab": "Add drift detection and alerting to the deployed service and wire a retraining job that is triggered when drift exceeds a threshold.",
                "quiz": [
                    q("Data drift means:", [("The distribution of inputs has changed since training", True), ("The model file was corrupted", False), ("The API is slow", False)]),
                    q("Which should trigger a review before automatic redeployment?", [("A drop in validation performance", True), ("A large change in input distribution", True), ("A successful health check", False)]),
                    tf("Labels for monitoring often arrive later than predictions.", True),
                ],
                "practical": {"title": "Monitored service with retraining loop", "instructions": "Submit the monitoring configuration, a drift report from a simulated shift, and evidence of a retraining run with a review gate."},
            },
            {
                "title": "Security, governance and responsible AI",
                "weeks": "Weeks 45 to 48",
                "overview": "Meeting the compliance expectations of public sector and enterprise clients.",
                "concepts": "Threat modelling for ML services. Input validation and prompt injection. Access control and audit logs. POPIA and data minimisation. Bias assessment. Explainability requirements. Documentation for procurement and audit.",
                "lab": "Run a security and fairness review of the capstone service and produce a compliance pack.",
                "quiz": [
                    q("Prompt injection is:", [("Untrusted input that manipulates a language model's behaviour", True), ("A way to speed up inference", False), ("A database migration", False)]),
                    q("Which support POPIA compliance in an AI service?", [("Data minimisation", True), ("Audit logging of access", True), ("Storing all raw personal data indefinitely", False)]),
                    tf("An audit log should record who accessed which records and when.", True),
                ],
                "practical": {"title": "Compliance pack", "instructions": "Submit a threat model, an access-control and audit-logging description, a bias assessment, and a data protection impact summary for your service."},
            },
        ],
        "capstone": {
            "title": "Capstone: production-ready AI microservice with automated CI/CD",
            "brief": (
                "Deliver an AI service end to end: a trained model (tabular, vision or LLM-based), "
                "served through FastAPI, containerised, deployed to Kubernetes through an automated "
                "pipeline, tracked in a registry, and monitored for drift, with a compliance pack."
            ),
            "instructions": (
                "Submit the repository link, the live endpoint, pipeline run links, the model card, the "
                "monitoring dashboard and the compliance pack, plus a fifteen-minute recorded "
                "architecture walkthrough. Assessment follows a production readiness rubric covering "
                "engineering quality, operability, security and documentation."
            ),
        },
    },
]
