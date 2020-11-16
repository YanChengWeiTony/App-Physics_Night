from twisted.internet import protocol, reactor

transports = set()

class Chat(protocol.Protocol):
    def dataReceived(self, data):
        print data
        print self.transport
        transports.add(self.transport)
        print transports
        
        if ':' not in data:
            return
        user, msg = data.split(':', 1)
        
        for t in transports:
            if t is not self.transport:
                t.write('[b][color={}]{}:[/color][/b] {}'.format(self.color, user,esc_markup(msg)))
                #t.write('{0} says: {1}'.format(user, msg))

class ChatFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Chat()

reactor.listenTCP(9096, ChatFactory())
reactor.run()
