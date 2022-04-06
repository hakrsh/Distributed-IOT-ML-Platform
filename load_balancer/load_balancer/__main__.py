from load_balancer.load_balancer import app

if(__name__ == "__main__"):
    app.run(host = "0.0.0.0", port = 9899)
