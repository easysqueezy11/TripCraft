from constraint import Problem


def create_schedule(attractions, days, budget, daily_hours=8):
    """
    Create a travel schedule using Constraint Satisfaction.

    Each attraction contains:
    name, cost, duration, opening, closing
    """

    problem = Problem()

    if not attractions:
        return {
            "status": "No attractions provided",
            "schedule": {}
        }

    names = [item["name"] for item in attractions]

    if len(names) != len(set(names)):
        return {
            "status": "Duplicate attraction names",
            "schedule": {}
        }

    # Create possible day and starting-time combinations
    for attraction in attractions:

        duration = attraction["duration"]
        opening = attraction["opening"]
        closing = attraction["closing"]

        possible_slots = []

        start = opening

        while start + duration <= closing:
            possible_slots.extend(
                (day, start)
                for day in range(1, days + 1)
            )
            start += 0.5

        if not possible_slots:
            return {
                "status": "No valid visiting time",
                "schedule": {}
            }

        problem.addVariable(
            attraction["name"],
            possible_slots
        )

    # Prevent overlapping visits
    for i in range(len(attractions)):
        for j in range(i + 1, len(attractions)):

            first = attractions[i]
            second = attractions[j]

            def no_overlap(a, b, d1=first["duration"],
                           d2=second["duration"]):

                day1, start1 = a
                day2, start2 = b

                if day1 != day2:
                    return True

                return (
                    start1 + d1 <= start2
                    or start2 + d2 <= start1
                )

            problem.addConstraint(
                no_overlap,
                [first["name"], second["name"]]
            )

    # Check total budget
    costs = {
        item["name"]: item["cost"]
        for item in attractions
    }

    problem.addConstraint(
        lambda *slots: sum(costs[name] for name in names)
        <= budget,
        names
    )

    # Check daily visiting-hour limits
    durations = {
        item["name"]: item["duration"]
        for item in attractions
    }

    for day in range(1, days + 1):

        def check_daily_hours(*slots, target_day=day):

            total = sum(
                durations[name]
                for name, slot in zip(names, slots)
                if slot[0] == target_day
            )

            return total <= daily_hours

        problem.addConstraint(
            check_daily_hours,
            names
        )

    solution = problem.getSolution()

    if solution is None:
        return {
            "status": "No feasible itinerary found",
            "schedule": {}
        }

    # Organize the result day-wise
    schedule = {}

    for name, (day, start) in solution.items():

        schedule.setdefault(day, []).append({
            "attraction": name,
            "start_time": start,
            "duration": durations[name],
            "cost": costs[name]
        })

    for day in schedule:
        schedule[day].sort(
            key=lambda item: item["start_time"]
        )

    return {
        "status": "Schedule generated successfully",
        "schedule": schedule,
        "total_cost": sum(costs.values())
    }