import argparse, json, random
from .config import Config
from .sensors import PresenceSensor
from .safety import SafetyGate
from .swarm import Swarm, Bot
from .reporting import make_report, write_report

def load_house_map(path: str):
    with open(path) as f:
        return json.load(f)

def occupancy_check_factory(sensor: PresenceSensor, gate: SafetyGate):
    def check(room: str) -> bool:
        occupied = sensor.occupied(room)
        # Gate determines whether operation is allowed; swarm avoids occupied rooms
        return occupied and not gate.allow_operation(occupied)
    return check

def main():
    parser = argparse.ArgumentParser(description="Bug Busters simulation")
    parser.add_argument("--map", required=True, help="Path to house map JSON")
    parser.add_argument("--child-safe", default="true", choices=["true","false"])
    parser.add_argument("--report", default="")
    parser.add_argument("--ticks", type=int, default=150)
    args = parser.parse_args()

    cfg = Config(child_safe=(args.child_safe == "true"))
    house_map = load_house_map(args.map)

    # Occupancy flags per room (demo: kids in living_room)
    room_flags = {room: {"kid": False, "pet": False, "adult": False} for room in house_map.keys()}
    if "living_room" in room_flags:
        room_flags["living_room"]["kid"] = True

    sensor = PresenceSensor(room_flags)
    gate = SafetyGate(child_safe=cfg.child_safe, retreat_on_presence=cfg.retreat_on_presence)
    occ_check = occupancy_check_factory(sensor, gate)

    # Initialize swarm
    rooms = [r for r in house_map.keys() if r != "outside"]
    bots = [Bot(id=i, room=random.choice(rooms)) for i in range(30)]
    swarm = Swarm(bots=bots, exits={"front_door": (0,0)})

    # Baseline coverage
    before = swarm.step(house_map, lambda r: False)

    # Simulation loop
    for _ in range(min(args.ticks, cfg.max_ticks)):
        swarm.step(house_map, occ_check)
        # Periodically “herd” bots toward outside
        for b in swarm.bots:
            neighbors = house_map[b.room].get("neighbors", [])
            if "outside" in neighbors:
                b.room = "outside"

    after = swarm.step(house_map, lambda r: False)

    print("All bots outside:", swarm.all_outside("outside"))
    print("Coverage before:", before)
    print("Coverage after:", after)

    if args.report
