# coding=utf8

import copy
import random
from threading import Timer

from .point import Point

# 列长度
x_count = 10
# 行长度
y_count = 10

# 图片的宽高
img_size = 48


# 初始化地图。将地图中所有方块区域位置置为空方块状态
map = [["" for y in range(y_count)] for x in range(x_count)]

# 存储连连看图片的地图分布信息
image_map = copy.deepcopy(map)

# cv = Canvas(root, bg='green', width=610, height=610)

# 已经被消去图片的点（直角点）
line_point_stack = []


def create_map():
    """
    初始化连连看地图
    :return:
    """
    global map
    # 生成随机地图
    # 将所有匹配成对的图标索引号放进一个临时的地图上
    tmp_map = []
    m = y_count * x_count // 10
    print("m=", m)

    # 把连连看图片对应的id按照总的方块数写入一个列表
    for x in range(0, m):
        for i in range(0, 10):
            tmp_map.append(x)

    # 随机打乱连连看的图片id顺序然后填充入地图每个格子中
    random.shuffle(tmp_map)
    for x in range(0, x_count):
        for y in range(0, y_count):
            map[x][y] = tmp_map[x * y_count + y]


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
            while check_p.y < y_count and map[check_p.x][check_p.y] == "":
                if second_line_check(check_p, p2):
                    print("下探测OK")
                    line_point_stack.append(check_p)
                    return True
                check_p.y += 1

            # 检测是否超出了底部边界,有些游戏超出边界的判断也有效，此处处理这种有效的情况
            if check_p.y == y_count:
                # 底部边界点
                z = Point(p2.x, y_count - 1)
                if line_check(z, p2):
                    line_point_stack.append(Point(p1.x, y_count))
                    line_point_stack.append(Point(p2.x, y_count))
                    print("下探测到游戏区域外部OK")
                    return True

        elif i == 2:
            # 向右检测
            check_p.x += 1
            while check_p.x < x_count and map[check_p.x][check_p.y] == "":
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
    查找能够连通的两个点
    :param event:
    :return:
    """
    global first_select_rectid, second_select_rectid
    m_n_row = x_count
    m_n_col = y_count

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
        # first_select_rectid = cv.create_rectangle(x1 * 40, y1 * 40, x1 * 40 + 40, y1 * 40 + 40, width=2, outline='red')
        # second_select_rectid = cv.create_rectangle(x2 * 40, y2 * 40, y2 * 40 + 40, y2 * 40 + 40, width=2, outline='red')
        #
        # 定时清除连线
        # t = Timer(timer_interval, delayrun)
        # t.run()
    return b_found
