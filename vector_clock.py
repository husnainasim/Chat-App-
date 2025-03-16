from typing import Dict, List
import copy

class VectorClock:
    def __init__(self, process_id: str, num_processes: int):
        """Initialize a vector clock for a process.
        
        Args:
            process_id: Unique identifier for this process
            num_processes: Total number of processes in the system
        """
        self.process_id = process_id
        self.clock: Dict[str, int] = {str(i): 0 for i in range(num_processes)}
        
    def increment(self) -> None:
        """Increment the local clock value for this process."""
        self.clock[self.process_id] += 1
        
    def update(self, other_clock: Dict[str, int]) -> None:
        """Update this vector clock based on received clock.
        
        Takes the component-wise maximum of the two clocks.
        """
        for process_id in self.clock:
            self.clock[process_id] = max(
                self.clock[process_id],
                other_clock.get(process_id, 0)
            )
            
    def is_concurrent_with(self, other_clock: Dict[str, int]) -> bool:
        """Check if this clock is concurrent with another clock."""
        return not (self.happens_before(other_clock) or 
                   self.happens_after(other_clock))
    
    def happens_before(self, other_clock: Dict[str, int]) -> bool:
        """Check if this clock happens before another clock."""
        at_least_one_less = False
        for process_id in self.clock:
            if self.clock[process_id] > other_clock.get(process_id, 0):
                return False
            if self.clock[process_id] < other_clock.get(process_id, 0):
                at_least_one_less = True
        return at_least_one_less
    
    def happens_after(self, other_clock: Dict[str, int]) -> bool:
        """Check if this clock happens after another clock."""
        at_least_one_more = False
        for process_id in self.clock:
            if self.clock[process_id] < other_clock.get(process_id, 0):
                return False
            if self.clock[process_id] > other_clock.get(process_id, 0):
                at_least_one_more = True
        return at_least_one_more
    
    def get_clock(self) -> Dict[str, int]:
        """Get a copy of the current clock values."""
        return copy.deepcopy(self.clock)
    
    def __str__(self) -> str:
        return f"VC[{self.process_id}]={self.clock}" 