# config.py

# --- Matching Algorithm Configuration ---

# The minimum similarity score (0-100) for a merchant to be considered a potential match.
# A lower value will include more, less-similar results.
MATCH_SCORE_THRESHOLD = 60

# If the top match's score is this much higher than the second-best match,
# we consider it a confident, unique match and don't ask for clarification.
# A higher value means the system will ask for clarification more often.
CONFIDENT_MATCH_DIFFERENCE = 15

# The maximum number of choices to present to the user when a match is ambiguous.
MAX_CLARIFICATION_OPTIONS = 2

# --- Application Configuration ---
SECRET_KEY = "a-very-secret-and-secure-key"
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret")
