import streamlit as st
import folium
from streamlit_folium import st_folium

from backend.algorithms.search import (
    TRAVEL_GRAPH,
    bfs,
    dfs,
    ucs,
    astar,
    calculate_cost
)

from backend.agents.constraint_agent import create_schedule


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="TripCraft | AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #17466d;
}
.stButton>button {
    background-color: #176b87;
    color: white;
    border-radius: 8px;
    height: 45px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.title("✈️ TripCraft")
st.subheader("Travel Itinerary Planning Multi-Agent System")

st.write(
    "Plan smarter journeys with search algorithms, "
    "budget constraints and intelligent itinerary generation."
)

st.divider()


# ---------------- LOCATION DATA ----------------

locations = {
    "Bangalore": [12.9716, 77.5946],
    "Mysore": [12.2958, 76.6394],
    "Coorg": [12.3375, 75.8069],
    "Chikmagalur": [13.3161, 75.7720],
    "Ooty": [11.4064, 76.6932]
}


# ---------------- ATTRACTION DATABASE ----------------

attraction_data = {
    "Mysore": [
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
    ],

    "Coorg": [
        {
            "name": "Abbey Falls",
            "cost": 50,
            "duration": 2,
            "opening": 9,
            "closing": 17
        },
        {
            "name": "Raja's Seat",
            "cost": 30,
            "duration": 1,
            "opening": 9,
            "closing": 18
        },
        {
            "name": "Dubare Elephant Camp",
            "cost": 100,
            "duration": 2,
            "opening": 9,
            "closing": 17
        }
    ],

    "Chikmagalur": [
        {
            "name": "Mullayanagiri",
            "cost": 50,
            "duration": 2,
            "opening": 7,
            "closing": 17
        },
        {
            "name": "Baba Budangiri",
            "cost": 50,
            "duration": 2,
            "opening": 8,
            "closing": 17
        },
        {
            "name": "Jhari Falls",
            "cost": 100,
            "duration": 2,
            "opening": 9,
            "closing": 17
        }
    ],

    "Ooty": [
        {
            "name": "Botanical Garden",
            "cost": 50,
            "duration": 2,
            "opening": 8,
            "closing": 18
        },
        {
            "name": "Ooty Lake",
            "cost": 30,
            "duration": 1,
            "opening": 9,
            "closing": 18
        },
        {
            "name": "Doddabetta Peak",
            "cost": 50,
            "duration": 2,
            "opening": 8,
            "closing": 17
        }
    ],

    "Bangalore": [
        {
            "name": "Lalbagh Botanical Garden",
            "cost": 50,
            "duration": 2,
            "opening": 6,
            "closing": 18
        },
        {
            "name": "Cubbon Park",
            "cost": 0,
            "duration": 1,
            "opening": 6,
            "closing": 18
        },
        {
            "name": "Bangalore Palace",
            "cost": 250,
            "duration": 2,
            "opening": 10,
            "closing": 17
        }
    ]
}


# ---------------- TIME FORMATTER ----------------

def format_time(value):
    hour = int(value)
    minutes = int(round((value - hour) * 60))

    suffix = "AM" if hour < 12 else "PM"
    display_hour = hour % 12

    if display_hour == 0:
        display_hour = 12

    return f"{display_hour}:{minutes:02d} {suffix}"


# ---------------- USER INPUT ----------------

st.header("1. Your Travel Preferences")

col1, col2 = st.columns(2)

with col1:

    start = st.selectbox(
        "Starting location",
        list(TRAVEL_GRAPH.keys())
    )

    budget = st.number_input(
        "Total budget (₹)",
        min_value=1000,
        max_value=1000000,
        value=15000,
        step=1000
    )

    days = st.number_input(
        "Number of travel days",
        min_value=1,
        max_value=28,
        value=3
    )

with col2:

    possible_destinations = [
        city for city in TRAVEL_GRAPH
        if city != start
    ]

    destination = st.selectbox(
        "Destination",
        possible_destinations
    )

    algorithm = st.selectbox(
        "Route search algorithm",
        ["A*", "BFS", "DFS", "Uniform Cost Search"]
    )

    interest = st.selectbox(
        "Travel interest",
        ["Nature", "Adventure", "Culture", "Sightseeing"]
    )


# ---------------- ROUTE PLANNING ----------------

st.divider()
st.header("2. Generate Your Travel Plan")

if st.button("Generate My Itinerary"):

    if algorithm == "BFS":

        route = bfs(TRAVEL_GRAPH, start, destination)
        distance = calculate_cost(TRAVEL_GRAPH, route)

    elif algorithm == "DFS":

        route = dfs(TRAVEL_GRAPH, start, destination)
        distance = calculate_cost(TRAVEL_GRAPH, route)

    elif algorithm == "Uniform Cost Search":

        route, distance = ucs(
            TRAVEL_GRAPH, start, destination
        )

    else:

        heuristic = {
            city: 0 for city in TRAVEL_GRAPH
        }

        route, distance = astar(
            TRAVEL_GRAPH,
            start,
            destination,
            heuristic
        )

    if not route:
        st.error("No route found.")
        st.stop()

    # ---------------- BASE BUDGET ----------------

    transport_cost = distance * 12
    accommodation = days * 1500
    food_cost = days * 700

    base_cost = (
        transport_cost + accommodation + food_cost
    )

    # ---------------- CSP AGENT ----------------

    attractions = attraction_data.get(destination, [])

    remaining_budget = max(0, budget - base_cost)

    csp_result = create_schedule(
        attractions,
        days=int(days),
        budget=remaining_budget,
        daily_hours=8
    )

    attraction_cost = csp_result.get("total_cost", 0)

    total_cost = base_cost + attraction_cost

    # ---------------- SAVE RESULTS ----------------

    st.session_state["trip"] = {
        "route": route,
        "distance": distance,
        "transport": transport_cost,
        "accommodation": accommodation,
        "food": food_cost,
        "attraction_cost": attraction_cost,
        "total": total_cost,
        "days": int(days),
        "budget": budget,
        "algorithm": algorithm,
        "interest": interest,
        "csp": csp_result
    }


# ---------------- DISPLAY RESULTS ----------------

if "trip" in st.session_state:

    trip = st.session_state["trip"]

    st.divider()
    st.header("3. Your Travel Itinerary")

    if trip["total"] <= trip["budget"]:

        st.success(
            "Your estimated trip cost is within budget!"
        )

    else:

        st.warning(
            "Your estimated trip cost exceeds your budget."
        )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Distance",
        f"{trip['distance']} km"
    )

    c2.metric(
        "Estimated Cost",
        f"₹{trip['total']:,.0f}"
    )

    c3.metric(
        "Travel Days",
        trip["days"]
    )

    # ---------------- OPTIMIZED ROUTE ----------------

    st.subheader("Optimized Route")

    route = trip["route"]

    st.write(" → ".join(route))

    # ---------------- BUDGET BREAKDOWN ----------------

    st.subheader("Budget Breakdown")

    st.write(f"🚗 Transport: ₹{trip['transport']:,.0f}")
    st.write(f"🏨 Accommodation: ₹{trip['accommodation']:,.0f}")
    st.write(f"🍽️ Food: ₹{trip['food']:,.0f}")
    st.write(
        f"🎟️ Attractions: ₹{trip['attraction_cost']:,.0f}"
    )

    st.write(
        f"**Total estimated expense: ₹{trip['total']:,.0f}**"
    )

    # ---------------- CSP SCHEDULE ----------------

    st.divider()

    st.header("4. AI Constraint-Based Scheduling")

    st.write(
        "The Constraint Satisfaction Agent schedules "
        "attractions using visiting hours, daily time "
        "limits and budget constraints."
    )

    csp = trip["csp"]

    if csp["status"] == "Schedule generated successfully":

        st.success("Feasible itinerary generated by CSP Agent!")

        for day, activities in sorted(
            csp["schedule"].items()
        ):

            with st.expander(
                f"Day {day} - Attraction Schedule",
                expanded=True
            ):

                for activity in activities:

                    start_time = activity["start_time"]
                    end_time = (
                        start_time + activity["duration"]
                    )

                    st.markdown(
                        f"""
                        **📍 {activity['attraction']}**

                        - Start: {format_time(start_time)}
                        - End: {format_time(end_time)}
                        - Duration: {activity['duration']} hours
                        - Entry cost: ₹{activity['cost']}
                        """
                    )

        st.metric(
            "Total Attraction Expenses",
            f"₹{csp['total_cost']:,.0f}"
        )

    else:

        st.error(
            "No feasible attraction schedule found. "
            "Try increasing your budget or travel days."
        )

        st.caption(f"CSP status: {csp['status']}")

    # ---------------- DAY-WISE TRAVEL SCHEDULE ----------------

    st.divider()

    st.subheader("5. Day-wise Travel Schedule")

    for day in range(trip["days"]):

        index = min(day, len(route) - 1)

        with st.expander(
            f"Travel Day {day + 1}",
            expanded=True
        ):

            if day == 0:

                st.write(
                    f"📍 Start your journey from {route[0]}."
                )

            else:

                st.write(
                    f"📍 Continue your journey towards {route[index]}."
                )

            if day == trip["days"] - 1:

                st.write(
                    f"🏁 Complete your trip at {route[-1]}."
                )

            else:

                st.write(
                    "Explore the destination and nearby attractions."
                )

            st.write(f"Interest: {trip['interest']}")

    # ---------------- INTERACTIVE MAP ----------------

    st.divider()

    st.subheader("6. Travel Route Map")

    map_start = locations.get(start, locations["Bangalore"])

    travel_map = folium.Map(
        location=map_start,
        zoom_start=7
    )

    route_coordinates = [
        locations[city]
        for city in route
        if city in locations
    ]

    for city in route:

        if city in locations:

            folium.Marker(
                locations[city],
                tooltip=city,
                popup=city
            ).add_to(travel_map)

    if route_coordinates:

        folium.PolyLine(
            route_coordinates,
            color="blue",
            weight=4
        ).add_to(travel_map)

    st_folium(
        travel_map,
        width=None,
        height=450
    )

    # ---------------- AI SEARCH INFORMATION ----------------

    st.divider()

    st.subheader("7. AI Search Information")

    st.write(
        f"Selected algorithm: {trip['algorithm']}"
    )

    st.write(
        f"Generated route: {' → '.join(route)}"
    )

    st.write(
        f"Total route distance: {trip['distance']} km"
    )

    st.write(
        "Constraint Agent: "
        + trip["csp"]["status"]
    )

    st.caption(
        "TripCraft prototype: sample route distances, "
        "illustrative expenses and predefined attraction data. "
        "Opening hours and costs should be verified before travel."
    )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "TripCraft | Travel Itinerary Planning Multi-Agent System"
)