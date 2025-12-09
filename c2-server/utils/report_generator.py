"""
Generate reports from collected data
"""
import json
from datetime import datetime
from typing import List, Dict
from services.result_storage import result_storage


class ReportGenerator:
    """Generate operation reports"""

    @staticmethod
    def generate_port_scan_report(date: str = None) -> str:
        """Generate port scan summary report"""

        results = result_storage.get_results(task_type="port_scan", date=date)

        if not results:
            return "No port scan results found"

        report = []
        report.append("=" * 60)
        report.append("PORT SCAN REPORT")
        report.append(f"Generated: {datetime.now()}")
        report.append(f"Total scans: {len(results)}")
        report.append("=" * 60)
        report.append("")

        # Aggregate results by target
        targets = {}
        for result in results:
            task_result = result.get("result", {})
            target = task_result.get("target", "unknown")

            if target not in targets:
                targets[target] = {
                    "open_ports": set(),
                    "scan_count": 0,
                    "nodes": set()
                }

            targets[target]["scan_count"] += 1
            targets[target]["nodes"].add(result.get("node_id", "unknown")[:8])

            open_ports = task_result.get("open_ports", [])
            for port_info in open_ports:
                if isinstance(port_info, dict):
                    port = port_info.get("port")
                elif isinstance(port_info, int):
                    port = port_info
                else:
                    continue

                if port:
                    targets[target]["open_ports"].add(port)

        # Report per target
        for target, data in targets.items():
            report.append(f"Target: {target}")
            report.append(f"  Scanned by {len(data['nodes'])} nodes")
            report.append(f"  Total scans: {data['scan_count']}")
            report.append(f"  Open ports: {sorted(data['open_ports'])}")
            report.append("")

        return "\n".join(report)

    @staticmethod
    def generate_traffic_gen_report(date: str = None) -> str:
        """Generate traffic generation report"""

        results = result_storage.get_results(task_type="traffic_gen", date=date)

        if not results:
            return "No traffic generation results found"

        report = []
        report.append("=" * 60)
        report.append("TRAFFIC GENERATION REPORT")
        report.append(f"Generated: {datetime.now()}")
        report.append("=" * 60)
        report.append("")

        total_requests = 0
        total_successful = 0
        total_failed = 0
        targets = {}

        for result in results:
            task_result = result.get("result", {})
            target = task_result.get("target_url", "unknown")

            requests = task_result.get("total_requests", 0)
            successful = task_result.get("successful", 0)
            failed = task_result.get("failed", 0)

            total_requests += requests
            total_successful += successful
            total_failed += failed

            if target not in targets:
                targets[target] = {
                    "requests": 0,
                    "successful": 0,
                    "failed": 0,
                    "nodes": 0
                }

            targets[target]["requests"] += requests
            targets[target]["successful"] += successful
            targets[target]["failed"] += failed
            targets[target]["nodes"] += 1

        report.append("OVERALL STATISTICS:")
        report.append(f"  Total requests sent: {total_requests:,}")
        report.append(f"  Successful: {total_successful:,}")
        report.append(f"  Failed: {total_failed:,}")
        report.append(f"  Success rate: {(total_successful/total_requests*100):.2f}%")
        report.append("")

        report.append("PER TARGET:")
        for target, data in targets.items():
            report.append(f"\n  {target}")
            report.append(f"    Nodes involved: {data['nodes']}")
            report.append(f"    Requests: {data['requests']:,}")
            report.append(f"    Successful: {data['successful']:,}")
            report.append(f"    Failed: {data['failed']:,}")

        return "\n".join(report)

    @staticmethod
    def save_report(filename: str, content: str):
        """Save report to file"""
        import os
        os.makedirs("reports", exist_ok=True)

        filepath = os.path.join("reports", filename)
        with open(filepath, 'w') as f:
            f.write(content)

        return filepath


if __name__ == "__main__":
    # Example usage
    gen = ReportGenerator()

    port_report = gen.generate_port_scan_report()
    print(port_report)

    traffic_report = gen.generate_traffic_gen_report()
    print(traffic_report)
