import pandas as pd
from config import TIER_1_CRITERIA, TIER_2_CRITERIA

def calculate_weighted_score(scores_dict):
    tier_1_score = sum(scores_dict.get(k, 0) for k in TIER_1_CRITERIA)
    tier_2_score = sum(scores_dict.get(k, 0) for k in TIER_2_CRITERIA)
    
    total_score = tier_1_score + tier_2_score
    
    is_structurally_sound = True if tier_1_score >= (len(TIER_1_CRITERIA) * 1.5) else False
    
    return total_score, is_structurally_sound

def evaluate_story(user_story, client):
    pass