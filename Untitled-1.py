# name_studentID_hotel_california.py
"""
Hotel California Elevator Management System
Python implementation for Data Structures course project.

Demonstrates:
 - Queue (collections.deque) for incoming requests
 - Priority Queue (heapq) as global prioritized request handler
 - Stack (list) for recent served requests
 - Array (list) to represent floors -10..30 and their call buttons
 - Linked List (custom) for each elevator's internal sorted schedule

Elevators: A and B
Floors: -10 .. 30  (41 floors)
"""

from dataclasses import dataclass, field
from collections import deque
import heapq
import time
import itertools
from typing import Optional, List

# ---------- Utilities & Data Structures ----------

def floor_idx(floor: int) -> int:
    """Convert floor number (-10..30) to array index 0..40."""
    return floor + 10

def idx_floor(idx: int) -> int:
    return idx - 10

request_counter = itertools.count()  # tie-breaker for heapq


@dataclass(order=True)
class PrioritizedRequest:
    priority: int
    count: int
    floor: int = field(compare=False)
    direction: Optional[str] = field(compare=False)  # 'up', 'down', or None (inside elevator)
    timestamp: float = field(compare=False, default_factory=time.time)


class LinkedListNode:
    def __init__(self, floor: int):
        self.floor = floor
        self.next: Optional['LinkedListNode'] = None

class SortedLinkedList:
    """
    Sorted linked list of floor stops for an elevator.
    Keeps stops in ascending order (for simplicity).
    When elevator is moving down we will iterate appropriately.
    """
    def __init__(self):
        self.head: Optional[LinkedListNode] = None

    def add(self, floor: int):
        if self.contains(floor):
            return
        node = LinkedListNode(floor)
        if not self.head or floor < self.head.floor:
            node.next = self.head
            self.head = node
            return
        cur = self.head
        while cur.next and cur.next.floor < floor:
            cur = cur.next
        node.next = cur.next
        cur.next = node

    def remove(self, floor: int):
        cur = self.head
        prev = None
        while cur:
            if cur.floor == floor:
                if prev:
                    prev.next = cur.next
                else:
                    self.head = cur.next
                return True
            prev = cur
            cur = cur.next
        return False

    def pop_next_for_direction(self, current_floor: int, direction: str) -> Optional[int]:
        """
        Choose next stop in current direction if available, otherwise None.
        For 'up' choose smallest floor > current_floor, for 'down' choose largest floor < current_floor.
        """
        if direction == 'up':
            cur = self.head
            while cur:
                if cur.floor > current_floor:
                    target = cur.floor
                    self.remove(target)
                    return target
                cur = cur.next
        elif direction == 'down':
            # find largest < current_floor
            cur = self.head
            candidate = None
            while cur:
                if cur.floor < current_floor:
                    candidate = cur.floor
                cur = cur.next
            if candidate is not None:
                self.remove(candidate)
                return candidate
        return None

    def is_empty(self):
        return self.head is None

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.floor
            cur = cur.next

# ---------- Elevator Model ----------

@dataclass
class Elevator:
    name: str
    current_floor: int = 0
    direction: str = 'idle'  # 'up', 'down', 'idle'
    schedule: SortedLinkedList = field(default_factory=SortedLinkedList)

    def step(self):
        """Move one floor in the direction, or become idle."""
        if self.direction == 'idle':
            # determine direction by schedule peek
            if not self.schedule.is_empty():
                # choose nearest scheduled stop
                target = next(iter(self.schedule))  # first node ascending
                if target == self.current_floor:
                    self.schedule.remove(target)
                    return
                self.direction = 'up' if target > self.current_floor else 'down'
            else:
                return

        if self.direction == 'up':
            self.current_floor += 1
        elif self.direction == 'down':
            self.current_floor -= 1

        # check if we reached a scheduled stop in this floor
        removed = self.schedule.remove(self.current_floor)
        if removed:
            print(f"[{self.name}] Stopped at floor {self.current_floor} to serve request.")
            # after serving, decide next direction
            if self.schedule.is_empty():
                self.direction = 'idle'
            else:
                # if there are any stops above remain -> keep up else switch to down
                remaining = list(self.schedule)
                if any(f > self.current_floor for f in remaining):
                    self.direction = 'up'
                elif any(f < self.current_floor for f in remaining):
                    self.direction = 'down'
                else:
                    self.direction = 'idle'

    def add_stop(self, floor: int):
        self.schedule.add(floor)
        if self.direction == 'idle':
            if floor > self.current_floor:
                self.direction = 'up'
            elif floor < self.current_floor:
                self.direction = 'down'
            else:
                # same floor - serve immediately on next simulation tick
                self.schedule.remove(floor)

    def status(self):
        sched = list(self.schedule)
        return f"{self.name}: floor={self.current_floor}, dir={self.direction}, schedule={sched}"

# ---------- System Controller ----------

class ElevatorSystem:
    def __init__(self):
        # floors array representing call button states: None, 'up', 'down', or both as set
        self.floors: List[Optional[set]] = [set() for _ in range(41)]
        self.incoming_fifo = deque()  # raw arrival order (Queue)
        self.global_heap = []  # priority queue of PrioritizedRequest
        self.recent_stack: List[tuple] = []  # stack showing recently served (floor, elevator)
        self.elevators = {
            'A': Elevator('A'),
            'B': Elevator('B')
        }

    def submit_call(self, floor: int, direction: Optional[str] = None):
        """User presses call button on floor (direction optional)"""
        idx = floor_idx(floor)
        if direction:
            self.floors[idx].add(direction)
        else:
            # internal elevator request (no direction)
            self.floors[idx].add('any')
        # push to FIFO
        self.incoming_fifo.append((floor, direction))
        print(f"Call submitted: floor={floor}, dir={direction}")

    def _calc_priority(self, floor: int, direction: Optional[str], elevator: Elevator):
        """
        Compute a priority score for giving this elevator the request.
        Lower score = higher priority in heapq.
        Factors: distance, direction match (penalty if opposite), idle bonus.
        """
        distance = abs(elevator.current_floor - floor)
        penalty = 0
        # if elevator moving and direction mismatch, add penalty
        if elevator.direction in ('up', 'down') and direction is not None:
            if (elevator.direction == 'up' and floor < elevator.current_floor) or \
               (elevator.direction == 'down' and floor > elevator.current_floor):
                penalty += 5
        # idle bonus
        if elevator.direction == 'idle':
            penalty -= 1
        # closer elevator -> lower priority number
        return distance + penalty

    def assign_requests(self):
        """
        Convert FIFO entries into prioritized requests in the global heap.
        Then pop and assign to best elevator.
        """
        # move FIFO to heap with per-elevator-best priority
        while self.incoming_fifo:
            floor, direction = self.incoming_fifo.popleft()
            # decide best elevator by computing priority for each elevator
            best_elev = None
            best_score = None
            for e in self.elevators.values():
                score = self._calc_priority(floor, direction, e)
                if best_score is None or score < best_score:
                    best_score = score
                    best_elev = e
            # push prioritized request with chosen elevator name embedded in timestamp? We'll store elevator suggested
            cnt = next(request_counter)
            # Create a composite priority so heap can store general fairness; but we will use assignment immediately
            pr = PrioritizedRequest(priority=best_score, count=cnt, floor=floor, direction=direction)
            heapq.heappush(self.global_heap, pr)
            print(f"Enqueued prioritized request floor={floor}, dir={direction}, suggested_elevator={best_elev.name}, score={best_score}")

        # pop and assign while heap not empty
        while self.global_heap:
            pr = heapq.heappop(self.global_heap)
            # choose actual elevator again (system dynamic): maybe the other elevator became better
            best_elev = None
            best_score = None
            for e in self.elevators.values():
                score = self._calc_priority(pr.floor, pr.direction, e)
                if best_score is None or score < best_score:
                    best_score = score
                    best_elev = e
            best_elev.add_stop(pr.floor)
            print(f"Assigned floor {pr.floor} to Elevator {best_elev.name} (score {best_score})")

    def step_simulation(self):
        """
        One tick of the simulation: assign requests -> move elevators -> record served floors
        """
        # assign requests from queues
        self.assign_requests()

        # move each elevator one step
        for e in self.elevators.values():
            prev_floor = e.current_floor
            e.step()
            if e.current_floor != prev_floor:
                print(f"[{e.name}] Moved {prev_floor} -> {e.current_floor} (dir {e.direction})")
            # if elevator served a floor (we printed in step), push to recent stack
            # We'll check recent service by seeing if the floor was in the floors array set (call buttons)
            idx = floor_idx(e.current_floor)
            if 'any' in self.floors[idx] or 'up' in self.floors[idx] or 'down' in self.floors[idx]:
                # clear floor calls when elevator reaches
                if self.floors[idx]:
                    served = self.floors[idx].copy()
                    self.floors[idx].clear()
                    self.recent_stack.append((e.current_floor, e.name, served))
                    print(f"[System] Floor {e.current_floor} calls {served} cleared by elevator {e.name}")
                    # keep stack short
                    if len(self.recent_stack) > 20:
                        self.recent_stack.pop(0)

    def print_status(self):
        print("--- System Status ---")
        for e in self.elevators.values():
            print(e.status())
        # show some floor button states
        active_floors = [idx_floor(i) for i, s in enumerate(self.floors) if s]
        print(f"Active floors with calls: {active_floors}")
        print(f"Recent served (top): {self.recent_stack[-5:]}")
        print("---------------------\n")

# ---------- Example usage / Simulation ----------

def sample_scenario():
    system = ElevatorSystem()

    # Example: people at floors calling elevators
    system.submit_call(5, 'down')    # floor 5 presses down
    system.submit_call(-3, 'up')     # underground -3 presses up
    system.submit_call(25, 'down')   # high floor wants to go down
    system.submit_call(0, 'up')      # ground wants up
    system.submit_call(10, None)     # internal request (e.g., someone inside elevator requested floor 10)

    # Run simulation for N ticks
    for tick in range(30):
        print(f"=== Tick {tick} ===")
        system.step_simulation()
        system.print_status()
        time.sleep(0.05)  # small delay for readability in example (remove in unit tests)

if __name__ == "__main__":
    sample_scenario()
