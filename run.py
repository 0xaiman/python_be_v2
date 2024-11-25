from app import create_app

# Initialize app and limiter
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')