#!/usr/local/bin/python3.4

import tkinter as tk
from tkinter import Tk, Label, Entry, Radiobutton, IntVar, Button, scrolledtext
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys
import getopt


mainWin = Tk()

mainWin.title("OmniFocus信件寄送")
mainWin.geometry("500x200")

Label_passwd  = Label(mainWin, text = "Password")
Label_subject = Label(mainWin, text = "Subject")
Label_note    = Label(mainWin, text = "Note")

def cal():
    sender = 'oriole0105work1@gmail.com'
    passwd = Entry_passwd.get()
    receivers = 'oriole0105.qfs6r@sync.omnigroup.com'

    msg = MIMEMultipart()
    # part = MIMEText( Entry_note.get() )
    part = MIMEText(  "not ready" )
    msg.attach(part)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] =  Entry_subject.get()
    msg['From'] = sender
    msg['To'] = receivers

    # Send the message via our own SMTP server.
    s = smtplib.SMTP("smtp.gmail.com:587")
    s.ehlo()
    s.starttls()
    s.login(sender, passwd)
    s.sendmail(msg['From'], receivers , msg.as_string())

    #s.send_message(msg)
    s.quit()

Entry_passwd  = Entry(mainWin, show="*", text = "", width = 40)
Entry_subject = Entry(mainWin, text = "", width = 40)
Entry_note = scrolledtext.ScrolledText(mainWin, width=50, height=4, wrap=tk.WORD)

button = Button(mainWin, text="Send", command = cal )




Label_passwd.grid  ( row=0,column=0)
Label_subject.grid ( row=1,column=0)
Label_note.grid    ( row=2,column=0)
button.grid        ( row=3, column=0)

Entry_passwd.grid  ( row=0,column=1 )
Entry_subject.grid ( row=1,column=1 )
Entry_note.grid    ( row=2,column=1)

mainWin.mainloop()



