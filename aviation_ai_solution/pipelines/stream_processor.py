"""
Stream Processor Pipeline for handling online streaming data.

This module handles downloading, extracting, and processing streaming aviation data
from online sources, grouping results by session with specified dates.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class StreamSession:
    """Represents a session of streamed data grouped by date."""
    session_id: str = ""
    date: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    data_points: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"SESSION_{self.date}_{hashlib.md5(self.date.encode()).hexdigest()[:8]}"


class StreamProcessor:
    """
    Processor for streaming aviation data from online sources.
    
    Capabilities:
    - Download data from streaming URLs
    - Extract and parse various data formats (JSON, CSV, binary)
    - Group data into chronological sessions by date
    - Process real-time ADS-B, METAR, NOTAM, and ATC transcript streams
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.sessions: Dict[str, StreamSession] = {}
        self.processed_count = 0
        self.error_count = 0
        self.connected = False
        self.current_stream_url = None
    
    def connect(self, url: str) -> bool:
        """
        Establish connection to a stream source.
        
        Args:
            url: Stream URL (rtsp://, http://, https://, file://)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Validate URL format
            if not url or not isinstance(url, str):
                self.error_count += 1
                return False
            
            # Store connection info
            self.current_stream_url = url
            self.connected = True
            
            # In production, establish actual connection based on URL scheme
            # For now, validate basic URL structure
            if url.startswith(('http://', 'https://', 'rtsp://', 'rtmp://', 'file://')):
                print(f"Connected to stream: {url}")
                return True
            else:
                # Try to treat as file path
                import os
                if os.path.exists(url):
                    print(f"Connected to file stream: {url}")
                    return True
                self.error_count += 1
                return False
                
        except Exception as e:
            self.error_count += 1
            print(f"Connection error: {e}")
            return False
    
    async def fetch_stream(self, url: str) -> List[Dict]:
        """Fetch data from a streaming URL."""
        # In production, use aiohttp for async HTTP requests
        # For now, simulate with sample data
        print(f"Fetching stream from: {url}")
        
        # Simulated stream data
        sample_data = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "adsb",
                "flight": "DLH456",
                "icao24": "3c6645",
                "latitude": 50.0379,
                "longitude": 8.5622,
                "altitude": 35000,
                "velocity": 450,
                "heading": 270
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "metar",
                "station": "EDDF",
                "observation_time": datetime.utcnow().isoformat(),
                "temp": 15,
                "dewpoint": 8,
                "wind_dir": 250,
                "wind_speed": 12,
                "visibility": 9999,
                "raw": "METAR EDDF 061430Z 25012KT 9999 FEW035 15/08 Q1013"
            }
        ]
        
        return sample_data
    
    def extract_data(self, raw_data: bytes, format_type: str) -> List[Dict]:
        """Extract structured data from raw stream data."""
        try:
            if format_type == "json":
                return json.loads(raw_data.decode('utf-8'))
            elif format_type == "csv":
                return self._parse_csv(raw_data)
            elif format_type == "base64":
                import base64
                decoded = base64.b64decode(raw_data)
                return json.loads(decoded.decode('utf-8'))
            else:
                # Try JSON first, then treat as plain text
                try:
                    return json.loads(raw_data.decode('utf-8'))
                except:
                    return [{"raw": raw_data.decode('utf-8', errors='ignore')}]
        except Exception as e:
            self.error_count += 1
            print(f"Error extracting data: {e}")
            return []
    
    def _parse_csv(self, raw_data: bytes) -> List[Dict]:
        """Parse CSV formatted data."""
        lines = raw_data.decode('utf-8').strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(',')
        records = []
        
        for line in lines[1:]:
            values = line.split(',')
            if len(values) == len(headers):
                records.append(dict(zip(headers, values)))
        
        return records
    
    def group_by_session(self, data_points: List[Dict], 
                         date_format: str = "%Y-%m-%d") -> Dict[str, StreamSession]:
        """Group data points into sessions by date."""
        sessions = {}
        
        for point in data_points:
            # Extract timestamp
            timestamp_str = point.get("timestamp", "")
            
            try:
                # Parse timestamp
                if 'T' in timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.utcnow()
                
                # Get date string
                date_str = timestamp.strftime(date_format)
                
                # Create or update session
                if date_str not in sessions:
                    sessions[date_str] = StreamSession(date=date_str)
                
                sessions[date_str].data_points.append(point)
                sessions[date_str].end_time = timestamp
                
            except Exception as e:
                self.error_count += 1
                print(f"Error grouping data point: {e}")
        
        return sessions
    
    async def process_stream(self, stream_url: str, 
                            output_dir: str = "./output") -> Dict[str, Any]:
        """
        Complete stream processing pipeline.
        
        Args:
            stream_url: URL of the streaming data source.
            output_dir: Directory to save processed results.
            
        Returns:
            Processing results with session summaries.
        """
        print(f"Starting stream processing from: {stream_url}")
        start_time = datetime.utcnow()
        
        # Step 1: Fetch stream data
        raw_data_points = await self.fetch_stream(stream_url)
        
        # Step 2: Group by session (date)
        self.sessions = self.group_by_session(raw_data_points)
        
        # Step 3: Save sessions to output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        session_summaries = []
        for date_str, session in self.sessions.items():
            # Save session data
            session_file = output_path / f"session_{date_str}.json"
            
            session_data = {
                "session_id": session.session_id,
                "date": session.date,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "data_point_count": len(session.data_points),
                "data_points": session.data_points,
                "metadata": session.metadata
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            # Create summary
            session_summaries.append({
                "session_id": session.session_id,
                "date": session.date,
                "data_points": len(session.data_points),
                "file": str(session_file)
            })
            
            self.processed_count += len(session.data_points)
        
        end_time = datetime.utcnow()
        
        return {
            "success": True,
            "stream_url": stream_url,
            "processing_time_seconds": (end_time - start_time).total_seconds(),
            "sessions_created": len(self.sessions),
            "total_data_points": self.processed_count,
            "errors": self.error_count,
            "session_summaries": session_summaries,
            "output_directory": str(output_path)
        }
    
    def download_and_extract(self, archive_url: str, 
                            extract_dir: str = "./data_lake/downloads") -> List[str]:
        """
        Download and extract archived data from a URL.
        
        Args:
            archive_url: URL to downloadable archive (zip, tar.gz, etc.).
            extract_dir: Directory to extract files to.
            
        Returns:
            List of extracted file paths.
        """
        import tempfile
        import requests
        
        extract_path = Path(extract_dir)
        extract_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download file
            print(f"Downloading from: {archive_url}")
            response = requests.get(archive_url, stream=True)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".download") as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                temp_path = tmp.name
            
            # Determine archive type and extract
            extracted_files = []
            
            if archive_url.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                    extracted_files = [str(extract_path / f) for f in zip_ref.namelist()]
            
            elif archive_url.endswith('.tar.gz') or archive_url.endswith('.tgz'):
                import tarfile
                with tarfile.open(temp_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_path)
                    extracted_files = [str(extract_path / f) for f in tar_ref.getnames()]
            
            # Cleanup temp file
            Path(temp_path).unlink()
            
            print(f"Extracted {len(extracted_files)} files to {extract_path}")
            return extracted_files
            
        except Exception as e:
            print(f"Error downloading/extracting: {e}")
            self.error_count += 1
            return []


async def main():
    """Example usage of StreamProcessor."""
    processor = StreamProcessor()
    
    # Process a stream
    result = await processor.process_stream(
        stream_url="https://example.com/aviation/stream",
        output_dir="./output/sessions"
    )
    
    print("\nStream Processing Results:")
    print(json.dumps(result, indent=2))
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
