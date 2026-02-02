# src/evaluator.py

TIER_1_KEYS = [
    "Role Identification", 
    "Task Nature",         
    "Acceptance Criteria", 
    "Business Need", 
    "Unambiguous"
]

TIER_2_KEYS = [
    "Task Identification", 
    "Dependency", 
    "Priority", 
    "Quality Requirement", 
    "Estimable", 
    "Well Formed", 
    "Problem Oriented", 
    "Unique", 
    "Testable"
]

def analyze_structural_quality(scores):
    """
    Implements the 'Weighted Criticality' check.
    Returns: (Tier 1 Score, Tier 2 Score, Is_Structurally_Sound)
    """
    tier_1_total = sum(scores.get(k, 0) for k in TIER_1_KEYS)
    tier_2_total = sum(scores.get(k, 0) for k in TIER_2_KEYS)
    
    is_structurally_sound = tier_1_total >= 8
    
    return tier_1_total, tier_2_total, is_structurally_sound