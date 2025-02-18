import os
import dash
from whoop import WhoopClient
from dotenv import load_dotenv
from waitress import serve
from flask import request

# Load environment variables
load_dotenv()

# Fetch Whoop credentials
USERNAME = os.getenv("WHOOP_USERNAME")
PASSWORD = os.getenv("WHOOP_PASSWORD")

# Initialize Dash app
app = dash.Dash(__name__)
# Expose the server
server = app.server

# Metric mapping
METRIC_MAP = {
    "RHR": ("get_recovery_collection", "score.resting_heart_rate"),
    "strain": ("get_cycle_collection", "score.strain"),
    "recovery": ("get_recovery_collection", "score.recovery_score"),
    "sleeptime": ("get_sleep_collection", "score.stage_summary.total_in_bed_time_milli"),
    "sleepperformance": ("get_sleep_collection", "score.sleep_performance_percentage"),
    "hrv": ("get_recovery_collection", "score.hrv_rmssd_milli")
}

@server.route('/whoop', methods=['GET'])
def get_whoop_stat():
    metric = request.args.get('stat')
    date = request.args.get('date')
    
    if metric not in METRIC_MAP:
        return {"error": "Invalid metric"}, 400
    
    try:
        with WhoopClient(USERNAME, PASSWORD) as client:
            api_function, metric_path = METRIC_MAP[metric]
            api_method = getattr(client, api_function)
            data = api_method(start_date=date, end_date=date)

            if not data:
                return {"error": "No data found"}, 404
            
            metric_keys = metric_path.split('.')
            value = data[0]
            for key in metric_keys:
                value = value.get(key)
                if value is None:
                    return {"error": "Metric not found"}, 404
            
            return {"value": value}
    
    except Exception as e:
        return {"error": str(e)}, 500

# Run the server with Waitress
if __name__ == "__main__":
    serve(app.server, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
