import zmq
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from vector_clock import VectorClock
import threading
import queue
import time

@dataclass
class ChatMessage:
    sender_id: str
    content: str
    timestamp: Dict[str, int]
    
class ChatNode:
    def __init__(self, node_id: str, num_nodes: int, port: int):
        """Initialize a chat node.
        
        Args:
            node_id: Unique identifier for this node
            num_nodes: Total number of nodes in the system
            port: Port number for ZMQ communication
        """
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id, num_nodes)
        self.message_buffer: List[ChatMessage] = []
        self.delivered_messages: List[ChatMessage] = []
        self.port = port
        
        # ZMQ setup
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.subscriber = self.context.socket(zmq.SUB)
        
        # Message queue for handling received messages
        self.message_queue = queue.Queue()
        
        # Start message processing thread
        self.running = True
        self.process_thread = threading.Thread(target=self._process_messages)
        self.process_thread.daemon = True
        self.process_thread.start()
    
    def start(self) -> None:
        """Start the chat node."""
        self.publisher.bind(f"tcp://*:{self.port}")
        # Subscribe to all other nodes
        for i in range(self.port - 1000, self.port + 1000):
            if i != self.port:
                self.subscriber.connect(f"tcp://localhost:{i}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # Start receiving messages
        threading.Thread(target=self._receive_messages, daemon=True).start()
    
    def stop(self) -> None:
        """Stop the chat node."""
        self.running = False
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
    
    def send_message(self, content: str) -> None:
        """Send a chat message to all other nodes."""
        self.vector_clock.increment()
        message = ChatMessage(
            sender_id=self.node_id,
            content=content,
            timestamp=self.vector_clock.get_clock()
        )
        
        # Broadcast message
        self.publisher.send_string(json.dumps({
            "sender_id": message.sender_id,
            "content": message.content,
            "timestamp": message.timestamp
        }))
        
        # Deliver message locally
        self.delivered_messages.append(message)
    
    def _receive_messages(self) -> None:
        """Receive messages from other nodes."""
        while self.running:
            try:
                message_str = self.subscriber.recv_string(flags=zmq.NOBLOCK)
                message_data = json.loads(message_str)
                message = ChatMessage(
                    sender_id=message_data["sender_id"],
                    content=message_data["content"],
                    timestamp=message_data["timestamp"]
                )
                self.message_queue.put(message)
            except zmq.ZMQError:
                time.sleep(0.1)
            except Exception as e:
                print(f"Error receiving message: {e}")
    
    def _process_messages(self) -> None:
        """Process received messages ensuring causal ordering."""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1)
                
                # Check if message can be delivered
                while not self._can_deliver_message(message):
                    # Buffer message and wait for dependencies
                    self.message_buffer.append(message)
                    message = self.message_queue.get(timeout=1)
                
                # Deliver message
                self.vector_clock.update(message.timestamp)
                self.delivered_messages.append(message)
                
                # Check buffer for messages that can now be delivered
                self._check_buffer()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
    
    def _can_deliver_message(self, message: ChatMessage) -> bool:
        """Check if a message can be delivered based on vector clock ordering."""
        # Check if we have all causally preceding messages
        for process_id, timestamp in message.timestamp.items():
            if process_id != message.sender_id:
                if self.vector_clock.clock[process_id] < timestamp:
                    return False
        return True
    
    def _check_buffer(self) -> None:
        """Check buffered messages to see if any can be delivered."""
        delivered = []
        for message in self.message_buffer:
            if self._can_deliver_message(message):
                self.vector_clock.update(message.timestamp)
                self.delivered_messages.append(message)
                delivered.append(message)
        
        # Remove delivered messages from buffer
        for message in delivered:
            self.message_buffer.remove(message)
    
    def get_messages(self) -> List[Tuple[str, str]]:
        """Get all delivered messages as (sender, content) tuples."""
        return [(msg.sender_id, msg.content) for msg in self.delivered_messages] 