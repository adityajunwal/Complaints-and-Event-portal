# 🏘️ Smart Community Hub
> **#1 Event Organizer & Complaint Management System**

A full-stack web application that allows residents to organize community events and raise complaints — with an admin panel for complaint resolution.

---

## ✨ Features

### 👤 Users
- Register & Login (JWT-based auth)
- Post community events with date, time & optional banner image
- Browse all community events
- File complaints with description & optional photo evidence
- View their own complaints and resolution status

### 🛡️ Admin
- Auto-created on startup from `.env` credentials
- View **all** events and complaints across the community
- Update complaint status: `Pending → In Review → Resolved`
- Provide a **resolve reason** when resolving a complaint

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python) |
| **Database** | SQLite (via SQLAlchemy) |
| **Auth** | JWT (python-jose) + bcrypt |
| **Image Upload** | Cloudinary |
| **Frontend** | HTML + CSS + Vanilla JS |

---

## 📁 Project Structure

```
Akshu-Major/
│
├── main.py                # All API routes
├── database.py            # SQLAlchemy models (User, Event, Complaint)
├── auth.py                # JWT auth helpers
├── cloudinary_helper.py   # Cloudinary image upload
├── migrate.py             # Safe schema migration runner
│
├── .env                   # Secrets (never commit this)
├── .gitignore
├── requirements.txt
│
└── static/
    ├── index.html         # Login / Register
    ├── dashboard.html     # Home with stats
    ├── events.html        # Post & view events
    ├── complaints.html    # File & track complaints
    ├── style.css          # Shared dark theme stylesheet
    └── app.js             # Shared JS utilities
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/adityajunwal/Complaints-and-Event-portal.git
cd Complaints-and-Event-portal
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
JWT_SECRET=any_long_random_string
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=yourpassword
```

> Get free Cloudinary credentials at [cloudinary.com](https://cloudinary.com)

### 5. Run the app
```bash
python main.py
```

Open **http://localhost:7979** in your browser.

> The admin account is **auto-created** on startup using `ADMIN_EMAIL` and `ADMIN_PASSWORD` from `.env`. No manual registration needed.

---

## 🗄️ Database Migrations

When new columns are added to the schema, run:

```bash
python migrate.py
```

This safely adds missing columns without touching existing data.

---

## 🔌 API Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register new user |
| `POST` | `/auth/login` | ❌ | Login, returns JWT |
| `GET` | `/events` | ❌ | List all events |
| `POST` | `/events` | ✅ | Create event (+ optional image) |
| `GET` | `/complaints` | ✅ | List complaints (own / all for admin) |
| `POST` | `/complaints` | ✅ | Submit complaint (+ optional photo) |
| `PATCH` | `/complaints/{id}/status` | ✅ Admin only | Update status + resolve reason |

Interactive API docs available at **http://localhost:7979/docs**

---

## 📸 Image Uploads

Images are uploaded directly to **Cloudinary**. Only the returned URL is stored in the database. Supported on:
- Event banner images
- Complaint photo evidence

---

## 🔒 Security Notes

- **Never commit `.env`** — it's in `.gitignore`
- JWT tokens expire after **24 hours**
- Admin privileges are enforced server-side on every request
- Passwords are hashed with **bcrypt**
