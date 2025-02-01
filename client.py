import tkinter
import socket
import ssl
import _thread
import sys

i = 3
client = 0
start = True
emoji_window = None

def openEmojiPicker():
    global emoji_window
    if emoji_window is not None:
        emoji_window.destroy()
        emoji_window = None
    else:
        emoji_window = tkinter.Toplevel(window)
        emoji_window.title("Emoji Picker")

        def selectEmoji(emoji_code):
            global emoji_window
            txt.insert(tkinter.END, emoji_code)
            emoji_window.destroy()
            emoji_window = None

        emojis = ["😊", "😂", "😍", "😎", "😜", "😄", "😉", "😋", "😘", "😇",
                  "👍", "👌", "🙌", "💪", "🔥", "❤️", "🎉", "🌟", "💯", "✨"]

        for i, emoji_code in enumerate(emojis):
            button = tkinter.Button(emoji_window, text=emoji_code, command=lambda emoji_code=emoji_code: selectEmoji(emoji_code))
            button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

def sendMessage(event=None):
    msg = txt.get()
    client.send(msg.encode('utf-8'))
    txt.delete(0, tkinter.END)
    return 'break'

def socketCreation():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.load_verify_locations("./server.pem")

    c = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname='192.168.126.145')
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    host = '10.1.0.233'
    port = 50000

    c.connect((host, port))
    global client
    client = c
    
    # Rest of the code remains the same
    global name
    name = input("Enter your alias name: ")
    c.send(name.encode('utf-8'))
    send = tkinter.Button(window, text="Send", command=sendMessage, bg='#72dc4d', fg='black')
    send.grid(column=2, row=2, padx=5, pady=15, sticky='e')
    emoji_btn = tkinter.Button(window, text="Emoji", command=openEmojiPicker, bg='#72dc4d', fg='black')
    emoji_btn.grid(column=1, row=2, padx=5, pady=15)
    _thread.start_new_thread(recievingMessage, (c,))

def recievingMessage(c):
    global i
    while True:
        msg = c.recv(2048).decode('utf-8')
        if not msg:
            sys.exit(0)
        global start
        if start:
            start = False
            window.title(msg)
            continue
        msglbl = tkinter.Label(window, text=msg, relief="groove", bg='#411562', fg='white', font=("Arial", 12))
        msglbl.grid(columnspan=2, column=0, row=i, padx=5, pady=2)
        i += 1

def connectNewClient(c):
    global aliases
    name = c.recv(2048).decode('utf-8')
    aliases.append(name)
    c.send(('Welcome, ' + name + '! You are client ' + str(len(aliases))).encode('utf-8'))
    print(name + ' has joined the chat room')
    while True:
        msg = c.recv(2048)
        num = aliases.index(name) + 1
        msg = str(num) + ':  (' + name + '):  ' + msg.decode('utf-8')
        sendToAll(msg, c)

window = tkinter.Tk()
window.title('Client')
window['bg'] = '#D6C2E6'
window['padx'] = 10
window['pady'] = 10

txt = tkinter.Entry(window)
txt['width'] = 60
txt['relief'] = tkinter.GROOVE
txt['bg'] = '#cbccd0'
txt['fg'] = 'black'
txt['font'] = ("", 18)
txt.grid(column=0, row=2, padx=5, pady=15)

lbl = tkinter.Label(window, text='Starting Chat Application', borderwidth=2, relief="groove", bg='#fc7675')
lbl['font'] = ("", 18)
lbl.grid(columnspan=2, column=0, row=1, padx=5, pady=5, sticky="ew")

_thread.start_new_thread(socketCreation, ())
window.mainloop()
