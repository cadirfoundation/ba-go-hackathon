import os
import random
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import clickhouse_connect

load_dotenv()

HOST = os.getenv("CLICKHOUSE_HOST")
PORT = int(os.getenv("CLICKHOUSE_PORT", 8443))
USER = os.getenv("CLICKHOUSE_USER", "default")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")

CITY_MAP = {
    "Canada": ["Toronto", "Vancouver", "Calgary"],
    "North America": ["New York", "Chicago", "Los Angeles"],
    "UK": ["London", "Birmingham", "Manchester"],
    "EU": ["Frankfurt", "Paris", "Amsterdam"],
    "Middle East": ["Dubai", "Riyadh", "Doha"],
    "South Asia": ["Lahore", "Karachi", "Mumbai"],
    "Asia Pacific": ["Singapore", "Sydney", "Tokyo"],
    "South America": ["São Paulo", "Buenos Aires", "Bogotá"]
}

def main():
    print("Connecting to ClickHouse Cloud...")
    client = clickhouse_connect.get_client(host=HOST, port=PORT, username=USER, password=PASSWORD, secure=True)

    print("Re-creating tables for 50-episode microdrama schema...")
    client.command("DROP TABLE IF EXISTS drama_catalog")
    client.command("DROP TABLE IF EXISTS viewing_sessions")
    client.command("DROP TABLE IF EXISTS drop_off_events")
    client.command("DROP TABLE IF EXISTS admob_impressions")

    client.command("""
    CREATE TABLE drama_catalog (
        drama_id UInt32, title String, total_episodes UInt16, genre String,
        target_affinity String, status Enum8('Active' = 1, 'Unpromoted' = 2, 'Archived' = 3), created_at Date
    ) ENGINE = MergeTree() ORDER BY drama_id
    """)

    client.command("""
    CREATE TABLE viewing_sessions (
        session_id String, user_id String, user_plan Enum8('AVOD' = 1, 'SVOD' = 2),
        drama_id UInt32, title String, episode_num UInt16, content_language LowCardinality(String),
        watch_time_seconds UInt16, completion_rate Float32, region String, city String,
        gender String, age_group String, content_affinity String, day_of_week String,
        hour_of_day UInt8, created_at DateTime
    ) ENGINE = MergeTree() ORDER BY (drama_id, episode_num, region, content_language, created_at)
    """)

    client.command("""
    CREATE TABLE drop_off_events (
        event_id String, user_id String, drama_id UInt32, title String, episode_num UInt16,
        content_language LowCardinality(String), drop_off_second UInt16, region String, city String, created_at DateTime
    ) ENGINE = MergeTree() ORDER BY (drama_id, episode_num, created_at)
    """)

    client.command("""
    CREATE TABLE admob_impressions (
        impression_id String, user_id String, drama_id UInt32, title String, episode_num UInt16,
        content_language LowCardinality(String), ad_type Enum8('Pre-Roll' = 1, 'Mid-Roll' = 2, 'Post-Roll' = 3),
        estimated_ecpm_usd Float32, revenue_usd Float32, region String, created_at DateTime
    ) ENGINE = MergeTree() ORDER BY (drama_id, episode_num, region, created_at)
    """)

    # All 10 Dramas updated to 50 Episodes
    catalog_dramas = [
        (101, "A Love Once Betrayed", 50, "Revenge Drama", "Revenge Drama", "Active"),
        (102, "The Marriage Contract", 50, "Billionaire Romance", "Billionaire Romance", "Active"),
        (103, "Blood Contract", 50, "Urban Thriller", "Urban Thriller", "Active"),
        (104, "The Family Secret", 50, "Family Drama", "Family Drama", "Active"),
        (105, "Two Worlds Apart", 50, "Romance", "Romance", "Active"),
        (106, "Twist of Time", 50, "Fantasy/Sci-Fi", "Fantasy/Sci-Fi", "Active"),
        (107, "Duty or Desire", 50, "Revenge Drama", "Revenge Drama", "Active"),
        (108, "Parlor Wali Original", 50, "Comedy/Drama", "Urban Thriller", "Active"),
        (109, "Love me or i Die", 50, "Romantic Thriller", "Romance", "Active"),
        (110, "Mysterious Murder", 50, "Crime Mystery", "Urban Thriller", "Unpromoted")
    ]

    catalog_data = [[d[0], d[1], d[2], d[3], d[4], d[5], date(2026, 1, 1)] for d in catalog_dramas]
    client.insert("drama_catalog", catalog_data, column_names=["drama_id", "title", "total_episodes", "genre", "target_affinity", "status", "created_at"])

    title_map = {d[0]: d[1] for d in catalog_dramas}
    active_drama_ids = [101, 102, 103, 104, 105, 106, 107, 108, 109]

    sessions_data, drop_off_data, admob_data = [], [], []
    languages = ["Urdu", "English", "Punjabi", "Pashto", "Hindi", "Arabic"]
    regions = list(CITY_MAP.keys())
    base_time = datetime.now() - timedelta(days=30)

    print("Generating 12,000+ sessions across 50 episodes per drama...")

    for i in range(12500):
        user_id = f"usr_{random.randint(10000, 99999)}"
        user_plan = "AVOD" if random.random() > 0.18 else "SVOD"
        drama_id = random.choice(active_drama_ids)
        title = title_map[drama_id]
        episode_num = random.randint(1, 50) # 50 Episodes per Title
        region = random.choice(regions)
        city = random.choice(CITY_MAP[region])
        gender = random.choice(["Male", "Female", "Non-Binary"])
        age_group = random.choice(["18-24", "25-34", "35-44", "45+"])
        affinity = random.choice(["Billionaire Romance", "Revenge Drama", "Urban Thriller", "Fantasy/Sci-Fi"])
        
        timestamp = base_time + timedelta(minutes=random.randint(1, 43200))
        day_str = timestamp.strftime("%A")
        hour_val = timestamp.hour

        if region in ["Canada", "UK"]:
            content_language = random.choice(["Punjabi", "Urdu", "English"])
        elif region == "Middle East":
            content_language = random.choice(["Arabic", "Urdu", "Pashto"])
        else:
            content_language = random.choice(languages)

        # Injected Anomaly: Episode 3 drop-off spike across dramas
        if episode_num == 3 and random.random() < 0.65:
            watch_time = random.randint(12, 35)
            completion_rate = watch_time / 120.0
            drop_off_data.append([f"evt_{i}", user_id, drama_id, title, episode_num, content_language, watch_time, region, city, timestamp])
        else:
            watch_time = random.randint(85, 120)
            completion_rate = watch_time / 120.0
            if random.random() < 0.12:
                drop_off_data.append([f"evt_{i}", user_id, drama_id, title, episode_num, content_language, watch_time, region, city, timestamp])

        if day_str in ["Saturday", "Sunday"] and region in ["Canada", "UK"] and content_language in ["Punjabi", "Urdu"]:
            ecpm = random.uniform(8.50, 14.00)
        else:
            ecpm = random.uniform(2.20, 5.50)

        if user_plan == "AVOD":
            admob_data.append([f"imp_{i}_1", user_id, drama_id, title, episode_num, content_language, "Pre-Roll", ecpm, ecpm / 1000.0, region, timestamp])
            if completion_rate > 0.45:
                admob_data.append([f"imp_{i}_2", user_id, drama_id, title, episode_num, content_language, "Mid-Roll", ecpm, ecpm / 1000.0, region, timestamp])
            if completion_rate >= 0.90:
                admob_data.append([f"imp_{i}_3", user_id, drama_id, title, episode_num, content_language, "Post-Roll", ecpm, ecpm / 1000.0, region, timestamp])

        sessions_data.append([
            f"ses_{i}", user_id, user_plan, drama_id, title, episode_num, content_language, watch_time,
            completion_rate, region, city, gender, age_group, affinity, day_str, hour_val, timestamp
        ])

    print("Inserting 12,000+ rows into ClickHouse Cloud...")
    client.insert("viewing_sessions", sessions_data, column_names=["session_id", "user_id", "user_plan", "drama_id", "title", "episode_num", "content_language", "watch_time_seconds", "completion_rate", "region", "city", "gender", "age_group", "content_affinity", "day_of_week", "hour_of_day", "created_at"])
    client.insert("drop_off_events", drop_off_data, column_names=["event_id", "user_id", "drama_id", "title", "episode_num", "content_language", "drop_off_second", "region", "city", "created_at"])
    client.insert("admob_impressions", admob_data, column_names=["impression_id", "user_id", "drama_id", "title", "episode_num", "content_language", "ad_type", "estimated_ecpm_usd", "revenue_usd", "region", "created_at"])

    print("Simulating real-time Google Ads CPI API sync...")

    # 1. Create the CPI table in ClickHouse
    client.command("""
        CREATE TABLE IF NOT EXISTS regional_cpi (
            region String,
            cpi_usd Float32,
            last_synced DateTime
        ) ENGINE = MergeTree()
        ORDER BY region
    """)

    # 2. Clear old data to prevent duplicates on rerun
    client.command("TRUNCATE TABLE regional_cpi")

    # 3. Define the simulated Google Ads API payload
    now = datetime.now()
    cpi_data = [
        ["Canada", 0.65, now],
        ["North America", 0.72, now],
        ["UK", 0.82, now],
        ["EU", 0.55, now],
        ["Middle East", 0.45, now],
        ["South Asia", 0.18, now],
        ["Asia Pacific", 0.38, now],
        ["South America", 0.28, now]
    ]

    # 4. Insert the live payload into the database
    client.insert(
        'regional_cpi', 
        cpi_data, 
        column_names=['region', 'cpi_usd', 'last_synced']
    )
    print("Real-time CPI data synced to ClickHouse!")

    print("Bulk ingestion complete! Database ready with 50-episode microdrama dataset.")

if __name__ == "__main__":
    main()