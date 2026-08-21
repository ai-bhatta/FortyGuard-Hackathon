def calculate_heat_score(environmental_data, satellite_data):

    location = environmental_data["locations"][0]
    params = location["parameters"]

    score = 0

    # Temperature
    temp = max(params.get("apparent_temperature_celsius", [0]))

    if temp >= 45:
        score += 30
    elif temp >= 40:
        score += 25
    elif temp >= 35:
        score += 18
    elif temp >= 30:
        score += 10

    # Humidity
    humidity = max(params.get("relative_humidity_percent", [0]))

    if humidity >= 80:
        score += 20
    elif humidity >= 60:
        score += 15
    elif humidity >= 40:
        score += 8

    # Heat Index
    heat_index = max(params.get("heat_index_celsius", [0]))

    if heat_index >= 45:
        score += 20
    elif heat_index >= 35:
        score += 15
    elif heat_index >= 25:
        score += 8

    # Solar Irradiance
    solar = (
        location.get("solar_irradiance", {})
        .get("clear_sky", {})
        .get("ghi", 0)
    )

    if solar >= 900:
        score += 15
    elif solar >= 700:
        score += 10
    elif solar >= 500:
        score += 5

    # Satellite Segmentation
    segmentation = satellite_data.get("segmentation", {})

    vegetation = segmentation.get("vegetation", 0)
    buildings = segmentation.get("building", 0)
    water = segmentation.get("water", 0)

    if vegetation > 40:
        score -= 10
    elif vegetation > 20:
        score -= 5

    if buildings > 40:
        score += 10
    elif buildings > 20:
        score += 5

    if water > 20:
        score -= 5

    # Air Quality
    aqi = params.get("air_quality:idx", [])
    valid = [x for x in aqi if x is not None]

    if valid:
        max_aqi = max(valid)

        if max_aqi > 150:
            score += 10
        elif max_aqi > 100:
            score += 5

    score = max(0, min(score, 100))

    if score < 25:
        risk = "Low"
    elif score < 50:
        risk = "Moderate"
    elif score < 75:
        risk = "High"
    else:
        risk = "Extreme"

    return {
        "score": score,
        "risk": risk,
        "temperature": temp,
        "humidity": humidity,
        "heat_index": heat_index,
        "solar": solar,
        "vegetation": vegetation,
        "buildings": buildings,
        "water": water,
    }