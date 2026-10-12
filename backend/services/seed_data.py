import json

from database.database import SessionLocal
from models.affair import Affair


db = SessionLocal()


sample_affairs = [
    Affair(
        category="Technology",
        title="AI is changing the way people work",
        summary="Artificial intelligence is increasingly being used across different industries.",
        remember=json.dumps([
            "AI is being adopted across industries",
            "Automation is an important application",
            "AI skills are becoming increasingly useful"
        ]),
        source="DailyIQ Demo",
        source_url="https://example.com"
    ),

    Affair(
        category="Economy",
        title="Understanding economic developments",
        summary="Economic developments can affect businesses, employment and consumers.",
        remember=json.dumps([
            "Economic policies can affect businesses",
            "Employment is connected to economic growth",
            "Consumers are affected by inflation"
        ]),
        source="DailyIQ Demo",
        source_url="https://example.com"
    )
]


db.add_all(sample_affairs)
db.commit()
db.close()


print("Sample affairs added successfully!")