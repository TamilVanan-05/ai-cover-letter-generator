# CoverCraft - AI Cover Letter Generator SaaS Platform

CoverCraft is a premium, production-ready AI-powered cover letter generator SaaS platform. It matches candidate experience with target job descriptions in real-time, scores drafts against ATS standard keywords, suggests structural adjustments, and renders letter previews in **15+ distinct templates** ready for PDF/Word exports or public sharing.

---

## 🚀 Tech Stack

### Frontend
- **Frameworks**: Vanilla HTML5, CSS3, JavaScript ES6
- **Styling**: Bootstrap 5 + Tailwind CSS (Utility classes for responsive layouts, shadows, and glassmorphic overlays)
- **Icons & Animations**: Font Awesome 6 + AOS (Animate On Scroll)
- **Data Visualizations**: Chart.js (Renders compliance analytics and stats timelines)
- **Client Exporter**: html2pdf.js (Crisp vector PDF extraction directly from CSS templates)

### Backend
- **Core Engine**: Python Flask + RESTful JSON APIs
- **Database ORM**: SQLAlchemy (Configured for SQLite locally & MySQL compatible in production)
- **Token Security**: Flask-JWT-Extended (JSON Web Token state sessions)
- **AI Core**: Google Gemini API SDK (`google-generativeai`) with a sophisticated rule-based fallback NLP generator for offline/zero-config operation
- **DOCX Parser**: python-docx (Compiles structured Word documents with 1-inch margins and customized layouts)

---

## 📁 Repository Folder Structure

```text
├── app.py                   # Flask main application entrypoint
├── config.py                # Configuration and environment management
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build blueprint
├── docker-compose.yml       # Local multi-container orchestration (Flask + MySQL)
├── .env                     # Configuration variables (gitignored, auto-created)
│
├── backend/
│   ├── __init__.py          # Blueprint hook
│   ├── auth.py              # Register, Login, JWT session controllers
│   ├── database.py          # SQLAlchemy schemas (User, Profile, CoverLetter, Logs, Feedback)
│   ├── ai_engine.py         # Gemini API connectors & local fallback generator
│   ├── ats_engine.py        # ATS keyword scoring, readability check & suggestions analyzer
│   ├── export_engine.py     # python-docx exporter & mock SMTP email dispatcher
│   └── admin.py             # Administrator analytics, user control & activities logs
│
├── templates/               # Server-side HTML views
│   ├── base.html            # Shared skeleton layout
│   ├── landing.html         # SaaS marketing homepage
│   ├── login.html           # Authentication views (Login/Register/Forgot slides)
│   ├── dashboard.html       # Dynamic SaaS user dashboard (Wizard + Editor + Stats)
│   ├── share.html           # Standalone public cover letter viewer
│   └── admin.html           # Administrator panel
│
└── static/                  # Client-side static resources
    ├── css/
    │   ├── style.css        # Main glassmorphic styling system & scrollbars
    │   └── templates.css    # Layout rules for all 15 cover letter presets
    └── js/
        ├── app.js           # Auth handlers, headers injections & toast routines
        ├── dashboard.js     # Wizard control, profile syncing, folder views & sandboxes
        ├── ats.js           # Score circles progress & matched tags renderer
        ├── admin.js         # Users managers, feedback lists & Chart.js graph engines
        └── export.js        # PDF builders, DOCX triggers & share copier helpers
```

---

## 🛠️ Installation & Setup

Ensure Python 3.10+ is installed on your local computer.

### Option A: Local Execution (Recommended)

1. **Clone & Open Workspace**:
   Navigate into the project root directory.

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environments**:
   Copy `.env.example` to `.env` or use the pre-generated `.env` file in the root. If you have a Gemini API key, add it to enable live generative AI calls:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *Note: If no API key is specified, the application automatically uses the local NLP fallback engine, ensuring the app works perfectly right out of the box!*

4. **Launch Server**:
   ```bash
   python app.py
   ```

5. **Open Browser**:
   Navigate to `http://localhost:5000` to access the website.

### Option B: Docker Container Deployment

1. **Build and Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   This spins up the Flask backend on port `5000` alongside a persistent MySQL server on port `3306`.

2. **Access Application**:
   Navigate to `http://localhost:5000`.

---

## 🔑 Test Accounts (Developer Sandbox)

The database automatically seeds a test administrator account upon startup. You can also sign up for new accounts on the login screen.

### 1. Developer Administrator Account
- **Email**: `admin@aicoveradmin.com`
- **Password**: `admin123`
- *Access*: Grants entrance to the **Admin Control** analytics dashboards, user tables, audit trails, and feedback feedback tickets.

### 2. Standard User Account
Simply navigate to `http://localhost:5000/login`, select **Register**, and create any account to start generating letters immediately. 

---

## 🔒 Security Practices Built-in
1. **JWT Auth Interceptors**: Token-based authentication checks all routes and expires sessions safely.
2. **Password Hashing**: Client credentials are encrypted using PBKDF2 cryptography hashing via `werkzeug.security`.
3. **Role Validation Decorators**: Checks roles on the server, blocking standard users from querying admin endpoints.
4. **No Placeholders**: Strict input controls prevent empty database logs or template rendering errors.
5. **Credit Limits**: Free tier limits generations to 5. Sandbox refilling endpoints allow developers to clear/reload values with one-click.

---

## ☁️ Production Deployment Guide

### Deploying to Render / Railway
1. Push this workspace code to your GitHub repository.
2. Connect your GitHub repository to Render/Railway.
3. Configure settings:
   - **Environment**: `Python` or use the included `Dockerfile`.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` or `python app.py`
4. Set Environment Variables:
   - `SECRET_KEY`: Random string
   - `JWT_SECRET_KEY`: Random string
   - `GEMINI_API_KEY`: Google Generative AI credentials
   - `DATABASE_URL`: Staging database connector (e.g. `mysql://user:pass@host/db`)
