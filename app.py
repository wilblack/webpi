import os

from tornado import websocket, web, ioloop
import tornado
import json

from sensor_threads import DS18B20Thread


cl = []

class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("www/index.html")

class SocketHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

class ApiHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        timestamp = self.get_argument("timestamp")
        data = {"id": id, "value" : value, "timestamp":timestamp}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @tornado.web.asynchronous
    def post(self):
        pass


settings = {

    "static_path":os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "www", "static")
}
app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/(favicon.ico)', tornado.web.StaticFileHandler, {'path': '../'}),
    (r'/(rest_api_example.png)', tornado.web.StaticFileHandler, {'path': './'}),
    
], **settings)

if __name__ == '__main__':

    # Start taking the temperature
    tsensor = DS18B20Thread(5*60)
    tsensor.start()
    print "Starting app.\nStatic root path: %s" %(settings['static_path'])
    

    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
