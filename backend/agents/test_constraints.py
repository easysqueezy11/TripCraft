from backend.agents.constraint_agent import create_schedule

attractions = [
    {
        "name": "Mysore Palace",
        "cost": 100,
        "duration": 2,
        "opening": 9,
        "closing": 17
    },
    {
        "name": "Brindavan Gardens",
        "cost": 50,
        "duration": 2,
        "opening": 9,
        "closing": 18
    },
    {
        "name": "Chamundi Hills",
        "cost": 80,
        "duration": 1,
        "opening": 7,
        "closing": 17
    }
]

result = create_schedule(
    attractions,
    days=2,
    budget=1000
)

print("\n===== TRIPCRAFT CSP TEST =====")
print("Status:", result["status"])
print("Schedule:", result["schedule"])

if "total_cost" in result:
    print("Total Cost:", result["total_cost"])

print("==============================")