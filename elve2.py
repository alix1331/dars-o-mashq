from typing import List


class Helper02:
    def print(self, s: str):
        print(s, end='')

    def println(self, s: str):
        print(s)


class LiftRequest:
    def __init__(self, start, destination):
        self.start_floor = start
        self.destination_floor = destination

    def get_start_floor(self):
        return self.start_floor

    def get_destination_floor(self):
        return self.destination_floor

    def get_move_direction(self):
        if self.start_floor != self.destination_floor:
            return 'U' if self.start_floor < self.destination_floor else 'D'
        return 'I'

    def __str__(self):
        return f"({self.start_floor}, {self.destination_floor})"


class LiftState:
    def __init__(self, lift):
        self.lift = lift

    def update_floor(self):
        pass

    def update_direction(self):
        pass

    def get_direction(self):
        raise NotImplementedError

    def get_time_to_reach_floor(self, floor, direction):
        raise NotImplementedError


class MovingUpState(LiftState):
    def get_time_to_reach_floor(self, floor, direction):
        current_floor = self.lift.get_current_floor()
        has_stop_opposite = self.lift.has_stop_in_opposite_direction()
        max_up_floor = self.get_max_up_floor()

        if floor > max_up_floor and has_stop_opposite:
            return -1
        if direction == 'U':
            if floor == current_floor:
                return 0
            if floor < current_floor:
                return -1
            return floor - current_floor

        if floor >= max_up_floor:
            return floor - current_floor

        return (max_up_floor - current_floor) + (max_up_floor - floor)

    def get_max_up_floor(self):
        floor = -1
        for req in self.lift.requests:
            floor = max(floor, req.get_start_floor(), req.get_destination_floor())
        return floor

    def update_floor(self):
        max_up_floor = self.get_max_up_floor()
        if self.lift.get_current_floor() < max_up_floor:
            self.lift.set_current_floor(self.lift.get_current_floor() + 1)

    def update_direction(self):
        if self.lift.get_current_floor() >= self.get_max_up_floor():
            self.lift.set_state('D')

    def get_direction(self):
        return 'U'


class MovingDownState(LiftState):
    def get_time_to_reach_floor(self, floor, direction):
        current_floor = self.lift.get_current_floor()
        has_stop_opposite = self.lift.has_stop_in_opposite_direction()
        min_down_floor = self.get_min_down_floor()

        if floor < min_down_floor and has_stop_opposite:
            return -1
        if direction == 'D':
            if floor == current_floor:
                return 0
            if floor > current_floor:
                return -1
            return current_floor - floor

        if floor <= min_down_floor:
            return current_floor - floor

        return (current_floor - min_down_floor) + (floor - min_down_floor)

    def get_min_down_floor(self):
        floor = float('inf')
        for req in self.lift.requests:
            floor = min(floor, req.get_start_floor(), req.get_destination_floor())
        return floor

    def update_floor(self):
        min_down_floor = self.get_min_down_floor()
        if self.lift.get_current_floor() > min_down_floor:
            self.lift.set_current_floor(self.lift.get_current_floor() - 1)

    def update_direction(self):
        if self.lift.get_current_floor() <= self.get_min_down_floor():
            self.lift.set_state('U')

    def get_direction(self):
        return 'D'


class IdleState(LiftState):
    def get_direction(self):
        return 'I'

    def get_time_to_reach_floor(self, floor, direction):
        return abs(floor - self.lift.get_current_floor())


class Lift:
    def __init__(self):
        self.current_floor = 0
        self.requests: List[LiftRequest] = []
        self.moving_up_state = MovingUpState(self)
        self.moving_down_state = MovingDownState(self)
        self.idle_state = IdleState(self)
        self.state = self.idle_state

    def has_stop_in_opposite_direction(self):
        direction = self.state.get_direction()
        if direction == 'I':
            return False
        for req in self.requests:
            if req.get_move_direction() != direction:
                return True
        return False

    def get_time_to_reach_floor(self, floor, direction):
        return self.state.get_time_to_reach_floor(floor, direction)

    def has_stop(self, floor, move_direction):
        for req in self.requests:
            if (req.get_start_floor() == floor or req.get_destination_floor() == floor) and \
                    move_direction == req.get_move_direction():
                return True
        return False

    def count_people(self, floor, direction):
        people = 0
        for req in self.requests:
            if req.get_move_direction() == direction:
                if direction == 'U' and req.get_start_floor() <= floor < req.get_destination_floor():
                    people += 1
                elif direction == 'D' and req.get_start_floor() >= floor > req.get_destination_floor():
                    people += 1
        return people

    def get_move_direction(self):
        return self.state.get_direction()

    def get_current_floor(self):
        return self.current_floor

    def has_space(self, start_floor, destination_floor):
        if start_floor == destination_floor:
            return False
        direction = 'U' if start_floor < destination_floor else 'D'
        if direction == 'U':
            for floor in range(start_floor, destination_floor):
                if self.count_people(floor, direction) >= 10:
                    return False
        else:
            for floor in range(start_floor, destination_floor, -1):
                if self.count_people(floor, direction) >= 10:
                    return False
        return True

    def update_lift_state(self):
        if len(self.requests) == 0 or self.state.get_direction() == 'I':
            self.set_state('I')
            return
        self.state.update_floor()
        self.update_requests()
        if len(self.requests) == 0:
            self.state = self.idle_state
        else:
            self.state.update_direction()

    def update_requests(self):
        direction = self.state.get_direction()
        if direction == 'I':
            return
        new_requests = []
        for req in self.requests:
            if direction == req.get_move_direction():
                passed_dest_up = direction == 'U' and self.current_floor >= req.get_destination_floor()
                passed_dest_down = direction == 'D' and self.current_floor <= req.get_destination_floor()
                if passed_dest_up or passed_dest_down:
                    continue
            new_requests.append(req)
        self.requests = new_requests

    def add_request(self, start, destination):
        self.requests.append(LiftRequest(start, destination))
        if len(self.requests) == 1:
            direction = self.requests[0].get_move_direction()
            if start > self.current_floor:
                direction = 'U'
            elif start < self.current_floor:
                direction = 'D'
            self.set_state(direction)

    def set_state(self, direction):
        if direction == 'U':
            self.state = self.moving_up_state
        elif direction == 'D':
            self.state = self.moving_down_state
        else:
            self.state = self.idle_state

    def set_current_floor(self, current_floor):
        self.current_floor = current_floor


class Solution:
    def __init__(self):
        self.floors = 0
        self.lifts_count = 0
        self.helper = None
        self.lifts: List[Lift] = []

    def init(self, floors, lifts, helper):
        self.floors = floors
        self.lifts_count = lifts
        self.helper = helper
        self.lifts = [Lift() for _ in range(lifts)]
        # helper.println("Lift system initialized ...")

    def request_lift(self, start_floor, destination_floor):
        if start_floor == destination_floor:
            return -1
        lift_id = -1
        time_to_reach_start = 10**6
        direction = 'U' if start_floor < destination_floor else 'D'
        for i in range(self.lifts_count):
            lift = self.lifts[i]
            reach_start = lift.get_time_to_reach_floor(start_floor, direction)
            reach_destination = lift.get_time_to_reach_floor(destination_floor, direction)
            if reach_start < 0 or reach_destination < 0 or reach_start > time_to_reach_start:
                continue
            if not lift.has_space(start_floor, destination_floor):
                continue
            if reach_start < time_to_reach_start:
                lift_id = i
                time_to_reach_start = reach_start

        if 0 <= lift_id < self.lifts_count:
            self.lifts[lift_id].add_request(start_floor, destination_floor)

        return lift_id

    def tick(self):
        for lift in self.lifts:
            lift.update_lift_state()

    def get_lifts_stopping_on_floor(self, floor, move_direction):
        lift_ids = []
        for i, lift in enumerate(self.lifts):
            if lift.has_stop(floor, move_direction):
                lift_ids.append(i)
        return lift_ids

    def get_number_of_people_on_lift(self, lift_id):
        if lift_id < 0 or lift_id >= self.lifts_count:
            return 0
        lift = self.lifts[lift_id]
        return lift.count_people(lift.get_current_floor(), lift.get_move_direction())

    def get_lift_states(self):
        return [f"{lift.get_current_floor()}-{lift.get_move_direction()}" for lift in self.lifts]


# Example usage:
if __name__ == "__main__":
    helper = Helper02()
    system = Solution()
    system.init(40, 2, helper)
    system.request_lift(0, 5)
    for _ in range(6):
        system.tick()
        print(system.get_lift_states())
