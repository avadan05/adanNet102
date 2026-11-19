
from flask import Flask, render_template, request, jsonify
from netmiko import ConnectHandler

app = Flask(__name__)



ROUTER_HOST = "192.168.10.234"
ROUTER_PORT = 32770

ROUTER_USERNAME = "YOUR_USERNAME"
ROUTER_PASSWORD = "YOUR_PASSWORD"
ROUTER_SECRET = ""

# Automation state
automation_running = False


 

def run_router_commands():

    router = {
        "device_type": "cisco_ios_telnet",
        "host": ROUTER_HOST,
        "port": ROUTER_PORT,
        "username": ROUTER_USERNAME,
        "password": ROUTER_PASSWORD,
        "secret": ROUTER_SECRET,
        "timeout": 15,
        "conn_timeout": 15,
    }

    results = {}

    connection = ConnectHandler(**router)

    try:
        # Enter privileged mode if necessary
        if not connection.check_enable_mode():
            connection.enable()

        commands = [
            "show version",
            "show ip interface brief",
            "show running-config"
        ]

        for command in commands:

            output = connection.send_command(
                command,
                read_timeout=30
            )

            results[command] = output

    finally:
        connection.disconnect()

    return results


# ==================================
# MAIN DASHBOARD
# ==================================

@app.route("/", methods=["GET", "POST"])
def home():

    error = None
    results = {}

    if request.method == "POST":

        try:
            results = run_router_commands()

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        error=error,
        results=results
    )


# ==================================
# AUTOMATION STATUS
# ==================================

@app.route("/api/status")
def status():

    return jsonify({
        "running": automation_running,
        "message": "Backend connected"
    })


# ==================================
# START AUTOMATION
# ==================================

@app.route("/api/automation/start", methods=["POST"])
def start_automation():

    global automation_running

    automation_running = True

    return jsonify({
        "success": True,
        "running": True,
        "message": "Automation started."
    })


# ==================================
# STOP AUTOMATION
# ==================================

@app.route("/api/automation/stop", methods=["POST"])
def stop_automation():

    global automation_running

    automation_running = False

    return jsonify({
        "success": True,
        "running": False,
        "message": "Automation stopped."
    })


# ==================================
# RUN FLASK APPLICATION
# ==================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
