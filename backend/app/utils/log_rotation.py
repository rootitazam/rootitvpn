import os
import glob
from datetime import datetime, timedelta
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def rotate_logs():
    """Delete log files older than retention period"""
    log_path = Path(settings.log_path)
    retention_hours = settings.log_retention_hours
    cutoff_time = datetime.now() - timedelta(hours=retention_hours)
    
    if not log_path.exists():
        logger.warning(f"Log path does not exist: {log_path}")
        return
    
    deleted_count = 0
    total_size_freed = 0
    
    # Find all log files
    log_patterns = [
        "access.log*",
        "error.log*",
        "*.log.*",  # Rotated logs
    ]
    
    for pattern in log_patterns:
        for log_file in log_path.glob(pattern):
            try:
                # Get file modification time
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if mtime < cutoff_time:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    total_size_freed += file_size
                    logger.info(f"Deleted old log file: {log_file.name} ({file_size} bytes)")
            except Exception as e:
                logger.error(f"Error deleting log file {log_file}: {e}")
    
    logger.info(f"Log rotation completed: {deleted_count} files deleted, {total_size_freed / 1024 / 1024:.2f} MB freed")


def clean_access_logs_db(db):
    """Clean old access logs from database"""
    from app.models import AccessLog
    from datetime import datetime, timedelta
    
    retention_hours = settings.log_retention_hours
    cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
    
    try:
        deleted_count = db.query(AccessLog).filter(
            AccessLog.timestamp < cutoff_time
        ).delete()
        db.commit()
        logger.info(f"Deleted {deleted_count} old access log records from database")
        return deleted_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning access logs from database: {e}")
        return 0

