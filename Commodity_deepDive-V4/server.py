import http.server
import socketserver
import json
import os
import urllib.parse
from datetime import datetime

# Load environment variables from .env if present
env_vars = {
    "PORT": 8085,
    "HOST": "127.0.0.1",
    "DATABASE_FILE": "database.json",
    "APP_TITLE": "Semiconductor Equipment Commodity & Supplier Study Platform"
}

if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

PORT = int(env_vars.get("PORT", 8085))
HOST = env_vars.get("HOST", "127.0.0.1")
DATABASE_FILE = env_vars.get("DATABASE_FILE", "database.json")

def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"commodities": {}, "suppliers": []}

def sort_suppliers(suppliers):
    # Sort suppliers by Region -> Country -> City
    return sorted(suppliers, key=lambda s: (
        s.get("region", "").lower(),
        s.get("country", "").lower(),
        s.get("city", "").lower(),
        s.get("name", "").lower()
    ))

class ChipChainHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path.startswith("/api/"):
            data = load_database()
            suppliers = data.get("suppliers", [])
            sorted_suppliers = sort_suppliers(suppliers)

            if path == "/api/health":
                self.send_json_response({
                    "status": "online",
                    "app": env_vars.get("APP_TITLE"),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "total_suppliers": len(suppliers)
                })
                return

            if path == "/api/commodities":
                self.send_json_response(data.get("commodities", {}))
                return

            if path in ["/api/suppliers", "/api/data"]:
                commodity = query_params.get("commodity", [None])[0]
                region = query_params.get("region", [None])[0]
                country = query_params.get("country", [None])[0]

                filtered = sorted_suppliers

                if commodity and commodity != "All":
                    # Flexible matching for commodity names
                    filtered = [s for s in filtered if commodity.lower() in s.get("commodity", "").lower() or s.get("commodity", "").lower() in commodity.lower()]

                if region and region != "All":
                    filtered = [s for s in filtered if s.get("region", "").lower() == region.lower()]

                if country and country != "All":
                    filtered = [s for s in filtered if s.get("country", "").lower() == country.lower()]

                if path == "/api/data":
                    self.send_json_response({
                        "commodities": data.get("commodities", {}),
                        "suppliers": filtered,
                        "metadata": {
                            "total_suppliers": len(suppliers),
                            "filtered_count": len(filtered),
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    })
                else:
                    self.send_json_response(filtered)
                return

            self.send_error(404, "API endpoint not found")
            return

        # Default static file handling
        return super().do_GET()

    def send_json_response(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        json_bytes = json.dumps(content, indent=2).encode("utf-8")
        self.send_header("Content-Length", str(len(json_bytes)))
        self.end_headers()
        self.wfile.write(json_bytes)

def run_server():
    server_address = (HOST, PORT)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(server_address, ChipChainHTTPRequestHandler)
    print(f"CHIPCHAIN API Server running on http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
