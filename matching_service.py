# matching_service.py
from thefuzz import process
from data import MERCHANTS
from config import MATCH_SCORE_THRESHOLD, CONFIDENT_MATCH_DIFFERENCE, MAX_CLARIFICATION_OPTIONS

class MerchantMatcher:
    """Handles the logic of finding merchants based on user input."""

    def __init__(self, merchants_data):
        self.merchants = merchants_data
        # Create a mapping for quick lookups by ID
        self.merchants_by_id = {m['id']: m for m in self.merchants}

    def find_matches(self, user_input, nearby_beacon_ids):
        """
        Finds merchant matches from a user's voice command.

        Returns a dictionary indicating the status:
        - 'NO_MATCH': No suitable merchant found.
        - 'SINGLE_MATCH': One confident match was found.
        - 'CLARIFICATION_NEEDED': Multiple close matches were found.
        """
        # 1. Filter merchants to only those that are nearby
        nearby_merchants = [m for m in self.merchants if m["beacon_id"] in nearby_beacon_ids]
        if not nearby_merchants:
            return {"status": "NO_MATCH"}

        # 2. Use thefuzz to find the best matches from the names of nearby merchants
        # We create a dictionary of {merchant_name: merchant_id} for processing
        choices = {m['name']: m['id'] for m in nearby_merchants}
        
        # 'process.extract' returns a list of tuples: (name, score, id)
        matches = [(name, score, choices[name]) for name, score in process.extract(user_input, choices.keys(), limit=MAX_CLARIFICATION_OPTIONS)]

        # Filter out any matches below our score threshold
        strong_matches = [m for m in matches if m[1] >= MATCH_SCORE_THRESHOLD]

        if not strong_matches:
            return {"status": "NO_MATCH"}

        # 3. Analyze the results to decide the outcome
        top_match_score = strong_matches[0][1]
        
        # If there's only one strong match, it's a confident win
        if len(strong_matches) == 1:
            match_id = strong_matches[0][2]
            return {"status": "SINGLE_MATCH", "data": self.merchants_by_id[match_id]}

        # If there are multiple matches, check if the top one is significantly better
        second_match_score = strong_matches[1][1]
        if (top_match_score - second_match_score) > CONFIDENT_MATCH_DIFFERENCE:
            match_id = strong_matches[0][2]
            return {"status": "SINGLE_MATCH", "data": self.merchants_by_id[match_id]}
        
        # Otherwise, we need the user to clarify
        clarification_options = [self.merchants_by_id[m[2]] for m in strong_matches]
        return {"status": "CLARIFICATION_NEEDED", "data": clarification_options}

# Create a single instance of the matcher to be used by the app
matcher = MerchantMatcher(MERCHANTS)