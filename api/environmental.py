from dotenv import load_dotenv
from fortyguard import FortyGuardClient

load_dotenv()

client = FortyGuardClient()

def get_environmental_data(latitude, longitude):

    response = client.environmental_parameters(
        latitude=latitude,
        longitude=longitude,
        temperature=8.47,
        start_date='2022-06-02',
        start_time='00:00',
        end_date='2022-06-02',
        end_time='15:00',
        filter_type=2
    )

    return response["result"]


