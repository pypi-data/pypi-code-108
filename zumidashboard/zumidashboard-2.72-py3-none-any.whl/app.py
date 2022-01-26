from zumidashboard import create_app, start_app

app = create_app()

def run():
    start_app(app)

if __name__ == '__main__':
    run()
