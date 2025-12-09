import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup logging configuration"""

    # Create logs directory
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler for all logs
    file_handler = RotatingFileHandler(
        f"{log_dir}/c2_server.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Separate file for security events
    security_handler = RotatingFileHandler(
        f"{log_dir}/security.log",
        maxBytes=10*1024*1024,
        backupCount=10
    )
    security_handler.setFormatter(detailed_formatter)
    security_handler.setLevel(logging.WARNING)

    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)

    # Task results logger
    task_handler = RotatingFileHandler(
        f"{log_dir}/tasks.log",
        maxBytes=50*1024*1024,  # 50MB for task results
        backupCount=5
    )
    task_handler.setFormatter(detailed_formatter)

    task_logger = logging.getLogger("tasks")
    task_logger.addHandler(task_handler)

    return logger

def log_task_result(task_id: str, node_id: str, result: dict):
    """Log task execution result"""
    task_logger = logging.getLogger("tasks")
    task_logger.info(f"Task {task_id} on node {node_id}: {result}")

def log_security_event(event_type: str, details: dict):
    """Log security-related events"""
    security_logger = logging.getLogger("security")
    security_logger.warning(f"{event_type}: {details}")
