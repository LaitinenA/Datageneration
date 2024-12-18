import pandas as pd
import random

# Constants
NUM_BAYS = 10
TOTAL_TIMESTEPS = 35040
WINTER_MONTHS = list(range(0, 8640)) + list(range(29184, 35040))  # Winter months based on index

# All probabilities, durations, and power variations are centralized in the dictionary
# No queueing system, bays work independently, charging power for cars and trucks and charging duration are independent.
# The "weights" are probabilities used by python's random.choice. This way any number of different charging powers and durations can be added as long as the weights are decided.
# "power" is the charging power in MW, currently 100 kW and 250 kW for cars / 1 MW and 2 MW for trucks.
# Vehicle arrival is based on random number, duration and power based on random.choice.
PROBABILITIES = {
    "winter_weekday_daytime": {
        "arrival": {"truck": 0.4, "car": 0.25, "none": 0.35},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.3, 0.3], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "winter_weekday_nighttime": {
        "arrival": {"truck": 0.20, "car": 0.10, "none": 0.75},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.3, 0.3], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "winter_weekend_daytime": {
        "arrival": {"truck": 0.15, "car": 0.30, "none": 0.55},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.3, 0.3], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "winter_weekend_nighttime": {
        "arrival": {"truck": 0.10, "car": 0.10, "none": 0.80},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.3, 0.3], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "summer_weekday_daytime": {
        "arrival": {"truck": 0.45, "car": 0.30, "none": 0.25},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.4, 0.2], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "summer_weekday_nighttime": {
        "arrival": {"truck": 0.25, "car": 0.15, "none": 0.60},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.4, 0.2], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "summer_weekend_daytime": {
        "arrival": {"truck": 0.15, "car": 0.40, "none": 0.45},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.4, 0.2], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
    "summer_weekend_nighttime": {
        "arrival": {"truck": 0.10, "car": 0.20, "none": 0.70},
        "truck": {"durations": [1, 3], "weights": [0.3, 0.7], "power": [1.0, 2.0], "power_weights": [0.5, 0.5]},
        "car": {"durations": [1, 2, 3], "weights": [0.4, 0.4, 0.2], "power": [0.1, 0.25], "power_weights": [0.7, 0.3]},
    },
}

# Initialize tracking lists
time_index = []
bay_data = {bay: [] for bay in range(NUM_BAYS)}
total_trucks = []
total_cars = []
total_power_mw = []
timestep_types = []

# Tracking bay availability
bay_timesteps_remaining = [0] * NUM_BAYS
bay_power = [0] * NUM_BAYS

# Main simulation loop
for timestep in range(1, TOTAL_TIMESTEPS + 1):
    is_winter = timestep in WINTER_MONTHS
    is_weekend = (timestep // (24 * 4)) % 7 in [5, 6]
    is_daytime = (timestep % (24 * 4)) in range(7 * 4, 19 * 4)
    season = "winter" if is_winter else "summer"
    day_type = "weekend" if is_weekend else "weekday"
    time_of_day = "daytime" if is_daytime else "nighttime"

    timestep_type = f"{season}_{day_type}_{time_of_day}"
    timestep_types.append(timestep_type)
    probabilities = PROBABILITIES[timestep_type]

    bays = []
    for bay in range(NUM_BAYS):
        if bay_timesteps_remaining[bay] > 0:
            bay_timesteps_remaining[bay] -= 1
            bays.append(bay_data[bay][-1])
        else:
            random_num = random.random()
            if random_num < probabilities["arrival"]["truck"]:
                bays.append(2)
                bay_timesteps_remaining[bay] = random.choices(
                    probabilities["truck"]["durations"], weights=probabilities["truck"]["weights"], k=1
                )[0] - 1
                bay_power[bay] = random.choices(
                    probabilities["truck"]["power"], weights=probabilities["truck"]["power_weights"], k=1
                )[0]
            elif random_num < probabilities["arrival"]["truck"] + probabilities["arrival"]["car"]:
                bays.append(1)
                bay_timesteps_remaining[bay] = random.choices(
                    probabilities["car"]["durations"], weights=probabilities["car"]["weights"], k=1
                )[0] - 1
                bay_power[bay] = random.choices(
                    probabilities["car"]["power"], weights=probabilities["car"]["power_weights"], k=1
                )[0]
            else:
                bays.append(0)
                bay_power[bay] = 0

    time_index.append(timestep)
    for bay in range(NUM_BAYS):
        bay_data[bay].append(bays[bay])
    total_trucks.append(bays.count(2))
    total_cars.append(bays.count(1))
    total_power_mw.append(round(sum(bay_power), 3))

# Convert to DataFrame and Export
data = {
    "time_index": time_index,
    **{f"bay_{b+1}": bay_data[b] for b in range(NUM_BAYS)},
    "total_trucks": total_trucks,
    "total_cars": total_cars,
    "total_power_mw": total_power_mw,
    "timestep_type": timestep_types,
}
df = pd.DataFrame(data)
df.to_excel("ev_charging_datatest2.xlsx", index=False, engine="openpyxl")

# Aggregate results for printing into console
scenario_stats = df.groupby("timestep_type").agg(
    avg_power_mw=("total_power_mw", "mean"),
    avg_trucks=("total_trucks", "mean"),
    avg_cars=("total_cars", "mean"),
)
# Print results to console
print("Average Power and Vehicle Counts by Scenario:")
print(scenario_stats)
