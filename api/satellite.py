from dotenv import load_dotenv
from fortyguard import FortyGuardClient

load_dotenv()

client = FortyGuardClient()

def get_satellite_segmentation(latitude, longitude):

    response = client.satellite_segmentation(
        latitude=latitude,
        longitude=longitude,
        start_date='2024-07-15',
        start_time='14:00',
        filter_type=1,
        granularity=80,
    )

    return response["result"]