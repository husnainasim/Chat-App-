# Distributed Chat System with Vector Clocks

A real-time distributed chat application that demonstrates causal ordering and time synchronization in distributed systems. This implementation simulates how modern chat applications (like WhatsApp or Slack) maintain message ordering across multiple nodes.

## 🌟 Features

- Real-time message delivery across distributed nodes
- Causal ordering using Vector Clocks
- Message buffering for out-of-order messages
- Interactive web interface showing system state
- Visual representation of Vector Clock states
- Concurrent message handling
- Network delay simulation

## 🔧 Technology Stack

- **Backend**:
  - Python 3.8+
  - FastAPI (async web framework)
  - ZeroMQ (distributed messaging)
  - Uvicorn (ASGI server)

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)
  - WebSocket for real-time communication

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser
- Terminal/Command Prompt

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd distributed-chat-system
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   - Open your browser and navigate to `http://127.0.0.1:8000`
   - You'll see three chat windows, each representing a distributed node

3. **Send messages**
   - Type a message in any node's input box
   - Press Enter or click Send
   - Observe how messages are ordered across nodes

4. **Observe Vector Clocks**
   - Each message shows its Vector Clock timestamp [x,y,z]
   - Watch how timestamps change as messages are exchanged

## 🏗 Project Structure

```
distributed-chat-system/
├── app.py                 # FastAPI application and WebSocket handlers
├── chat_node.py          # Distributed chat node implementation
├── vector_clock.py       # Vector Clock implementation
├── requirements.txt      # Python dependencies
├── static/
│   └── style.css        # CSS styles for web interface
└── templates/
    └── index.html       # HTML template for web interface
```

## 🔍 Key Components

### Vector Clock Implementation
```python
class VectorClock:
    def __init__(self, process_id: str, num_processes: int):
        self.process_id = process_id
        self.clock = {str(i): 0 for i in range(num_processes)}
```
Maintains logical timestamps for causal ordering of messages.

### Chat Node
```python
class ChatNode:
    def __init__(self, node_id: str, num_nodes: int, port: int):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id, num_nodes)
        self.message_buffer = []
```
Handles message sending, receiving, and buffering.

### Message Ordering
- Messages are delivered only when causally ready
- Out-of-order messages are buffered
- Concurrent messages are handled appropriately

## 📊 Understanding Vector Clock Timestamps

- `[1,0,0]` - First message from Node 0
- `[1,1,0]` - Node 1's message after seeing Node 0's message
- `[1,1,1]` - Node 2's message after seeing messages from Node 0 and 1

## 🎯 Example Scenarios

1. **Simple Message Exchange**
   ```
   Node 0: "Hello" [1,0,0]
   Node 1: "Hi" [1,1,0]
   Node 2: "Hey both!" [1,1,1]
   ```

2. **Concurrent Messages**
   ```
   Node 0: "First" [1,0,0]
   Node 1: "Also first" [0,1,0]
   ```

## 🔬 Testing

To test different scenarios:

1. **Basic Communication**
   - Send messages from different nodes
   - Observe message ordering

2. **Concurrent Messages**
   - Send messages simultaneously from different nodes
   - Watch how the system handles concurrency

3. **Network Delays**
   - Messages are automatically delayed randomly
   - Observe how buffering handles out-of-order messages

## 🛠 Troubleshooting

1. **WebSocket Connection Issues**
   - Check if the server is running
   - Verify the correct WebSocket URL
   - Check browser console for errors

2. **Message Ordering Issues**
   - Verify Vector Clock timestamps
   - Check message buffer status
   - Ensure all nodes are connected

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📚 Further Reading

- [Vector Clocks in Distributed Systems](https://en.wikipedia.org/wiki/Vector_clock)
- [Distributed Systems Concepts](https://www.distributed-systems.net/index.php/books/ds3/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name
- Contact Information

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- ZeroMQ team for the messaging library
- Distributed systems research community 