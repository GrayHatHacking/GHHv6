#client.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 4242))
s.send(b'Say something:') # b tag added in python3 to indicate bytes not str
data = s.recv(1024)
s.close()
print('Received', data)
