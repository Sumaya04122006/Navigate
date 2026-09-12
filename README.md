# 🚀 NAVIGATE — From Opportunity to Action

https://navigatee.vercel.app/

### AI-Powered Opportunity Eligibility & Action Planning System

NAVIGATE helps students answer three important questions:

- Am I eligible?
- Why or why not?
- What should I do next?

---

# 💡 What is NAVIGATE?

Students find internships, scholarships, fellowships, and other opportunities online, but eligibility requirements are often buried inside long and complex opportunity pages.

NAVIGATE converts an opportunity URL and a student's profile into a structured eligibility analysis and personalized action plan.

## Input

- Opportunity URL
- Degree
- Academic Year
- CGPA
- Skills

## Output

- Opportunity information
- Official requirements
- Eligibility result
- Requirement gaps
- Missing information
- Personalized action plan
- Recommended preparation
- Conditional requirements
- Source evidence

---

# 🎯 The Problem

Finding an opportunity is easy.

**Understanding whether you actually qualify is not.**

Students often have to manually:

- Read long opportunity descriptions
- Find eligibility requirements
- Compare their CGPA
- Check their academic year
- Compare required skills
- Identify missing requirements
- Decide what to improve before applying

Even after doing all this, a student may still not know:

> "If I'm not eligible today, what should I do to become ready?"

---

# 💡 The Key Idea

NAVIGATE is not simply an AI chatbot.

Instead of asking an LLM to make a simple YES/NO decision, NAVIGATE separates the process into different stages:

```text
AI → Extracts requirements
        ↓
Python → Evaluates eligibility
        ↓
AI → Generates an action plan
```

### AI interprets. Python decides. AI plans.

This separation makes the eligibility evaluation more structured, consistent, and explainable.

---

# ⚙️ How NAVIGATE Works

```text
┌─────────────────────────┐
│    OPPORTUNITY URL      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│     WEB RETRIEVAL       │
│ Requests + BeautifulSoup│
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   AI REQUIREMENT        │
│      EXTRACTION         │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ STRUCTURED REQUIREMENTS │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ PYTHON DETERMINISTIC    │
│   ELIGIBILITY ENGINE    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│      GAP ANALYSIS       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│    AI ACTION PLANNER    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   RESULTS + EVIDENCE    │
└─────────────────────────┘
```

---

# 🧠 Core Features

## 1. Opportunity Retrieval

NAVIGATE retrieves information from the opportunity webpage provided by the student.

## 2. AI Requirement Extraction

The retrieved content is processed by AI to identify explicitly stated requirements and convert them into structured data.

## 3. Deterministic Eligibility Engine

The extracted requirements are evaluated using Python-based rules.

NAVIGATE can classify requirements as:

- ✅ PASS
- ❌ FAIL
- ⚠️ NEEDS INPUT
- 🔶 CONDITIONAL

The overall eligibility result can be:

- ELIGIBLE
- NOT ELIGIBLE
- NEEDS REVIEW

## 4. Gap Analysis

NAVIGATE identifies requirements that:

- The student does not currently meet
- Require additional information
- Require further verification
- May prevent eligibility

## 5. Personalized Action Plan

Instead of stopping at **"Not Eligible"**, NAVIGATE generates practical next steps based on the identified gaps.

## 6. Source Evidence

The opportunity source is retained so that the analysis can be connected back to the information used by the system.

---

# 🧪 Example

## Student Profile

| Field | Example |
|---------|---------|
| Degree | Bachelor of Information Technology |
| Academic Year | 2 |
| CGPA | 3.98 |
| Skills | Python, SQL, AI, HTML, CSS, JavaScript, Git, GitHub |

## Example Analysis

| Requirement | Result |
|------------|---------|
| CGPA Requirement | ✅ PASS |
| Degree Requirement | ✅ PASS / ⚠️ REVIEW |
| Academic Year | ❌ FAIL |
| Other Requirements | ⚠️ NEEDS INPUT |

NAVIGATE does not simply return:

```text
❌ NOT ELIGIBLE
```

It explains **why**, identifies the gap, and generates an action plan.

---

# 🏗️ System Architecture

```text
USER
  │
  ▼
┌─────────────┐
│   VERCEL    │
│  FRONTEND   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│   RENDER    │
│   FASTAPI   │
└──────┬──────┘
       │
 ┌─────┴─────┐
 ▼           ▼
WEB       OPENROUTER
RETRIEVAL
 │
 └─────┬─────┘
       ▼
PYTHON ELIGIBILITY
      ENGINE
       │
       ▼
   GAP ANALYSIS
       │
       ▼
 AI ACTION PLAN
       │
       ▼
  FINAL RESULTS
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---------|---------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Web Retrieval | Requests |
| Web Parsing | BeautifulSoup |
| AI | OpenRouter |
| Eligibility Engine | Python deterministic rules |
| Data Validation | Pydantic |
| Environment Variables | python-dotenv |
| Version Control | Git + GitHub |
| Frontend Deployment | Vercel |
| Backend Deployment | Render |

---

# 📁 Project Structure

```text
NAVIGATE/
│
├── Backend/
│   ├── main.py
│   └── requirements.txt
│
├── Frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .gitignore
└── README.md
```

---

# ▶️ Run Locally

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/NAVIGATE.git
cd NAVIGATE
```

> Replace `YOUR-USERNAME` with your actual GitHub username.

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

---

## 3. Activate the Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r Backend/requirements.txt
```

---

## 5. Configure the API Key

Create:

```text
Backend/.env
```

Add:

```env
OPENROUTER_API_KEY=your_api_key_here
```

⚠️ Never commit your API key to GitHub.

---

## 6. Start the Backend

```bash
python -m uvicorn Backend.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🌐 Deployment

NAVIGATE is deployed using separate frontend and backend services.

| Component | Platform |
|------------|------------|
| Frontend | Vercel |
| Backend | Render |
| AI API | OpenRouter |
| Source Code | GitHub |

## Deployment Flow

```text
GitHub
   │
   ├──────────────► Vercel
   │                 │
   │                 ▼
   │             Frontend
   │                 │
   │               HTTPS
   │                 │
   └──────────────► Render
                     │
                     ▼
                  FastAPI
                     │
                     ▼
                 OpenRouter
```

---

# 🔐 Security

Sensitive credentials are stored using environment variables rather than being hard-coded into the application.

The repository excludes:

```text
.env
.venv/
__pycache__/
```

API keys should never be committed to GitHub.

---

# 🎯 Current MVP

The current MVP focuses on proving the complete end-to-end workflow:

```text
URL
 ↓
Retrieve
 ↓
Extract Requirements
 ↓
Evaluate Eligibility
 ↓
Identify Gaps
 ↓
Generate Action Plan
 ↓
Show Evidence
```

The MVP intentionally focuses on the core problem and working pipeline instead of adding unnecessary features.

---

# ⚠️ Limitations

NAVIGATE depends on the accessibility and structure of the source webpage.

Potential limitations include:

- Websites that block automated requests
- JavaScript-heavy webpages
- Login-protected opportunities
- Incomplete opportunity information
- Ambiguous requirements
- Requirements that require external verification

When information cannot be confidently determined, NAVIGATE can classify it as:

- ⚠️ NEEDS INPUT
- 🔶 CONDITIONAL
- 🟡 NEEDS REVIEW

rather than assuming an answer.

---

# 🔮 Future Development

Potential future improvements include:

- Persistent student profiles
- More opportunity sources
- Improved source verification
- Opportunity tracking
- Deadline reminders
- Resume/CV integration
- Skill-gap recommendations
- Application readiness monitoring
- Improved dynamic webpage handling

---

# 👩‍💻 Developer

**Sumaya Fathima**  
Bachelor of Information Technology — AI  
Liwa University, UAE

---

# ⭐ Project Vision

> "Students don't just need to find opportunities. They need to understand where they stand and what to do next."

## NAVIGATE

### From Opportunity to Action
