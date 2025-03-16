from chat_node import ChatNode
import time
import threading
from typing import List
import random

def simulate_network_delay():
    """Simulate random network delay."""
    time.sleep(random.uniform(0.1, 0.5))

def run_chat_simulation():
    # Create three chat nodes
    nodes: List[ChatNode] = []
    for i in range(3):
        node = ChatNode(str(i), 3, 5000 + i)
        nodes.append(node)
        node.start()
    
    # Wait for nodes to connect
    time.sleep(1)
    
    try:
        # Simulate concurrent messages
        threading.Thread(target=lambda: (
            simulate_network_delay(),
            nodes[0].send_message("Hello from Node 0!")
        )).start()
        
        threading.Thread(target=lambda: (
            simulate_network_delay(),
            nodes[1].send_message("Hi from Node 1!")
        )).start()
        
        # Wait for messages to be processed
        time.sleep(2)
        
        # Node 2 sends a message after seeing messages from 0 and 1
        nodes[2].send_message("Hey both!")
        
        # Wait for final message to be processed
        time.sleep(1)
        
        # Print delivered messages for each node
        for i, node in enumerate(nodes):
            print(f"\nNode {i} delivered messages:")
            for sender, content in node.get_messages():
                print(f"From Node {sender}: {content}")
            
    finally:
        # Clean up
        for node in nodes:
            node.stop()

if __name__ == "__main__":
    print("Starting distributed chat simulation...")
    run_chat_simulation() 