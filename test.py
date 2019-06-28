from tkinter import *

root = Tk()

cv = Canvas(root, bg='white', width=300, height=120)
# 绘制直线
cv.create_line(10, 10, 100, 80, width=2, dash=7)
# 显示画布
cv.pack()

root.mainloop()
