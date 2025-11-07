from stem.control import Controller
from flask import Flask, render_template

if __name__ == "__main__":

    app = Flask("TorWeb")
    port = 5000
    host = "127.0.0.1"
    hidden_svc_dir = "E:/web" #change to your desired path

    @app.route('/')
    def index():
        return render_template('index.html')
    
    print('* Getting controller')
    controller = Controller.from_port(address="127.0.0.1", port=9151)
    try:
        controller.authenticate(password="Msft#win123")
        controller.set_options([
            ("HiddenServiceDir", hidden_svc_dir),
            ("HiddenServicePort", "80 %s:%s" % (host, str(port)))
        ])
        svc_name = open(hidden_svc_dir + "/hostname", "r").read().strip()
        print("* Created host: ", svc_name)
    except Exception as e:
        print(e)
    app.run()
