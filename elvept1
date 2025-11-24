#!/usr/bin/env python3
"""
Elevator Simulator (Interactive)
Hotel California: floors -10 .. +30, two elevators (A and B)
Uses: Queue, Priority Queue (heap), Stack, Array, LinkedList
Commands:
  request <floor>   - add request (or just type number)
  undo              - cancel last request (uses stack)
  step              - advance simulation: each elevator serves next target if available
  auto              - run until all queues empty
  status            - print current state
  help              - this help
  exit              - quit
"""

import heapq
from collections import deque

MIN_FLOOR = -10
MAX_FLOOR = 30

# -----------------------------
# Linked List for history log
# -----------------------------
class ListNode:
    def __init__(self, floor):
        self.floor = floor
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    def append(self, floor):
        node = ListNode(floor)
        if not self.head:
            self.head = node
            return
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = node
    def to_list(self):
        out = []
        cur = self.head
        while cur:
            out.append(cur.floor)
            cur = cur.next
        return out

# -----------------------------
# Stack (for undo)
# -----------------------------
class Stack:
    def __init__(self):
        self._data = []
    def push(self, x): self._data.append(x)
    def pop(self):
        return None if not self._data else self._data.pop()
    def is_empty(self): return len(self._data) == 0
    def __len__(self): return len(self._data)

# -----------------------------
# PriorityQueue wrappers
# up: min-heap  (lowest floor on top)
# down: max-heap implemented via negative values
# -----------------------------
class UpPQ:
    def __init__(self):
        self.heap = []
    def push(self, floor):
        heapq.heappush(self.heap, floor)
    def pop(self):
        return heapq.heappop(self.heap) if self.heap else None
    def peek(self):
        return self.heap[0] if self.heap else None
    def empty(self):
        return len(self.heap) == 0
    def to_list(self): return list(self.heap)

class DownPQ:
    def __init__(self):
        self.heap = []
    def push(self, floor):
        heapq.heappush(self.heap, -floor)
    def pop(self):
        return -heapq.heappop(self.heap) if self.heap else None
    def peek(self):
        return -self.heap[0] if self.heap else None
    def empty(self):
        return len(self.heap) == 0
    def to_list(self): return [-x for x in self.heap]

# -----------------------------
# Queue for incoming requests
# -----------------------------
class RequestQueue:
    def __init__(self):
        self.q = deque()
    def push(self, floor): self.q.append(floor)
    def pop(self):
        return self.q.popleft() if self.q else None
    def empty(self): return len(self.q) == 0
    def __len__(self): return len(self.q)
    def to_list(self): return list(self.q)

# -----------------------------
# Elevator structure (each elevator uses up/down PQs and a LinkedList history)
# -----------------------------
class Elevator:
    def __init__(self, name):
        self.name = name
        self.current = 0
        self.direction = 'idle'  # 'up', 'down', 'idle'
        self.up = UpPQ()
        self.down = DownPQ()
        self.history = LinkedList()

    def add_request(self, floor):
        if floor == self.current:
            # immediate service (log it)
            self.history.append(floor)
            return
        if floor > self.current:
            self.up.push(floor)
        else:
            self.down.push(floor)

    def has_pending(self):
        return (not self.up.empty()) or (not self.down.empty())

    def next_target(self):
        # decide next target based on direction and queues
        if self.direction == 'up':
            if not self.up.empty():
                return self.up.peek()
            elif not self.down.empty():
                return self.down.peek()
            else:
                return None
        elif self.direction == 'down':
            if not self.down.empty():
                return self.down.peek()
            elif not self.up.empty():
                return self.up.peek()
            else:
                return None
        else:  # idle
            if not self.up.empty():
                return self.up.peek()
            elif not self.down.empty():
                return self.down.peek()
            else:
                return None

    def move_to_next(self):
        """
        Pop the next target according to direction rules and move elevator there.
        Returns the served floor or None.
        """
        # choose direction if idle
        if self.direction == 'idle':
            # prefer closest direction: if both exist, choose nearest by distance to peek values
            up_p = self.up.peek()
            down_p = self.down.peek()
            if up_p is not None and down_p is not None:
                # compute distances
                if abs(up_p - self.current) <= abs(down_p - self.current):
                    self.direction = 'up'
                else:
                    self.direction = 'down'
            elif up_p is not None:
                self.direction = 'up'
            elif down_p is not None:
                self.direction = 'down'
            else:
                return None  # nothing to do

        if self.direction == 'up':
            if not self.up.empty():
                target = self.up.pop()
                self.current = target
                self.history.append(target)
                # remain 'up' as long as up not empty; else if down has items change dir next time
                if self.up.empty() and not self.down.empty():
                    self.direction = 'down'
                elif self.up.empty():
                    self.direction = 'idle'
                return target
            else:
                # no up requests, try down
                if not self.down.empty():
                    self.direction = 'down'
                    target = self.down.pop()
                    self.current = target
                    self.history.append(target)
                    if not self.down.empty():
                        self.direction = 'down'
                    elif not self.up.empty():
                        self.direction = 'up'
                    else:
                        self.direction = 'idle'
                    return target
                else:
                    self.direction = 'idle'
                    return None

        if self.direction == 'down':
            if not self.down.empty():
                target = self.down.pop()
                self.current = target
                self.history.append(target)
                if self.down.empty() and not self.up.empty():
                    self.direction = 'up'
                elif self.down.empty():
                    self.direction = 'idle'
                return target
            else:
                if not self.up.empty():
                    self.direction = 'up'
                    target = self.up.pop()
                    self.current = target
                    self.history.append(target)
                    if not self.up.empty():
                        self.direction = 'up'
                    elif not self.down.empty():
                        self.direction = 'down'
                    else:
                        self.direction = 'idle'
                    return target
                else:
                    self.direction = 'idle'
                    return None

# -----------------------------
# Assignment logic: which elevator gets a request?
# -----------------------------
def assign_request_to_elevator(floor, elevators):
    """
    elevators: list/array of two Elevator objects [A, B]
    Priority:
      1) Elevator moving in same direction and will pass/request in that direction.
      2) Idle elevator.
      3) Closer elevator (by distance).
    """
    A, B = elevators[0], elevators[1]

    # helper to check if elevator is "suitable"
    def suitable(elev):
        if elev.direction == 'idle':
            return True
        if elev.direction == 'up' and floor >= elev.current:
            return True
        if elev.direction == 'down' and floor <= elev.current:
            return True
        return False

    # 1) same-direction preference
    A_s = suitable(A)
    B_s = suitable(B)
    if A_s and not B_s:
        return A
    if B_s and not A_s:
        return B

    # 2) idle preference
    if A.direction == 'idle' and B.direction != 'idle':
        return A
    if B.direction == 'idle' and A.direction != 'idle':
        return B

    # 3) closer elevator
    distA = abs(A.current - floor)
    distB = abs(B.current - floor)
    if distA <= distB:
        return A
    else:
        return B

# -----------------------------
# Main Simulator
# -----------------------------
def print_status(elevators, req_q, undo_stack):
    for e in elevators:
        up_list = sorted(e.up.to_list())
        down_list = sorted(e.down.to_list(), reverse=True)
        hist = e.history.to_list()
        print(f"Elevator {e.name}: floor={e.current} dir={e.direction} up={up_list} down={down_list} history={hist}")
    print("Incoming Request Queue:", req_q.to_list())
    print("Undo Stack (most recent last):", undo_stack._data)
    print("------")

def run_interactive():
    # Array of elevators (requirement: use array)
    elevators = [Elevator('A'), Elevator('B')]

    # Request queue (FIFO)
    req_q = RequestQueue()

    # Undo stack
    undo_stack = Stack()

    print("Hotel California Elevator Simulator (interactive)")
    print("Floors:", MIN_FLOOR, "to", MAX_FLOOR)
    print("Type 'help' for commands.\n")

    while True:
        cmd = input("> ").strip()
        if cmd == "":
            continue
        parts = cmd.split()
        command = parts[0].lower()

        # --- request <floor> or just number
        if command in ("request",) or (command.lstrip("-").isdigit() and len(parts) == 1):
            if command == "request":
                if len(parts) < 2:
                    print("usage: request <floor>")
                    continue
                try:
                    floor = int(parts[1])
                except:
                    print("invalid floor")
                    continue
            else:
                floor = int(command)

            if floor < MIN_FLOOR or floor > MAX_FLOOR:
                print(f"floor must be between {MIN_FLOOR} and {MAX_FLOOR}")
                continue

            # push to incoming request queue and undo stack
            req_q.push(floor)
            undo_stack.push(('request', floor))
            print(f"Requested floor {floor}. Added to incoming queue.")

            # immediately try to dispatch next request from incoming queue (optional optimization)
            # but we keep requests in queue until 'step' or dispatch now:
            # We'll dispatch immediately here for interactivity:
            next_req = req_q.pop()
            if next_req is not None:
                assigned = assign_request_to_elevator(next_req, elevators)
                assigned.add_request(next_req)
                print(f"Assigned floor {next_req} to Elevator {assigned.name} (current floor {assigned.current}).")
            continue

        # --- undo
        if command == "undo":
            last = undo_stack.pop()
            if not last:
                print("Nothing to undo.")
                continue
            typ, value = last
            if typ == 'request':
                # remove from both elevator queues or from incoming queue if present
                removed = False
                # check incoming queue and remove if present
                try:
                    # remove first occurrence in deque
                    req_q.q.remove(value)
                    removed = True
                except ValueError:
                    pass
                # else remove from elevator queues
                for e in elevators:
                    # up
                    try:
                        e.up.heap.remove(value)
                        heapq.heapify(e.up.heap)
                        removed = True
                    except ValueError:
                        pass
                    # down (in negative form)
                    try:
                        e.down.heap.remove(-value)
                        heapq.heapify(e.down.heap)
                        removed = True
                    except ValueError:
                        pass
                if removed:
                    print(f"Undo: removed request {value}.")
                else:
                    print(f"Undo: request {value} was already being served or not found.")
            else:
                print("Unknown undo type.")
            continue

        # --- status
        if command == "status":
            print_status(elevators, req_q, undo_stack)
            continue

        # --- step: advance each elevator by serving its next target (one served per elevator)
        if command == "step":
            any_served = False
            for e in elevators:
                served = e.move_to_next()
                if served is not None:
                    print(f"Elevator {e.name} served floor {served}.")
                    any_served = True
            if not any_served:
                print("No pending targets to serve.")
            continue

        # --- auto: run until all queues empty
        if command == "auto":
            steps = 0
            while True:
                pending = any(e.has_pending() for e in elevators)
                if not pending:
                    break
                for e in elevators:
                    served = e.move_to_next()
                    if served is not None:
                        print(f"[auto] Elevator {e.name} served {served}.")
                steps += 1
                if steps > 1000:
                    print("Stopping auto (safety).")
                    break
            print("Auto-run finished.")
            continue

        # --- help
        if command == "help":
            print("Commands:")
            print("  request <floor>   - add request (or just type number e.g. 5 or -3)")
            print("  undo              - cancel last request")
            print("  step              - each elevator serves one next target if available")
            print("  auto              - run until all queues empty")
            print("  status            - print current state")
            print("  help              - this text")
            print("  exit              - quit")
            continue

        # --- exit
        if command in ("exit", "quit"):
            print("Exiting simulator.")
            break

        print("Unknown command. Type 'help' for commands.")

if __name__ == "__main__":
    run_interactive()
