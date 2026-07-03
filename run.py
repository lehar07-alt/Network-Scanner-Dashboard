from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True gives us auto-reload on code changes + detailed error pages
    # NEVER leave debug=True in a real production deployment
    app.run(debug=True)