# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

TIER_1_CRITERIA = [
    "Role Identification",
    "Task Nature",
    "Acceptance Criteria",
    "Business Need",
    "Unambiguous"
]

TIER_2_CRITERIA = [
    "Dependency",
    "Priority",
    "Quality Requirement",
    "Estimable",
    "Well Formed",
    "Problem Oriented",
    "Unique",
    "Testable",
    "Task Identification"
]