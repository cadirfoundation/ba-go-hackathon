import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

def get_db_client():
    """Establishes a secure connection to ClickHouse Cloud."""
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8443)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        secure=True
    )

def query_top_performing_dramas():
    """Retrieves top micro-dramas ordered by total viewer sessions and average completion rate."""
    client = get_db_client()
    query = """
        SELECT 
            drama_id,
            count() AS total_views,
            avg(completion_rate) * 100 AS avg_completion_pct
        FROM viewing_sessions
        GROUP BY drama_id
        ORDER BY total_views DESC
    """
    return client.query(query).result_rows

def query_drop_off_timing(drama_id: int):
    """Retrieves precise drop-off timestamps (in seconds) per episode relative to total duration."""
    client = get_db_client()
    query = f"""
        SELECT 
            episode_num,
            avg(drop_off_second) AS avg_drop_off_second,
            count() AS drop_off_count
        FROM drop_off_events
        WHERE drama_id = {int(drama_id)}
        GROUP BY episode_num
        ORDER BY episode_num ASC
    """
    return client.query(query).result_rows

def query_admob_monetization_estimate(drama_id: int):
    """Retrieves actual AdMob revenue, impression counts, and average eCPM from the admob_impressions table."""
    client = get_db_client()
    query = f"""
        SELECT 
            episode_num,
            count() AS total_impressions,
            sum(revenue_usd) AS estimated_admob_revenue_usd,
            avg(estimated_ecpm_usd) AS avg_ecpm
        FROM admob_impressions
        WHERE drama_id = {int(drama_id)}
        GROUP BY episode_num
        ORDER BY episode_num ASC
    """
    return client.query(query).result_rows

def query_regional_drop_off_stats(drama_id: int):
    """Query drop-off rates and completion percentages grouped by geographic region."""
    client = get_db_client()
    query = f"""
        SELECT 
            region,
            count() AS total_views,
            avg(completion_rate) * 100 AS avg_completion_pct
        FROM viewing_sessions
        WHERE drama_id = {int(drama_id)}
        GROUP BY region
        ORDER BY avg_completion_pct ASC
    """
    return client.query(query).result_rows

def query_demographic_insights(drama_id: int):
    """Query completion rates and views grouped by Gender, Age Group, and Content Affinity."""
    client = get_db_client()
    query = f"""
        SELECT 
            gender,
            age_group,
            content_affinity,
            count() AS audience_count,
            avg(completion_rate) * 100 AS avg_completion_pct
        FROM viewing_sessions
        WHERE drama_id = {int(drama_id)}
        GROUP BY gender, age_group, content_affinity
        ORDER BY audience_count DESC
    """
    return client.query(query).result_rows

def run_dynamic_sql(sql_query: str):
    """Executes a dynamic SQL SELECT query on ClickHouse and returns a dictionary with 'data' and 'columns' keys, or an error string if execution fails."""
    try:
        client = get_db_client()
        result = client.query(sql_query)
        return {
            "data": result.result_rows,
            "columns": result.column_names
        }
    except Exception as e:
        return str(e)
