#!/usr/local/bin/python3.4

# 步驟一：匯入 tkinter 模組。
import tkinter as tk
from tkinter import Tk, Label, Entry, Radiobutton, IntVar, Button, scrolledtext

# 步驟二：建立主視窗。
mainWin = Tk()
var = IntVar()
operation = [ '+', '-', '*', '/']

# 視窗標題
mainWin.title("OmniFocus信件寄送")
# 視窗大小
mainWin.geometry("400x200")

# 步驟三：建立視窗控制項元件。
# 建立標籤
firstNumLabel = Label(mainWin, text="Subject")
secondNumLabel = Label(mainWin, text="Note")

# 按鈕 Click 事件處理函式
def cal():
    exp = firstNum.get() +operation[var.get()] + secondNum.get()

# 建立文字方塊
firstNum = Entry(mainWin, text="Num1")
firstNum.focus()
# secondNum = Entry(mainWin, text="Num2", width=100)

secondNum = scrolledtext.ScrolledText(mainWin, width=40, height=4, wrap=tk.WORD)



button = Button(mainWin, text="Send")


# 版面配置
firstNumLabel.grid(row=0,column=0)
secondNumLabel.grid(row=1,column=0)

firstNum.grid(row=0,column=1 )
#secondNum.grid(row=1,column=1, columnspan=2, rowspan=2)
secondNum.grid(row=1,column=1)
button.grid(row=3, column=0)

# 步驟四： 進入事件處理迴圈。
mainWin.mainloop()
