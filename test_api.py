from api.environmental import get_environmental_data
from api.satellite import get_satellite_segmentation
from utils.heat_score import calculate_heat_score

# Test coordinates (Abu Dhabi)
latitude = 24.4539
longitude = 54.3773

print("========== Industrial Climate Intelligence ==========\n")

# -------------------------------
# Environmental API
# -------------------------------
print("Getting environmental data...")

environmental_data = get_environmental_data(latitude, longitude)

print("✓ Environmental data received.")

# -------------------------------
# Satellite API
# -------------------------------
print("\nGetting satellite segmentation...")

satellite_data = get_satellite_segmentation(latitude, longitude)

print("✓ Satellite data received.")

# -------------------------------
# Heat Risk Score
# -------------------------------
print("\nCalculating Heat Risk Score...")

result = calculate_heat_score(
    environmental_data,
    satellite_data
)
print("\n========== INDUSTRIAL CLIMATE REPORT ==========\n")

print("Heat Risk Score :", result["score"])
print("Risk Level      :", result["risk"])

print()

print("Maximum Apparent Temperature :", result["temperature"], "°C")
print("Maximum Humidity             :", result["humidity"], "%")
print("Heat Index                  :", result["heat_index"], "°C")
print("Solar Irradiance            :", result["solar"], "W/m²")


print("\nEnvironmental Parameters Available:")

location = environmental_data["locations"][0]
params = location["parameters"]

print("Maximum Apparent Temperature:",
      max(params["apparent_temperature_celsius"]), "°C")

print("Maximum Relative Humidity:",
      max(params["relative_humidity_percent"]), "%")

print("Maximum Heat Index:",
      max(params["heat_index_celsius"]), "°C")

print("\nSatellite Information:")

print("Coordinates:",
      satellite_data["coordinates"])

print("Image Year:",
      satellite_data["image_year"])

print("\nSegmentation Classes:")

for key in satellite_data["segmentation"].keys():
    print("-", key)

print("\n====================================")