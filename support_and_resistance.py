# Identify support and resistance levels


def identify_support_resistance(data):
    support_levels = []
    resistance_levels = []

    for i in range(2, len(data) - 2):
        if (
            data["low"][i] < data["low"][i - 1]
            and data["low"][i] < data["low"][i + 1]
            and data["low"][i + 1] < data["low"][i + 2]
            and data["low"][i - 1] < data["low"][i - 2]
        ):
            support_levels.append(data["low"][i])
        if (
            data["high"][i] > data["high"][i - 1]
            and data["high"][i] > data["high"][i + 1]
            and data["high"][i + 1] > data["high"][i + 2]
            and data["high"][i - 1] > data["high"][i - 2]
        ):
            resistance_levels.append(data["high"][i])

    return support_levels, resistance_levels
