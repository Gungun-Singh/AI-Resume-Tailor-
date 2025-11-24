# agent.py
import os
import re
import json
import ast
from dotenv import load_dotenv
from io import BytesIO

from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.configs import GroqConfig
from camel.agents import ChatAgent

load_dotenv("api.env")

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("❌ GROQ_API_KEY missing in api.env")

# MODEL SETUP (CAMEL docs style)
model = ModelFactory.create(
    model_platform=ModelPlatformType.GROQ,
    model_type="llama-3.1-8b-instant",
    model_config_dict=GroqConfig(temperature=0.2, max_tokens=4096).as_dict(),
)

# AGENT SETUP
tailor_agent = ChatAgent(
    system_message=(
        "You are an AI Resume Tailoring Assistant. Given a job description and a resume, "
        "you MUST output a single, valid JSON object (no explanation, no extra text) that "
        "matches the EXACT schema provided below. Use only the keys shown and valid JSON types.\n\n"
        "Output SCHEMA (exact keys and types):\n"
        "{\n"
        '  "matched_skills": ["skill1", "skill2", ...],\n'
        '  "missing_skills": ["skill1", "skill2", ...],\n'
        '  "improved_bullets": ["bullet1", "bullet2", ...],\n'
        '  "cover_letter": "short cover letter text (150-200 words)",\n'
        '  "match_score": 0  # integer 0-100\n'
        "}\n\n"
        "If information is unavailable, return an empty array or reasonable default (e.g. 0 for match_score)."
    ),
    model=model
)


def extract_pdf_text_from_bytes(pdf_bytes: bytes) -> str:
    """
    Helper to extract text from PDF bytes using pdfplumber.
    Returns concatenated text or empty string if nothing extracted.
    """
    try:
        import pdfplumber
    except Exception:
        return ""

    text = ""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        # pdfplumber could fail on some scanned images; return empty string
        return ""
    return text


def _extract_first_json_block(text: str) -> str | None:
    """
    Return the first {...} block found in text using a greedy bracket match.
    """
    # find first '{'
    start = text.find("{")
    if start == -1:
        return None

    # naive but effective approach: walk brackets to find the matching closing brace
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _safe_parse_json_like(text: str):
    """
    Try to parse JSON from text robustly. Return dict on success, else raise ValueError.
    """
    # 1) Try direct json.loads
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2) Try to extract first {...} block then json.loads
    block = _extract_first_json_block(text)
    if block:
        try:
            return json.loads(block)
        except Exception:
            pass

        # 3) Try ast.literal_eval as fallback (handles single quotes / python-like dicts)
        try:
            return ast.literal_eval(block)
        except Exception:
            pass

    # 4) Nothing worked
    raise ValueError("Could not parse JSON from agent response.")


def tailor_resume(job_description: str, resume_text: str) -> dict:
    """
    Returns a dict with either parsed JSON keys or raw agent text.
    On success returns {"result": parsed_dict}
    On parse failure returns {"raw": agent_text, "error": "..."}
    """

    if not job_description or not job_description.strip():
        return {"error": "Job description is empty."}
    if not resume_text or not resume_text.strip():
        return {"error": "Resume text is empty."}

    # Build prompt (include the JD and resume)
    prompt = f"""
    JOB DESCRIPTION:
    {job_description}

    RESUME:
    {resume_text}

    Remember: Return ONLY a single valid JSON object EXACTLY matching the schema below (no extra explanation):

    {{
      "matched_skills": ["skill1", "skill2"],
      "missing_skills": ["skill1", "skill2"],
      "improved_bullets": ["bullet1", "bullet2"],
      "cover_letter": "cover letter text (150-200 words)",
      "match_score": 0
    }}
    """

    # Send to CAMEL agent
    response = tailor_agent.step(prompt)
    agent_text = response.msgs[0].content

    # Try to parse
    try:
        parsed = _safe_parse_json_like(agent_text)
        # Ensure keys exist and have safe defaults
        parsed_safe = {
            "matched_skills": parsed.get("matched_skills", []) if isinstance(parsed, dict) else [],
            "missing_skills": parsed.get("missing_skills", []) if isinstance(parsed, dict) else [],
            "improved_bullets": parsed.get("improved_bullets", []) if isinstance(parsed, dict) else [],
            "cover_letter": parsed.get("cover_letter", "") if isinstance(parsed, dict) else "",
            "match_score": int(parsed.get("match_score", 0)) if isinstance(parsed, dict) else 0,
        }
        return {"result": parsed_safe}
    except Exception as e:
        # parsing failed — return raw text so UI can display it for debugging
        return {"raw": agent_text, "error": "parse_failure", "exception": str(e)}
