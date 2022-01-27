from Famcy import create_app

app = create_app('test',False)

if __name__ == "__main__":
    app.run()