from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import json
import asyncio
from typing import Dict, Set, List
from chat_node import ChatNode
import uvicorn

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store active connections, chat nodes, and message tracking
active_connections: Dict[str, WebSocket] = {}
chat_nodes: Dict[str, ChatNode] = {}
last_message_count: Dict[str, int] = {}  # Track number of messages sent to each client
TOTAL_NODES = 3

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{node_id}")
async def websocket_endpoint(websocket: WebSocket, node_id: str):
    await websocket.accept()
    active_connections[node_id] = websocket
    last_message_count[node_id] = 0  # Initialize message count for this client
    
    # Create chat node if it doesn't exist
    if node_id not in chat_nodes:
        chat_nodes[node_id] = ChatNode(node_id, TOTAL_NODES, 5000 + int(node_id))
        chat_nodes[node_id].start()
    
    node = chat_nodes[node_id]
    
    try:
        # Start background task to send updates
        update_task = asyncio.create_task(send_updates(websocket, node, node_id))
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                node.send_message(message_data["content"])
                
    except WebSocketDisconnect:
        active_connections.pop(node_id, None)
        last_message_count.pop(node_id, None)
        update_task.cancel()
    except Exception as e:
        print(f"Error in websocket connection: {e}")
        active_connections.pop(node_id, None)
        last_message_count.pop(node_id, None)
        update_task.cancel()

async def send_updates(websocket: WebSocket, node: ChatNode, node_id: str):
    """Send periodic updates about node state to the websocket client."""
    try:
        while True:
            # Send vector clock update
            await websocket.send_json({
                "type": "vector_clock",
                "clock": node.vector_clock.get_clock()
            })
            
            # Send buffer status
            await websocket.send_json({
                "type": "buffer",
                "count": len(node.message_buffer)
            })
            
            # Send only new messages
            messages = node.get_messages()
            current_count = len(messages)
            if current_count > last_message_count[node_id]:
                # Send only new messages
                for msg in messages[last_message_count[node_id]:]:
                    await websocket.send_json({
                        "type": "message",
                        "sender_id": msg[0],
                        "content": msg[1],
                        "timestamp": node.vector_clock.get_clock()
                    })
                last_message_count[node_id] = current_count
            
            await asyncio.sleep(0.1)  # Update every 100ms
            
    except Exception as e:
        print(f"Error in update task: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 