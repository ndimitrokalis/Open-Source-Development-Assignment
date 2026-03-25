from app import startup

app = startup()

if __name__ == "__main__":
    app.run(debug=True)