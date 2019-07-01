import random
import copy
from threading import Timer

from tkinter import *

from point import Point

root = Tk()
# 所有待选图片
imgs = [PhotoImage(file='gif/bar_0' + str(i) + '.png') for i in range(10)]

# 是否已经选中第一块
select_first = False
# 被选中的第一块图片
first_select_rectid = -1
# 被选中的第二块图片
second_select_rectid = -1

# 连通两个块之间的转折点，0到两个
line_point_stack = []
# 连通两块之间绘制的线的id列表
line_id = []

HEIGHT = 9
WIDTH = 10

# 每个块的尺寸
BLOCK_SIZE = 40

# 空面板中的每个位置。默认为空字符串表示未填充图片
map = [["" for y in range(HEIGHT)] for x in range(WIDTH)]
image_map = copy.deepcopy(map)

cv = Canvas(root, bg='green', width=610, height=610)
p1 = p2 = Point(-1, -1)
# 提示信息文字对象
message_id = cv.create_text((500, 50), text="", fill='red', anchor='w', tags='msg')
message_cv = cv.find_withtag("msg")[0]


def create_map():
    """
    初始化连连看地图数据
    :return:
    """
    global map
    # 生成随机地图
    # 将所有匹配成对的图标索引号放进一个临时的地图上
    tmp_map = []
    m = WIDTH * HEIGHT // 10
    print("m=", m)

    # 把连连看图片对应的id按照总的方块数写入一个列表
    for x in range(0, m):
        for i in range(0, 10):
            tmp_map.append(x)

    # 随机打乱连连看的图片id顺序然后填充入地图每个格子中
    random.shuffle(tmp_map)
    for x in range(0, WIDTH):
        for y in range(0, HEIGHT):
            map[x][y] = tmp_map[x * HEIGHT + y]


def print_map():
    """
    输出map 地图
    :return:
    """
    global image_map
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if map[x][y] != '':
                img1 = imgs[int(map[x][y])]
                image_map[x][y] = cv.create_image((x * BLOCK_SIZE + 20, y * BLOCK_SIZE + 20), image=img1)
    cv.pack()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            print(map[x][y], end=' ')
        print(",", y)


def is_link(p1, p2):
    """
    判断两个选中的方块是否可以相连
    :param p1:
    :param p2:
    :return:
    """
    if line_check(p1, p2):
        return True
    elif second_line_check(p1, p2):
        return True
    elif tri_line_check(p1, p2):
        return True
    return False


def line_check(p1, p2):
    """
    检测是否直连
    :param p1:
    :param p2:
    :return:
    """
    # 两个点之间的距离
    abs_distance = 0
    # 两个点之间的空白格子数量
    space_count = 0

    # 同一点或是两点不在同一行或同一列则不适用本方法
    if (p1.x == p2.x and p1.y == p2.y) or (p1.x != p2.x and p1.y != p2.y):
        return False

    if p1.x == p2.x:
        # 同一列的处理
        abs_distance = abs(p1.y - p2.y) - 1

        if p1.y - p2.y > 0:
            zf = -1
        else:
            zf = 1

        for i in range(1, abs_distance + 1):
            if map[p1.x][p1.y + i * zf] == "":
                space_count += 1
            else:
                break
    elif p1.y == p2.y:
        # 同一行的处理
        abs_distance = abs(p1.x - p2.x) - 1
        if p1.x - p2.x > 0:
            zf = -1
        else:
            zf = 1

        for i in range(1, abs_distance + 1):
            if map[p1.x + i * zf][p1.y] == "":
                space_count += 1
            else:
                break

    if space_count == abs_distance:
        print(abs_distance, space_count)
        print("行/列可以直接连通")
        return True
    print("行/列不可直接连通")
    return False


def second_line_check(p1, p2):
    """
    检测是否一折相连,即两个点之间的连线需要一个转折点
    两个点所在位置应能构成一个矩形的对角。
    故分别判断另外两个角所在的位置是否能够连通两个点既可
    :param p1:
    :param p2:
    :return:
    """
    # 第一个直角所在的点(这个点本身也需要验证是否为空)
    check_p1 = Point(p1.x, p2.y)
    # 第二个直角检查点
    check_p2 = Point(p2.x, p1.y)

    if map[check_p1.x][check_p1.y] == "":
        if line_check(p1, check_p1) and line_check(check_p1, p2):
            print("第一个直角可以相连,", check_p1.x, check_p1.y)
            line_point_stack.append(check_p1)
            return True

    if map[check_p2.x][check_p2.y] == "":
        if line_check(p1, check_p2) and line_check(check_p2, p2):
            print("第二个直角可以相连,", check_p2.x, check_p2.y)
            line_point_stack.append(check_p2)
            return True

    print("一折相连的检测不通过")
    return False


def tri_line_check(p1, p2):
    """
    检测是否二折相连。即两个位置的连线需要有两个转折点才可以连通
    检测思路分两步
    1.在p1点周围的4个方向寻找空块检测点。
    2.第一步找到的点是否有任一个可以通过second_line_check的检验。
    若所有空格都遍历完还没有找到则认为不可连通
    :param p1:
    :param p2:
    :return:
    """
    check_p = Point(p1.x, p1.y)

    # 遍历p1的四个方向
    for i in range(0, 4):
        check_p.x = p1.x
        check_p.y = p1.y
        # 向下
        if i == 3:
            check_p.y += 1
            while check_p.y < HEIGHT and map[check_p.x][check_p.y] == "":
                if second_line_check(check_p, p2):
                    print("下探测OK")
                    line_point_stack.append(check_p)
                    return True
                check_p.y += 1

            # 检测是否超出了底部边界,有些游戏超出边界的判断也有效，此处处理这种有效的情况
            if check_p.y == HEIGHT:
                # 底部边界点
                z = Point(p2.x, HEIGHT - 1)
                if line_check(z, p2):
                    line_point_stack.append(Point(p1.x, HEIGHT))
                    line_point_stack.append(Point(p2.x, HEIGHT))
                    print("下探测到游戏区域外部OK")
                    return True

        elif i == 2:
            # 向右检测
            check_p.x += 1
            while check_p.x < WIDTH and map[check_p.x][check_p.y] == "":
                if second_line_check(check_p, p2):
                    print("右探测OK")
                    line_point_stack.append(check_p)
                    return True
                check_p.x += 1
        elif i == 1:
            # 向左
            check_p.x -= 1
            while check_p.x >= 0 and map[check_p.x][check_p.y] == "":
                if second_line_check(check_p, p2):
                    print("左探测ok")
                    line_point_stack.append(check_p)
                    return True
                check_p.x -= 1
        elif i == 0:
            # 向上
            check_p.y -= 1
            while check_p.y >= 0 and map[check_p.x][check_p.y] == "":
                if second_line_check(check_p, p2):
                    print("上探测ok")
                    line_point_stack.append(check_p)
                    return True
                check_p.y -= 1

        # 4个方向均为找到合适的检测点
        print("两直角连接没找到适合的检测点")
    return False


def is_same_img(p1, p2):
    """
    判断两个点是否是同一个图标
    :param p1:
    :param p2:
    :return:
    """
    return map[p1.x][p1.y] == map[p2.x][p2.y]


def find2block(event):
    """
    鼠标右键的回调事件，智能查找功能.查找能够连通的两个点
    :param event:
    :return:
    """
    global first_select_rectid, second_select_rectid
    m_n_row = WIDTH
    m_n_col = HEIGHT

    b_found = False

    # 第一个方块从地图的0位置开始
    for i in range(0, m_n_row * m_n_col):
        if b_found:
            break

        x1 = i % m_n_col
        y1 = i // m_n_col
        p1 = Point(x1, y1)

        # 无图案则继续判断下一个
        if map[x1][y1] == "":
            continue
        for j in range(i + 1, m_n_row * m_n_col):
            x2 = j % m_n_col
            y2 = j // m_n_col
            p2 = Point(x2, y2)

            # 第二个方块不为空，且与第一个方块的图标相同
            if map[x2][y2] != "" and is_same_img(p1, p2):
                if is_link(p1, p2):
                    b_found = True
                    break

    if b_found:
        print("找到了,", p1.x, p1.y, p2.x, p2.y)

        # 找到后在两个图标之间绘制连线？
        first_select_rectid = cv.create_rectangle(x1 * 40, y1 * 40, x1 * 40 + 40, y1 * 40 + 40, width=2, outline='red')
        second_select_rectid = cv.create_rectangle(x2 * 40, y2 * 40, y2 * 40 + 40, y2 * 40 + 40, width=2, outline='red')

        # 定时清除连线
        t = Timer(timer_interval, delay_run)
        t.run()
    return b_found


def showinfo(title, message):
    """
    显示提示
    :param title:
    :param message:
    :return:
    """
    cv.itemconfig(message_cv, text="%s,%s" % (title, message))


def draw_line(p1, p2):
    """
    绘制两个块之间的直线
    :param p1:
    :param p2:
    :return:
    """
    print("draw_line p1, p2", p1.x, p1.y, p2.x, p2.y)
    id = cv.create_line(p1.x * BLOCK_SIZE + 20, p1.y * BLOCK_SIZE + 20,
                        p2.x * BLOCK_SIZE + 20, p2.y * BLOCK_SIZE + 20,
                        width=5, fill='red')
    return id


def draw_link_line(p1, p2):
    """
    画两个连接对象之间的线(如有折点。则是多条直线组成完整的连接线)
    :param p1:
    :param p2:
    :return:
    """
    if len(line_point_stack) == 0:
        line_id.append(draw_line(p1, p2))
    else:
        print(line_point_stack, len(line_point_stack))

    if len(line_point_stack) == 1:
        z = line_point_stack.pop()
        print("一折联通点z", z.x, z.y)
        line_id.append(draw_line(p1, z))
        line_id.append(draw_line(p2, z))

    if len(line_point_stack) == 2:
        z1 = line_point_stack.pop()
        print("两者联通点z1", z1.x, z1.y)
        line_id.append(draw_line(p1, z1))
        z2 = line_point_stack.pop()
        print("两折联通点z2", z2.x, z2.y)
        line_id.append(draw_line(z1, z2))
        # 绘制第二个点和所选点之间的线
        line_id.append(draw_line(z2, p1))


def undraw_connect_line():
    """
    清除画板上的连接线
    :return:
    """
    while len(line_id) > 0:
        cv.delete(line_id.pop())


def clear_two_block():
    """
    清除连通成功的两个点之间的连线和方块图片
    :return:
    """
    global select_first
    # 清除第一个选定框线
    cv.delete(first_select_rectid)
    # 清除第二个选定框线
    cv.delete(second_select_rectid)
    # 清除所选方块的值
    map[p1.x][p1.y] = ''
    cv.delete(image_map[p1.x][p1.y])
    map[p2.x][p2.y] = ''
    cv.delete(image_map[p2.x][p2.y])
    select_first = False
    # 清除选中方块之间的连接线
    undraw_connect_line()


def is_win():
    """
    检测是否游戏胜利(可以优化,减少遍历)
    :return:
    """
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if map[x][y] != '':
                return False
    return True


# 0.3 秒
timer_interval = 0.3


def delay_run():
    """
    延时清除连线以及方块
    :return:
    """
    clear_two_block()


def callback(event):
    """
    鼠标左键回调事件，选中图片
    :param event:
    :return:
    """
    global select_first
    global first_select_rectid, second_select_rectid
    global p1
    global p2
    # 换算棋盘坐标
    x = event.x // BLOCK_SIZE
    y = event.y // BLOCK_SIZE
    print("clicked at", x, y)

    if map[x][y] == '':
        showinfo(title="提示", message="此处无方块")
    else:
        if not select_first:
            p1 = Point(x, y)
            # 在所选块周围画线表示选中
            first_select_rectid = cv.create_rectangle(x * BLOCK_SIZE, y * BLOCK_SIZE,
                                                      (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                                      outline='blue')
            select_first = True
        else:
            p2 = Point(x, y)
            # 判断第二次点击是否和第一次点击时同一个坐标
            if p1.x == p2.x and p1.y == p2.y:
                return

            # 画选中x2, y2处的框线
            print("第2次点击的方块", x, y)
            second_select_rectid = cv.create_rectangle(x * BLOCK_SIZE, y * BLOCK_SIZE,
                                                       (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                                       outline='yellow')
            print("第2次点击的方块", second_select_rectid)
            cv.pack()

            # 是同一张图且两者之间可以连通
            if is_same_img(p1, p2) and is_link(p1, p2):
                print("连通", x, y)
                select_first = False
                # 画选中方块之间的连接线
                draw_link_line(p1, p2)
                # 定时函数清除连通成功的方块和之间的连线
                t = Timer(timer_interval, delay_run)
                t.run()
            else:
                # 删除第一个选定框线和第二个选定框线
                cv.delete(first_select_rectid)
                cv.delete(second_select_rectid)
                select_first = False


# 鼠标左键事件
cv.bind("<Button-1>", callback)
# 鼠标右键事件
cv.bind("<Button-3>", find2block)

cv.pack()
create_map()
print_map()
root.mainloop()
