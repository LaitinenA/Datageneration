import pandas as pd
import random

# Constants
NUM_BAYS = 10
TOTAL_TIMESTEPS = 35040
WINTER_MONTHS = list(range(0, 8640)) + list(range(29184, 35040))  # Winter months based on index
TRUCK_POWER = 2.2  # MW
CAR_POWER = 0.22  # MW
TRUCK_DURATION_PROBABILITIES = [1, 3]  # 15 minutes (1 timestep) or 45 minutes (3 timesteps)
TRUCK_DURATION_WEIGHTS = [0.3, 0.7]
CAR_DURATION_PROBABILITIES = [1, 2, 3]  # 15, 30, or 45 minutes
CAR_DURATION_WEIGHTS = [0.4, 0.4, 0.2]
NUM_ARRIVAL_CHECKS = 10  # Number of arrival checks per timestep

# Initialize lists for tracking data
time_index = []
bay_data = {bay: [] for bay in range(NUM_BAYS)}
total_trucks = []
total_cars = []
total_power_mw = []
timestep_types = []

# Tracking bay availability
bay_timesteps_remaining = [0] * NUM_BAYS  # Tracks how many timesteps each bay remains occupied
vehicle_queue = []  # FCFS queue, stores tuples of (vehicle_type, duration)

# Main data generation
for timestep in range(1, TOTAL_TIMESTEPS + 1):
    is_winter = timestep in WINTER_MONTHS
    is_weekend = (timestep // (24 * 4)) % 7 in [5, 6]  # Sat, Sun
    is_daytime = (timestep % (24 * 4)) in range(7 * 4, 19 * 4)  # 7:00 - 19:00
    season = "winter" if is_winter else "summer"
    day_type = "weekend" if is_weekend else "weekday"
    time_of_day = "daytime" if is_daytime else "nighttime"

    timestep_type = f"{season}-{day_type}-{time_of_day}"
    timestep_types.append(timestep_type)

    # Arrival probabilities
    truck_prob = 0.1 if time_of_day == "nighttime" else 0.2
    car_prob = 0.2 if time_of_day == "nighttime" else 0.3

    if season == "summer":
        car_prob *= 1.3
    elif season == "winter":
        car_prob *= 0.8

    # Generate multiple arrival checks per timestep
    for _ in range(NUM_ARRIVAL_CHECKS):
        if random.random() < truck_prob:
            vehicle_queue.append(("truck", random.choices(
                TRUCK_DURATION_PROBABILITIES, weights=TRUCK_DURATION_WEIGHTS, k=1
            )[0]))
        if random.random() < car_prob:
            vehicle_queue.append(("car", random.choices(
                CAR_DURATION_PROBABILITIES, weights=CAR_DURATION_WEIGHTS, k=1
            )[0]))

    # Simulate bays with FCFS logic
    bays = []
    for bay in range(NUM_BAYS):
        if bay_timesteps_remaining[bay] > 0:
            # Bay is occupied; decrement remaining time
            bay_timesteps_remaining[bay] -= 1
            bays.append(bay_data[bay][-1])  # Keep the same vehicle type as previous timestep
        elif vehicle_queue:
            # Bay is free and queue has vehicles; assign next vehicle
            vehicle, duration = vehicle_queue.pop(0)
            bays.append(2 if vehicle == "truck" else 1)
            bay_timesteps_remaining[bay] = duration - 1
        else:
            bays.append(0)  # Bay is empty

    # Record data
    time_index.append(timestep)
    for bay in range(NUM_BAYS):
        bay_data[bay].append(bays[bay])
    total_trucks.append(bays.count(2))  # Correctly count trucks as `2`
    total_cars.append(bays.count(1))  # Correctly count cars as `1`
    total_power_mw.append(round(bays.count(2) * TRUCK_POWER + bays.count(1) * CAR_POWER, 3))

# Prepare data for analysis and output
data = {
    "time_index": time_index,
    **{f"bay_{b+1}": bay_data[b] for b in range(NUM_BAYS)},
    "total_trucks": total_trucks,
    "total_cars": total_cars,
    "total_power_mw": total_power_mw,
    "timestep_type": timestep_types,
}

df = pd.DataFrame(data)

# Function to calculate average power for specific categories
def calculate_average_power(df, season, day_type, time_of_day):
    condition = df["timestep_type"].str.contains(f"{season}-{day_type}-{time_of_day}")
    return round(df.loc[condition, "total_power_mw"].mean(), 3)

# Calculate average power for all combinations
average_powers = {
    "winter_weekday_daytime": calculate_average_power(df, "winter", "weekday", "daytime"),
    "winter_weekday_nighttime": calculate_average_power(df, "winter", "weekday", "nighttime"),
    "winter_weekend_daytime": calculate_average_power(df, "winter", "weekend", "daytime"),
    "winter_weekend_nighttime": calculate_average_power(df, "winter", "weekend", "nighttime"),
    "summer_weekday_daytime": calculate_average_power(df, "summer", "weekday", "daytime"),
    "summer_weekday_nighttime": calculate_average_power(df, "summer", "weekday", "nighttime"),
    "summer_weekend_daytime": calculate_average_power(df, "summer", "weekend", "daytime"),
    "summer_weekend_nighttime": calculate_average_power(df, "summer", "weekend", "nighttime"),
}

# Print averages for reference
print("Average Power Consumption (MW):")
for category, avg_power in average_powers.items():
    print(f"{category}: {avg_power} MW")

# Export data to Excel
output_file = "ev_charging_data_fcfs_with_more_arrivals.xlsx"
df.to_excel(output_file, index=False, engine="openpyxl")
print(f"Data exported to {output_file}")
