import socket
import select



class Chatroom:
    def __init__(self):
        self.usernames = {}
        self.name = ''
        
    def login(self,name, address):
        if name in self.usernames:
            return 'Username already in use, try another.', address
            
        else:
            return self.addUser(name, address)

    def checkInput(self, msg, address):
        
        commandList = ['login', 'list', 'sendto', 'logout', 'exit']
        notInList = 'Invalid command.'
        msg = msg.split()
        
        if msg[0] not in commandList:
            return 'Invalid command.', address
        else:
            if msg[0] == commandList[0]:
                return self.login(msg[1], address)
            
            elif msg[0] == commandList[1]:
                return self.list(address)
            
            elif msg[0] == commandList[2]:
                msg.pop(0)
                reciever = msg.pop(0)
                msg = ' '.join(msg)
                return self.sendTo(reciever,msg)
            elif msg[0] == commandList[3]:
                return self.logout(address)
            elif msg[0] == commandList[4]:
                return self.exit(address)

    def exit(self, address):
        return address
                
    def list(self, address):
        if len([*self.usernames]) == 0:
            return 'There is noone in the server.', address
        else:
            return str([*self.usernames]) + ' is in the server.', address

    def sendTo(self, name, msg):
        return msg, self.usernames[name]

    def logout(self, address):
        self.usernames= {k:v for k, v in self.usernames.items() if v != address}
        return 'Logout successful!', address
    
    def addUser(self,name, address):
        self.usernames[name] = address
        return 'You are connected, ' + name + ' is in the server.', address
        

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 8822))
#sock.listen(5)
# lists of sockets to watch for input and output events
ins = [sock]
ous = []
# mapping socket -> data to send on that socket when feasible
data = {}
# mapping socket -> (host, port) on which the client is running
adrs = {}

#SOCKET_LIST.append(sock)

try:
    print('d')
    room = Chatroom()
    self = None
    while True:
        i, o, e = select.select(ins, ous, [])  # no excepts nor timeout
        for x in i:
            if x is sock:
                # input event on sock means client trying to connect
                newSocket, address = sock.accept(  )
                print ("Connected from", address)
                
                ins.append(newSocket)
                temp = adrs
                adrs = list(temp)
                adrs.append(address)
                adrs = tuple(adrs)
                #adrs[newSocket] = address
                print('a')
            
            else:
                # other input events mean data arrived, or disconnections
                newdata = x.recv(8192)

                if newdata:
                    # data arrived, prepare and queue the response to it
                    print ("%d bytes from %s" % (len(newdata), adrs))
                    print("Received: ", newdata.decode('utf-8'))
                    command = room.checkInput(newdata.decode('utf-8'), adrs)
                    if len(command) > 1:
                        adrs = command[1]
                        command = command[0] 
                    data[x] = data.get(x, b'') + command.encode('utf-8')
                    
                    if x not in ous: ous.append(x)
                else:
                    # a disconnect, give a message and clean up
                    print ("disconnected from", adrs)
                    del adrs[x]
                    try: ous.remove(x)
                    except ValueError: pass
                    x.close(  )

        
        for x in o:
            # output events always mean we can send some data
            tosend = data.get(x)
            if tosend:
                nsent = x.send(tosend)
                #tosend = Chatroom().checkInput(newdata.decode('utf-8'))
                
                print ("%d bytes to %s" % (nsent, adrs))
                # remember data still to be sent, if any
                tosend = tosend[nsent:]
            if tosend: 
                print ("%d bytes remain for %s" % (len(tosend), adrs))
                data[x] = tosend
            else:
                try: del data[x]
                except KeyError: pass
                ous.remove(x)
                print("No data currently remain for", adrs)
finally:
    sock.close(  )
