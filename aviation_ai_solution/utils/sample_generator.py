"""
Sample Data Generator for Aviation AI Solution.
Creates dummy audio files and seeds the MongoDB data lake with realistic records.
"""

import os
import wave
import struct
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from aviation_ai_solution.data_lake.mongo_client import AviationDataLake

def create_dummy_wav(file_path: str, duration_sec: int = 10):
    """Create a dummy WAV file with random noise to simulate voice records."""
    sample_rate = 16000
    # 16-bit mono
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for _ in range(sample_rate * duration_sec):
            # Random noise
            value = random.randint(-32767, 32767)
            wav_file.writeframes(struct.pack('h', value))

def seed_database(db: AviationDataLake):
    """Seed the database with realistic aviation records."""
    flights = [
        {"code": "DLH456", "origin": "EDDM", "destination": "EDDF", "fir": "EDGG"},
        {"code": "AFR123", "origin": "LFFF", "destination": "EDDM", "fir": "LFFF"},
        {"code": "BAW789", "origin": "EGTT", "destination": "LFFF", "fir": "EGTT"},
        {"code": "KLM456", "origin": "EBBU", "destination": "EDDF", "fir": "EBBU"},
    ]
    
    records = []
    transcripts = []
    
    for flight in flights:
        code = flight["code"]
        # Create 5 records per flight
        for i in range(5):
            timestamp = (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat()
            
            # Audio record
            audio_path = f"data_lake/samples/{code}_{i}.wav"
            records.append({
                "flight_code": code,
                "timestamp": timestamp,
                "type": "audio",
                "source": audio_path,
                "fir": flight["fir"],
                "origin": flight["origin"],
                "destination": flight["destination"],
                "duration": 15.0 + random.random() * 10
            })
            
            # Corresponding transcript
            text_samples = [
                f"{code}, cleared for approach runway 25C, maintain 3000 feet.",
                f"{code}, turn left heading 270, descend to flight level 100.",
                f"{code}, contact tower on 118.1, good day.",
                f"Tower, {code} established on final, requesting landing clearance.",
                f"{code}, climbing to flight level 350, report reaching."
            ]
            transcripts.append({
                "flight_code": code,
                "timestamp": timestamp,
                "text": random.choice(text_samples),
                "confidence": 0.85 + random.random() * 0.1,
                "speaker": "ATC" if random.random() > 0.5 else "Pilot"
            })
            
    # Insert records
    for r in records:
        db.insert_record("records", r)
    
    # Insert transcripts
    for t in transcripts:
        db.insert_record("transcripts", t)
        
    return len(records)

def setup_samples(config: Dict = None):
    """Main entry point to setup samples."""
    db = AviationDataLake(config)
    
    # Create samples directory
    samples_dir = Path("aviation_ai_solution/data_lake/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    # Create audio files
    flights = ["DLH456", "AFR123", "BAW789", "KLM456"]
    created_count = 0
    for flight in flights:
        for i in range(5):
            file_path = samples_dir / f"{flight}_{i}.wav"
            create_dummy_wav(str(file_path))
            created_count += 1
            
    # Seed DB
    seeded_count = seed_database(db)
    
    print(f"Created {created_count} sample audio files.")
    print(f"Seeded {seeded_count} records into database.")

if __name__ == "__main__":
    setup_samples()
