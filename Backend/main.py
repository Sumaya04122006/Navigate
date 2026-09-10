import os
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing from .env")


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="NAVIGATE API",
    description="AI Opportunity Eligibility and Action Planning System",
    version="0.3.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class OpportunityRequest(BaseModel):
    url: str
    degree: str
    year: str
    cgpa: str
    skills: str


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "NAVIGATE backend is running."
    }


@app.get("/test")
def test():
    return {
        "status": "success",
        "message": "NAVIGATE API is working."
    }


# ============================================================
# WEBPAGE RETRIEVAL
# ============================================================

def get_webpage_text(url: str):

    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/139.0 Safari/537.36"
            )
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "noscript"
    ]):
        element.decompose()

    return soup.get_text(
        separator=" ",
        strip=True
    )


# ============================================================
# OPENROUTER
# ============================================================

def call_ai(prompt: str):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(
            f"OpenRouter API error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise Exception(
            f"Unexpected OpenRouter response: {data}"
        )


# ============================================================
# JSON CLEANING
# ============================================================

def clean_json(text: str):

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return json.loads(text)


# ============================================================
# REQUIREMENT EXTRACTION
# ============================================================

def analyze_with_ai(
    webpage_text: str,
    degree: str,
    year: str,
    cgpa: str,
    skills: str
):
    webpage_text = webpage_text[:30000]

    prompt = f"""
You are the combined AI analysis agent for NAVIGATE.

NAVIGATE analyzes real opportunities such as internships,
scholarships, competitions, jobs and programs.

You must perform TWO tasks in this single response:

TASK 1 — REQUIREMENT EXTRACTION

Extract ONLY requirements explicitly supported by the webpage.

Do not invent requirements.

TASK 2 — ACTION PLAN

Using the extracted requirements and the supplied student profile,
produce a practical action plan.

The action plan must NOT invent requirements or student facts.
It must clearly distinguish:
1. Current blockers
2. Missing information
3. Conditional requirements
4. Preparation actions

Do not invent deadlines or application requirements.
Use existing student skills when suggesting preparation.
Keep the plan concise and practical.

IMPORTANT:
The deterministic eligibility engine will independently calculate
the official eligibility result after this response. Do not override
that result and do not claim eligibility as a fact.

Return ONLY valid JSON.

Required structure:

{{
  "requirements": {{
    "title": "",
    "organization": "",
    "type": "",
    "deadline": "",
    "required_degree": [],
    "required_year": [],
    "minimum_cgpa": "",
    "required_skills": [],
    "location": "",
    "other_requirements": []
  }},
  "action_plan": {{
    "goal": "",
    "current_position": "",
    "blockers": [],
    "missing_information": [],
    "action_plan": [
      {{
        "step": 1,
        "action": "",
        "why": "",
        "priority": "HIGH"
      }}
    ],
    "skills_to_strengthen": [],
    "application_preparation": [],
    "conditional_actions": [],
    "readiness_checklist": [],
    "short_term_focus": ""
  }}
}}

REQUIREMENT EXTRACTION RULES:

1. Do not invent degree requirements.
2. Do not invent skill requirements.
3. If a requirement is not mentioned, return an empty array/string.
4. Preserve academic year requirements accurately.
5. Preserve requirements about completed years of study.
6. Preserve age, nationality, university, residency,
   medical and approval requirements when explicitly stated.
7. Preserve conditional requirements.
8. Do not convert preferences into mandatory requirements.
9. Return concise JSON only.

ACTION PLAN RULES:

1. Never override the deterministic eligibility result.
2. Never invent requirements.
3. Never invent student facts.
4. Never claim a requirement is completed unless the input proves it.
5. Never claim a conditional requirement is already failed.
6. Clearly distinguish:
   - Current blockers
   - Missing information
   - Conditional requirements
   - Preparation actions
7. If academic year is a blocker, state it clearly.
8. Do not pretend learning a skill fixes an academic-year requirement.
9. Do not invent deadlines.
10. Do not invent application requirements.
11. Use existing student skills when suggesting preparation.
12. Keep the plan concise and practical.

STUDENT PROFILE:

Degree: {degree}
Year: {year}
CGPA: {cgpa}
Skills: {skills}

WEBPAGE:

{webpage_text}
"""

    result = clean_json(call_ai(prompt))

    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object.")

    requirements = result.get("requirements")
    action_plan = result.get("action_plan")

    if not isinstance(requirements, dict):
        raise ValueError("AI response is missing valid requirements.")

    if not isinstance(action_plan, dict):
        raise ValueError("AI response is missing valid action_plan.")

    return requirements, action_plan


# ============================================================
# HELPER: EXTRACT CGPA
# ============================================================

def extract_min_cgpa(cgpa_text):

    if not cgpa_text:
        return None

    matches = re.findall(
        r"\d+(?:\.\d+)?",
        cgpa_text
    )

    if not matches:
        return None

    return float(matches[0])


# ============================================================
# HELPER: NORMALIZE YEAR
# ============================================================

def normalize_year(year):

    if not year:
        return None

    text = str(year).strip().lower()

    match = re.search(
        r"\b([1-6])(?:st|nd|rd|th)?\b",
        text
    )

    if match:
        return int(match.group(1))

    written_years = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6
    }

    for word, number in written_years.items():
        if word in text:
            return number

    return None


# ============================================================
# HELPER: EXTRACT REQUIRED YEARS
# ============================================================

def extract_required_years(required_year_list):

    if not required_year_list:
        return []

    text = " ".join(
        str(item)
        for item in required_year_list
    ).lower()

    years = []

    numeric_matches = re.findall(
        r"\b([1-6])(?:st|nd|rd|th)?\b",
        text
    )

    for value in numeric_matches:

        number = int(value)

        if number not in years:
            years.append(number)

    written_years = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6
    }

    for word, number in written_years.items():

        if word in text and number not in years:
            years.append(number)

    return years


# ============================================================
# DETERMINISTIC ELIGIBILITY ENGINE
# ============================================================

def analyze_eligibility(
    requirements,
    degree,
    year,
    cgpa,
    skills
):

    checks = []
    critical_gaps = []
    needs_input = []
    conditional_requirements = []

    student_year = normalize_year(year)

    # ========================================================
    # ACADEMIC YEAR
    # ========================================================

    required_years = extract_required_years(
        requirements.get("required_year", [])
    )

    if required_years:

        if student_year is None:

            checks.append({
                "requirement": "Academic year",
                "status": "NEEDS INPUT",
                "reason": (
                    "Student academic year could not be determined."
                )
            })

            needs_input.append(
                "Student academic year"
            )

        elif student_year in required_years:

            checks.append({
                "requirement": "Academic Year",
                "status": "PASS",
                "reason": (
                    f"Student is Year {student_year}, "
                    "which matches the stated requirement."
                )
            })

        else:

            checks.append({
                "requirement": "Academic Year",
                "status": "FAIL",
                "reason": (
                    f"Student is Year {student_year}; "
                    f"opportunity requires Year "
                    f"{', '.join(map(str, required_years))}."
                )
            })

            critical_gaps.append(
                f"Academic year requirement not met: "
                f"student is Year {student_year}, "
                f"required Year "
                f"{', '.join(map(str, required_years))}"
            )

    # ========================================================
    # COMPLETED TWO YEARS / STUDY DURATION
    # ========================================================

    for requirement in requirements.get(
        "other_requirements",
        []
    ):

        req_lower = requirement.lower()

        if (
            "completed two years" in req_lower
            or "completed 2 years" in req_lower
            or "two years' full-time study" in req_lower
            or "two years of full-time study" in req_lower
            or "2 years' full-time study" in req_lower
            or "2 years of full-time study" in req_lower
        ):

            if student_year is None:

                checks.append({
                    "requirement": requirement,
                    "status": "NEEDS INPUT",
                    "reason": (
                        "Student academic standing is required "
                        "to determine whether this requirement "
                        "is satisfied."
                    )
                })

                needs_input.append(
                    "Academic study duration"
                )

            elif student_year >= 3:

                checks.append({
                    "requirement": requirement,
                    "status": "PASS",
                    "reason": (
                        f"Student is Year {student_year}, "
                        "so the two-year study threshold "
                        "has been reached."
                    )
                })

            else:

                checks.append({
                    "requirement": requirement,
                    "status": "FAIL",
                    "reason": (
                        f"Student is Year {student_year}; "
                        "the opportunity requires completion "
                        "of two years of full-time study."
                    )
                })

                critical_gaps.append(
                    "Required two years of full-time study "
                    "have not yet been completed."
                )

    # ========================================================
    # CGPA
    # ========================================================

    minimum_cgpa = extract_min_cgpa(
        requirements.get("minimum_cgpa", "")
    )

    try:
        student_cgpa = float(cgpa)
    except (ValueError, TypeError):
        student_cgpa = None

    if minimum_cgpa is not None:

        if student_cgpa is None:

            checks.append({
                "requirement": "Minimum CGPA",
                "status": "NEEDS INPUT",
                "reason": (
                    "Student CGPA is missing or invalid."
                )
            })

            needs_input.append(
                "Valid student CGPA"
            )

        elif student_cgpa >= minimum_cgpa:

            checks.append({
                "requirement": f"Minimum CGPA: {minimum_cgpa}",
                "status": "PASS",
                "reason": (
                    f"Student CGPA is {student_cgpa}, "
                    f"which meets the minimum of "
                    f"{minimum_cgpa}."
                )
            })

        else:

            checks.append({
                "requirement": f"Minimum CGPA: {minimum_cgpa}",
                "status": "FAIL",
                "reason": (
                    f"Student CGPA is {student_cgpa}, "
                    f"which is below the minimum of "
                    f"{minimum_cgpa}."
                )
            })

            critical_gaps.append(
                f"CGPA below required minimum of "
                f"{minimum_cgpa}"
            )

    # ========================================================
    # DEGREE
    # ========================================================

    required_degrees = requirements.get(
        "required_degree",
        []
    )

    if required_degrees:

        degree_text = degree.lower().strip()

        matched = any(
            req.lower().strip() in degree_text
            or degree_text in req.lower().strip()
            for req in required_degrees
        )

        if matched:

            checks.append({
                "requirement": "Degree requirement",
                "status": "PASS",
                "reason": (
                    "Student degree matches the stated "
                    "degree requirement."
                )
            })

        else:

            checks.append({
                "requirement": "Degree requirement",
                "status": "FAIL",
                "reason": (
                    "Student degree does not match the "
                    "stated degree requirement."
                )
            })

            critical_gaps.append(
                "Degree does not meet the stated requirement."
            )

    # ========================================================
    # SKILLS
    # ========================================================

    required_skills = requirements.get(
        "required_skills",
        []
    )

    student_skills = [
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    ]

    if required_skills:

        missing_skills = []

        for required_skill in required_skills:

            required_skill_lower = (
                required_skill.lower().strip()
            )

            matched = any(
                required_skill_lower in student_skill
                or student_skill in required_skill_lower
                for student_skill in student_skills
            )

            if not matched:
                missing_skills.append(
                    required_skill
                )

        if not missing_skills:

            checks.append({
                "requirement": "Required skills",
                "status": "PASS",
                "reason": (
                    "Student has the explicitly required skills."
                )
            })

        else:

            checks.append({
                "requirement": "Required skills",
                "status": "FAIL",
                "reason": (
                    "Missing skills: "
                    + ", ".join(missing_skills)
                )
            })

            critical_gaps.extend(
                [
                    f"Missing required skill: {skill}"
                    for skill in missing_skills
                ]
            )

    # ========================================================
    # OTHER REQUIREMENTS
    # ========================================================

    for requirement in requirements.get(
        "other_requirements",
        []
    ):

        req_lower = requirement.lower().strip()

        # Already handled above
        if (
            "completed two years" in req_lower
            or "completed 2 years" in req_lower
            or "two years' full-time study" in req_lower
            or "two years of full-time study" in req_lower
            or "2 years' full-time study" in req_lower
            or "2 years of full-time study" in req_lower
        ):
            continue

        # ----------------------------------------------------
        # AGE
        # ----------------------------------------------------

        if (
            "over 18" in req_lower
            or "18 years of age" in req_lower
            or "18 years" in req_lower
        ):

            checks.append({
                "requirement": requirement,
                "status": "NEEDS INPUT",
                "reason": (
                    "Student age was not provided, "
                    "so this requirement cannot be confirmed."
                )
            })

            needs_input.append(
                "Student age"
            )

        # ----------------------------------------------------
        # UNIVERSITY
        # ----------------------------------------------------

        elif "university" in req_lower:

            checks.append({
                "requirement": requirement,
                "status": "NEEDS INPUT",
                "reason": (
                    "Student university was not provided, "
                    "so university eligibility cannot be confirmed."
                )
            })

            needs_input.append(
                "Student university"
            )

        # ----------------------------------------------------
        # RESIDENCY
        # ----------------------------------------------------

        elif (
            "reside in" in req_lower
            or "residency" in req_lower
            or "able to reside" in req_lower
            or "reside" in req_lower
        ):

            checks.append({
                "requirement": requirement,
                "status": "NEEDS INPUT",
                "reason": (
                    "Student's ability to satisfy the "
                    "residency requirement was not provided."
                )
            })

            needs_input.append(
                "Residency availability"
            )

        # ----------------------------------------------------
        # MEDICAL
        # ----------------------------------------------------

        elif "medical" in req_lower:

            checks.append({
                "requirement": requirement,
                "status": "CONDITIONAL",
                "reason": (
                    "This requirement applies when the "
                    "relevant placement conditions require "
                    "medical fitness."
                )
            })

            conditional_requirements.append(
                requirement
            )

        # ----------------------------------------------------
        # GOVERNMENT / APPROVAL
        # ----------------------------------------------------

        elif (
            "government" in req_lower
            or "approval" in req_lower
            or "authority" in req_lower
        ):

            checks.append({
                "requirement": requirement,
                "status": "CONDITIONAL",
                "reason": (
                    "This requirement is handled during "
                    "the application or placement process."
                )
            })

            conditional_requirements.append(
                requirement
            )

        # ----------------------------------------------------
        # NATIONALITY
        # ----------------------------------------------------

        elif (
            "national" in req_lower
            or "nationality" in req_lower
        ):

            if (
                "uae nationals or non-uae nationals"
                in req_lower
                or "uae or non-uae nationals"
                in req_lower
                or "both uae and non-uae nationals"
                in req_lower
            ):

                checks.append({
                    "requirement": requirement,
                    "status": "PASS",
                    "reason": (
                        "The opportunity explicitly allows "
                        "both UAE Nationals and Non-UAE Nationals."
                    )
                })

            else:

                checks.append({
                    "requirement": requirement,
                    "status": "NEEDS INPUT",
                    "reason": (
                        "Student nationality was not provided, "
                        "so this requirement cannot be confirmed."
                    )
                })

                needs_input.append(
                    "Student nationality"
                )

        # ----------------------------------------------------
        # OTHER UNSUPPORTED REQUIREMENTS
        # ----------------------------------------------------

        else:

            checks.append({
                "requirement": requirement,
                "status": "NEEDS INPUT",
                "reason": (
                    "This requirement was identified from "
                    "the opportunity, but NAVIGATE does not "
                    "currently have enough student information "
                    "to verify it automatically."
                )
            })

            needs_input.append(
                requirement
            )

    # ========================================================
    # OVERALL STATUS
    # ========================================================

    if critical_gaps:

        overall_status = "NOT ELIGIBLE"

    elif needs_input:

        overall_status = "NEEDS REVIEW"

    else:

        overall_status = "ELIGIBLE"

    # ========================================================
    # MATCH SCORE
    # ========================================================

    assessable_checks = [
        check
        for check in checks
        if check["status"] in ["PASS", "FAIL"]
    ]

    if assessable_checks:

        passed = sum(
            1
            for check in assessable_checks
            if check["status"] == "PASS"
        )

        match_score = round(
            (passed / len(assessable_checks)) * 100
        )

    else:

        match_score = 0

    # ========================================================
    # SUMMARY
    # ========================================================

    if overall_status == "ELIGIBLE":

        summary = (
            "The student currently meets all requirements "
            "that NAVIGATE can verify from the supplied profile."
        )

    elif overall_status == "NEEDS REVIEW":

        summary = (
            "No confirmed mandatory failure was found, "
            "but additional student information is required "
            "before eligibility can be confirmed."
        )

    else:

        summary = (
            "The student currently does not meet one or "
            "more mandatory requirements for this opportunity."
        )

    return {
        "overall_status": overall_status,
        "summary": summary,
        "match_score": match_score,
        "checks": checks,
        "critical_gaps": list(
            dict.fromkeys(critical_gaps)
        ),
        "needs_input": list(
            dict.fromkeys(needs_input)
        ),
        "conditional_requirements": list(
            dict.fromkeys(conditional_requirements)
        )
    }


# ============================================================
# ACTION PLAN AGENT
# ============================================================

def generate_action_plan(
    requirements,
    eligibility,
    degree,
    year,
    cgpa,
    skills,
    precomputed_action_plan=None
):
    # The AI action plan is generated together with requirement extraction
    # in the single OpenRouter request. Keep this function so the existing
    # endpoint structure and response format remain unchanged.
    if precomputed_action_plan is not None:
        return precomputed_action_plan

    # No second API call is made here.
    return {
        "goal": "",
        "current_position": "",
        "blockers": [],
        "missing_information": [],
        "action_plan": [],
        "skills_to_strengthen": [],
        "application_preparation": [],
        "conditional_actions": [],
        "readiness_checklist": [],
        "short_term_focus": ""
    }


# ============================================================
# MAIN ANALYSIS ENDPOINT
# ============================================================

@app.post("/analyze")
def analyze_opportunity(request: OpportunityRequest):

    try:

        # ----------------------------------------------------
        # 1. RETRIEVE WEBPAGE
        # ----------------------------------------------------

        webpage_text = get_webpage_text(
            request.url
        )

        # ----------------------------------------------------
        # 2. EXTRACT REQUIREMENTS
        # ----------------------------------------------------

        requirements, ai_action_plan = analyze_with_ai(
            webpage_text=webpage_text,
            degree=request.degree,
            year=request.year,
            cgpa=request.cgpa,
            skills=request.skills
        )

        # ----------------------------------------------------
        # 3. DETERMINISTIC ELIGIBILITY
        # ----------------------------------------------------

        eligibility = analyze_eligibility(
            requirements=requirements,
            degree=request.degree,
            year=request.year,
            cgpa=request.cgpa,
            skills=request.skills
        )

        # ----------------------------------------------------
        # 4. USE ACTION PLAN FROM THE SAME AI CALL
        # ----------------------------------------------------

        action_plan = generate_action_plan(
            requirements=requirements,
            eligibility=eligibility,
            degree=request.degree,
            year=request.year,
            cgpa=request.cgpa,
            skills=request.skills,
            precomputed_action_plan=ai_action_plan
        )

        # ----------------------------------------------------
        # 5. RETURN RESULT
        # ----------------------------------------------------

        return {
            "status": "success",

            "message": (
                "NAVIGATE completed opportunity "
                "analysis and action planning!"
            ),

            "student_profile": {
                "degree": request.degree,
                "year": request.year,
                "cgpa": request.cgpa,
                "skills": [
                    skill.strip()
                    for skill in request.skills.split(",")
                    if skill.strip()
                ]
            },

            "opportunity": {
                "url": request.url,
                "requirements": requirements,
                "webpage_preview": webpage_text[:3000]
            },

            "eligibility": eligibility,

            "action_plan": action_plan
        }

    except requests.exceptions.RequestException as e:

        return {
            "status": "error",
            "stage": "web_retrieval",
            "message": (
                "NAVIGATE could not retrieve the webpage."
            ),
            "details": str(e)
        }

    except json.JSONDecodeError as e:

        return {
            "status": "error",
            "stage": "ai_json",
            "message": (
                "The AI returned an invalid JSON response."
            ),
            "details": str(e)
        }

    except Exception as e:

        return {
            "status": "error",
            "stage": "analysis",
            "message": (
                "NAVIGATE encountered an unexpected error."
            ),
            "details": str(e)
        }
