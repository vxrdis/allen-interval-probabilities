from live_simulator import app

# Export the underlying Flask server for Gunicorn to use
server = app.server

if __name__ == "__main__":
    app.run_server(debug=False)
