import os
import sys
from dotenv import load_dotenv

# Ensure local backend imports load properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google import genai
from google.genai import types
import clickhouse_tools

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION", "us-central1")

# Initialize Vertex AI Client using google-genai SDK
client = genai.Client(vertexai=True, project=PROJECT_ID, location=REGION)

SYSTEM_INSTRUCTION = """
You are BA_Go, an executive AI Decision Agent for MicroDrama Streaming platforms (AVOD & SVOD).
Your primary role is to evaluate business hypotheses, analyze viewer retention, regional expat behavior, and optimize AdMob ad revenue.

Available ClickHouse Database Tables:

1. `viewing_sessions`:
   - Columns: `session_id` (String), `user_id` (String), `user_plan` (Enum8: 'AVOD', 'SVOD'), `drama_id` (UInt32), `episode_num` (UInt16), `content_language` (LowCardinality String: 'Urdu', 'English', 'Punjabi', 'Pashto', 'Hindi', 'Arabic'), `watch_time_seconds` (UInt16), `completion_rate` (Float32), `region` (String: 'Canada', 'North America', 'UK', 'EU', 'Middle East', 'South Asia', 'Asia Pacific', 'South America'), `gender` (String), `age_group` (String), `content_affinity` (String), `day_of_week` (String), `hour_of_day` (UInt8), `created_at` (DateTime).

2. `drop_off_events`:
   - Columns: `event_id` (String), `user_id` (String), `drama_id` (UInt32), `episode_num` (UInt16), `content_language` (String), `drop_off_second` (UInt16), `region` (String), `created_at` (DateTime).

3. `admob_impressions`:
   - Columns: `impression_id` (String), `user_id` (String), `drama_id` (UInt32), `episode_num` (UInt16), `content_language` (String), `ad_type` (Enum8: 'Pre-Roll', 'Mid-Roll', 'Post-Roll'), `estimated_ecpm_usd` (Float32), `revenue_usd` (Float32), `region` (String), `created_at` (DateTime).

SQL Writing Rules:
- Generate clean, high-performance ClickHouse SQL SELECT queries via the `run_dynamic_sql` tool.
- For weekend queries, check `day_of_week IN ('Saturday', 'Sunday')`.
- Calculate percentages using `AVG(completion_rate) * 100` and revenues using `SUM(revenue_usd)`.

Output Format Requirements:
Always format your final text response strictly using these standalone bold sections:

**Hypothesis Evaluation**
[Direct 1-2 sentence confirmation or disproval of the hypothesis]

**Key SQL Insights**
- [Metric 1 summary retrieved from database]
- [Metric 2 summary retrieved from database]

**Suggested Operational Action**
- **Action:** [Specific workflow/content edit recommendation]
- **Target Segment:** [Region, Language, or Audience demographic]

**Pros & Cons**
- **Pros:** [2 key advantages]
- **Cons:** [2 potential operational or revenue risks]

**Risk Assessment**
[Low / Medium / High] - [Brief explanation]
"""

def run_agent_query(user_prompt: str) -> str:
    """Executes a natural language business query by calling Gemini 2.5 Pro with dynamic ClickHouse SQL tools."""
    try:
        chat = client.chats.create(
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[clickhouse_tools.run_dynamic_sql],
                temperature=0.1
            )
        )
        
        response = chat.send_message(user_prompt)
        return response.text

    except Exception as e:
        error_msg = str(e)
        if "Reauthentication" in error_msg or "401" in error_msg:
            return "⚠️ **Authentication Error**: Google Cloud credentials expired. Please run `gcloud auth application-default login` in your terminal."
        return f"⚠️ **Agent Execution Error**: {error_msg}"

if __name__ == "__main__":
    print("\n--- Testing BA_Go Agent Decision Engine ---")
    test_hypothesis = "Test hypothesis: Do viewers in Canada watching Punjabi dubbing on weekends generate higher AdMob revenue than weekdays?"
    print(run_agent_query(test_hypothesis))