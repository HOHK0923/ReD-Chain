import json
import os
from datetime import datetime
from typing import Dict, Any

class ResultStorage:
    """Store task results to files for later analysis"""

    def __init__(self, base_dir: str = "results"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save_result(self, task_id: str, node_id: str, task_type: str, result: Dict[Any, Any]):
        """Save task result to file"""

        # Create directory structure: results/YYYY-MM-DD/task_type/
        date_str = datetime.now().strftime("%Y-%m-%d")
        task_dir = os.path.join(self.base_dir, date_str, task_type)
        os.makedirs(task_dir, exist_ok=True)

        # Save result
        filename = f"{task_id}_{node_id[:8]}.json"
        filepath = os.path.join(task_dir, filename)

        data = {
            "task_id": task_id,
            "node_id": node_id,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_results(self, task_type: str = None, date: str = None):
        """Retrieve stored results"""

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        results_dir = os.path.join(self.base_dir, date)

        if not os.path.exists(results_dir):
            return []

        results = []

        if task_type:
            task_dir = os.path.join(results_dir, task_type)
            if os.path.exists(task_dir):
                for filename in os.listdir(task_dir):
                    if filename.endswith('.json'):
                        with open(os.path.join(task_dir, filename)) as f:
                            results.append(json.load(f))
        else:
            # Get all task types
            for task_type_dir in os.listdir(results_dir):
                task_path = os.path.join(results_dir, task_type_dir)
                if os.path.isdir(task_path):
                    for filename in os.listdir(task_path):
                        if filename.endswith('.json'):
                            with open(os.path.join(task_path, filename)) as f:
                                results.append(json.load(f))

        return results

result_storage = ResultStorage()
