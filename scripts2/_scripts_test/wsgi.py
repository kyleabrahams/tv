# uwsgi --socket 127.0.0.1:8000 --wsgi-file wsgi.py --callable application --master --processes 4 --threads 2


def application(environ, start_response):
    status = "200 OK"
    headers = [("Content-Type", "text/html")]
    
    # Run the script and capture output
    import subprocess
    result = subprocess.run(
        ["python3", "/Users/kyleabrahams/Documents/GitHub/tv/scripts/merge_epg-test.py"],
        capture_output=True,
        text=True
    )
    
    response_body = result.stdout if result.stdout else "Error running script."
    
    start_response(status, headers)
    return [response_body.encode()]
