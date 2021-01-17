from tkinter import *


def update_spin():
    t = int(time.get())
    t += 1
    t = str(t)
    time.set(t)
    root.after(2000, update_spin)


def runner(*args):
    print("hello")
    print(time.get())
    time.set("3")

    


root = Tk()


time = StringVar()
time.set("4")
# root.geometry("200*200")

s = Spinbox(root, from_=1, to=72, textvariable=time)
s.pack()

root.bind("<Return>", runner)
update_spin()
root.mainloop()
