from backend import create_app

app = create_app()

# Generate pdf

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9050)

# Activate environment with flask
# source venv/bin/activate

# Run flask server
# python3 -m flask --app server run --host=0.0.0.0 --port=9050
# or 
# python3 server.py

# http request endpoint
# http://192.168.1.103:9050
