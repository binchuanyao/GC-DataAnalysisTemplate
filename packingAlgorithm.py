# -*- coding: utf-8 -*-
# @File   : 3D-carton
# @Time   : 2022/04/14 20:02 
# @Author : BCY

from matplotlib import pyplot as plt
#设置图表刻度等格式
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from datetime import datetime


def packing(skuList, ctnSize):
    # print('---------------------------------- ')
    # print('skuList: ', skuList)
    # print('ctnSize: ', ctnSize)

    containerVol = ctnSize[0] * ctnSize[1] * ctnSize[2]

    # 已装sku数量 packed_list = [packedNum, packedVol]
    packed_result_list = [0, 0]
    usedPoint = []
    skuNum = len(skuList)

    O = (0, 0, 0)  # 原点坐标
    show_num = [make(O, ctnSize, 'red')]

    # skuList按体积降序排列
    skuList = sorted(skuList, reverse=True)


    # 把货物第一次装箱
    # 返回的结果为：4个元素列表 放置点列表，弃用点列表，已装数量，已装体积
    # Plan1[0]: 放置点列表
    # Plan1[1]: 弃用点列表
    Plan1 = packing3D(packed_result_list, show_num, (0, 0, 0), ctnSize, skuList, usedPoint)

    # change = ['ab', 'bc']


    # 如果已装数量等于sku总件数，则放回满箱率；否则交换长宽方向，继续尝试装箱
    if packed_result_list[0] == skuNum:
        ratio = 1.0 * float(packed_result_list[1]) / float(containerVol)
        return ratio
    else:
        # 尝试长宽交换和宽高交换  ['ab', 'bc']

        # 逆转方向后返回未装箱的skulist
        restSKUList1 = surplus(packed_result_list[0], skuList[:], 'ab')

        # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
        re1 = twice(show_num, packed_result_list.copy(), Plan1[1], ctnSize, restSKUList1, usedPoint)

        ratio1 = 1.0 * float(re1[1]) / float(containerVol)

        # 逆转方向后返回未装箱的skulist
        restSKUList2 = surplus(packed_result_list[0], skuList[:], 'bc')
        # restSKUList2 = surplus(Plan1[2], skuList, 'ac')
        # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
        re2 = twice(show_num, packed_result_list.copy(), Plan1[1], ctnSize, restSKUList2, usedPoint)
        # print('22222222: ', show_num, Plan3[2], Plan3[3], Plan3[1], ctnSize, restSKUList2)
        ratio2 = 1.0 * float(re2[1]) / float(containerVol)

        ratio = max(ratio1, ratio2)


        # 选择满箱率最大的方式
        if re1[0]==skuNum | re2[0]==skuNum:
            # make_pic(show_num)
            return ratio
        else:
            # make_pic(show_num)
            return 0


def packing3D_improve(skuList, ctnSize, show=False):
    '''
    按朝向和放置点，遍历搜索是否能放入
    :param show_num: 图显信息
    :param ctnSize: 纸箱尺寸
    :param skuList: sku列表
    :return: 满箱率
    '''
    # skuList按体积降序排列
    skuList = sorted(skuList, reverse=True)

    original = (0,0,0)  #初始放置点为 原点（0,0,0)
    show_num = [make(original, ctnSize, 'red')]

    ctnVol = ctnSize[0] * ctnSize[1] * ctnSize[2]   # 箱型体积
    skuNum = len(skuList)                          # 总件数

    ## 初始放置点
    O_items = [original]
    used_point = []      # 已放置点列表
    placed_sku = []      # 已放入SKU列表
    packedNum = 0        # 已放入sku数量
    packedVol = 0.0      # 已放入sku总体积

    # 初始化最小cube为第一个sku
    cube = skuList[0]

    # 放置货物的朝向
    # face = ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
    # face = ['abc', 'bac', 'acb']
    color_dict = {'abc': 'blue', 'bac': 'orange', 'acb': 'yellow'}

    for i in range(len(skuList)):
        # 遍历SKU的可选朝向, 每换一个sku, face重新初始化
        face = ['abc', 'bac', 'acb']
        for choose_face in face:
            curr_sku = exchange(skuList[i], choose_face)

            for point in O_items:

                # 判断如果当前放置点及朝向有重叠，则跳过
                isOverlapFlag = 0
                if len(placed_sku) > 0:
                    for j in range(len(used_point)):
                        if isOverlap(point, curr_sku, used_point[j], placed_sku[j]):
                            isOverlapFlag += 1

                if isOverlapFlag > 0:
                    continue
                # 如果放置点放置货物后，三个方向都不会超过箱体限制,则认为可以堆放
                elif point[0]+curr_sku[0]<=ctnSize[0] and point[1]+curr_sku[1]<=ctnSize[1] and point[2]+curr_sku[2]<=ctnSize[2]:
                    #使用放置点，添加一个图显信息
                    new_show = make(point, curr_sku, color_dict[choose_face])

                    if new_show not in show_num:
                        # print('1 new_show: ', new_show)
                        show_num.append(new_show)
                        # make_pic(show_num)
                        used_point.append(point)      # 在已用点列表中增加当前放置点
                        placed_sku.append(curr_sku)   # 在已放sku列表中增加当前sku
                        # 计数加1
                        # print('222 current face: ', choose_face,  '222 current Box: ', curr_sku)

                        packedNum += 1
                        packedVol += curr_sku[0] * curr_sku[1] * curr_sku[2]
                        cube = gene_min_cube(cube, point, curr_sku)

                        ## 把堆叠后产生的新的点，加入放置点列表
                        for new_O in newsite(point, curr_sku):
                            # 保证放入的可用点是不重复的
                            if new_O not in O_items:
                                O_items.append(new_O)

                        # 将已用点从放置点列表中删除
                        O_items = list(filter(lambda x: x not in used_point, O_items))
                        O_items = sorted(O_items, key=lambda x: distance(x))   # 按与原点的距离升序排列，优先使用靠近原点的点

                        # if len(O_items) > 1:
                        #     O_items = self.clear_newsite3(O_items)

                    # 如果当前sku能放入，则跳出选点的循环
                    break

            # 如果已装数量 大于当前列表index+1，表示当前sku已经装入，跳出旋转的循环
            if packedNum >= i+1:
                break

    if packedNum == skuNum:
        if show:
            make_pic(show_num)
        return float(packedVol/ctnVol)
    else:
        if show:
            make_pic(show_num)
            print('目标箱型尺寸： ', ctnSize)
            print('订单sku列表： ', skuList)
            print('订单总件数： ', skuNum, '已装件数', packedNum)
            print('=' * 15, '当前订单无法匹配目标箱型!', '=' * 15)
        return 0


def isOverlap(aCoord, aSize, bCoord, bSize):
    """
    判断三面投影是否重叠
    按逻辑，如果两个立方体不重叠，在OXY,OXZ,OYZ上最多允许有一个投影面发生重叠（三维问题转二维）
    """
    overlap = 0  # 计算有几个面重叠
    if bCoord[0] >= aCoord[0] + aSize[0] or aCoord[0] >= bCoord[0] + bSize[0] or bCoord[1] >= aCoord[1] + aSize[1] or aCoord[1] >= bCoord[1] + bSize[1]:
        """
        按逻辑，如果两个方形不重叠
        在两个轴方向上，只要有一边超出另一个物体的长度范围即可（二维转一维）
        下同理
        """
        # print("底面不重叠")
        pass
    else:
        # print("底面重叠")
        overlap = overlap + 1

    if bCoord[0] >= aCoord[0] + aSize[0] or aCoord[0] >= bCoord[0] + bSize[0] or bCoord[2] >= aCoord[2] + aSize[2] or aCoord[2] >= bCoord[2] + bSize[2]:
        # print("长侧面不重叠")
        pass
    else:
        # print("长侧面重叠")
        overlap = overlap + 1
    if bCoord[1] >= aCoord[1] + aSize[1] or aCoord[1] >= bCoord[1] + bSize[1] or bCoord[2] >= aCoord[2] + aSize[2] or aCoord[2] >= bCoord[2] + bSize[2]:
        # print("宽侧面不重叠")
        pass
    else:
        # print("宽侧面重叠")
        overlap = overlap + 1

    if overlap>1: # 如果这个值大于1则判断两个方体重叠
        return True
    else:
        return False

def distance(x):  # 返回与原点的欧式距离
    return x[0]*x[0], x[1]*x[1], x[2]*x[2]

#make_pic内置函数
def box(ax,x, y, z, dx, dy, dz, color='red'):
    xx = [x, x, x+dx, x+dx, x]
    yy = [y, y+dy, y+dy, y, y]
    kwargs = {'alpha': 1, 'color': color}
    ax.plot3D(xx, yy, [z]*5, **kwargs)#下底
    ax.plot3D(xx, yy, [z+dz]*5, **kwargs)#上底
    ax.plot3D([x, x], [y, y], [z, z+dz], **kwargs)
    ax.plot3D([x, x], [y+dy, y+dy], [z, z+dz], **kwargs)
    ax.plot3D([x+dx, x+dx], [y+dy, y+dy], [z, z+dz], **kwargs)
    ax.plot3D([x+dx, x+dx], [y, y], [z, z+dz], **kwargs)
    return ax


#把尺寸数据生成绘图数据
def make(O,C, color):
    data = [O[0],O[1],O[2],C[0],C[1],C[2], color]
    return data

def make_pic(Items):
    fig = plt.figure()
    ax = Axes3D(fig)
    # ax.xaxis.set_major_locator(MultipleLocator(50))
    # ax.yaxis.set_major_locator(MultipleLocator(50))
    # ax.zaxis.set_major_locator(MultipleLocator(50))


    Xmax = (int(max(Items[-1][0:6]) / 10) + 1) * 10   # xyz最大刻度为纸箱最长边
    print('Xmax: ', Xmax)

    ax.set_xlim3d(0, Xmax)
    ax.set_ylim3d(0, Xmax)
    ax.set_zlim3d(0, Xmax)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # print 画图的点
    print('---- show num: ')
    print(Items)

    for num in Items:
        box(ax, num[0], num[1], num[2], num[3], num[4], num[5], num[6])
    plt.show()

#可用点的生成方法
def newsite(O,B_i):
    # 在X轴方向上生成
    O1 = (O[0]+B_i[0],O[1],O[2])
    # 在Y轴方向上生成
    O2 = (O[0],O[1]+B_i[1],O[2])
    # 在Z轴方向上生成
    O3 = (O[0],O[1],O[2]+B_i[2])
    # return [O1,O2,O3]  # 返回长宽高方向的放置点
    return [O3, O2, O1]  # 高宽长方向的放置点

#3.拟人化依次堆叠方体, 返回已码数量、放置点，弃用点
def packing3D(packed_result_list, show_num, O, C, Box_list, used_point):
    O_items = [O]
    O_pop = []
    for i in range(0,len(Box_list)):
        #货物次序应小于等于可用点数量，如：第四个货物i=3，使用列表内的第4个放置点O_items[3]，i+1即常见意义的第几个，len即总数，可用点总数要大于等于目前个数
        if i+1 <= len(O_items):
            #如果放置点放置货物后，三个方向都不会超过箱体限制,则认为可以堆放
            if O_items[i-1][0]+Box_list[i][0]<=C[0] and O_items[i-1][1]+Box_list[i][1]<=C[1] and O_items[i-1][2]+Box_list[i][2]<=C[2]:
                #使用放置点，添加一个图显信息
                new_show = make(O_items[i-1],Box_list[i], 'blue')
                if new_show not in show_num:
                    show_num.append(make(O_items[i-1],Box_list[i], 'blue'))
                    used_point.append(O_items[i-1])
                    # 计数加1
                    # print('2 packedNum: ', packedNum)
                    packed_result_list[0] += 1
                    # print('1111111111: ', packedNum )
                    packed_result_list[1] += Box_list[i][0] * Box_list[i][1] * Box_list[i][2]
                #把堆叠后产生的新的点，加入放置点列表
                for new_O in newsite(O_items[i-1],Box_list[i]):
                    #保证放入的可用点是不重复的
                    if new_O not in O_items:
                        O_items.append(new_O)

                # 将已用点从放置点列表中删除
                O_items = list(filter(lambda x: x not in used_point, O_items))

            #如果轮到的这个放置点不可用
            else:
                #把这个可用点弹出弃用
                O_pop.append(O_items.pop(i-1))
                #弃用可用点后，货物次序应小于等于剩余可用点数量
                if i+1 <= len(O_items):# and len(O_items)-1>=0:
                    #当可用点一直不可用时
                    while O_items[i-1][0]+Box_list[i][0]>C[0] or O_items[i-1][1]+Box_list[i][1]>C[1] or O_items[i-1][2]+Box_list[i][2]>C[2]:
                        #一直把可用点弹出弃用
                        O_pop.append(O_items.pop(i-1))
                        #如果弹出后货物次序超出剩余可用点，则认为无法继续放置
                        if i-1 > len(O_items)-1:
                            break
                    #货物次序应小于等于剩余可用点数量
                    if i+1 <= len(O_items):
                        #如果不再超出限制，在这个可用点上堆叠
                        new_show = make(O_items[i-1],Box_list[i], 'blue')
                        if new_show not in show_num:
                            show_num.append(make(O_items[i-1],Box_list[i], 'blue'))
                        #计数加1
                            # print('2 packedNum: ', packedNum)
                            packed_result_list[0] +=  1
                            # print('22222222222: ', packedNum)
                            packed_result_list[1] += Box_list[i][0] * Box_list[i][1] * Box_list[i][2]
                        #把堆叠后产生的新的点，加入放置点列表
                        for new_O in newsite(O_items[i-1],Box_list[i]):
                            #保证放入的可用点是不重复的
                            if new_O not in O_items:
                                O_items.append(new_O)

                        # 将已用点从放置点列表中删除
                        O_items = list(filter(lambda x: x not in used_point, O_items))

    # 返回放置点列表，弃用点列表，已装数量，已装体积
    return O_items,O_pop



def minCube(skuList, show=False):
    '''
    根据sku列表生成最小cube
    :param skuList: sku列表，sku为元组形式
    :return:
    '''
    O = (0,0,0)       # 初始放置点
    O_items = [O]     # 放置点列表
    used_point = []   # 已用放置点
    placed_sku = []   # 已放sku

    # 图显信息列表
    show_num = []

    # 初始化最小cube为第一个sku
    cube = skuList[0]
    show_num.append(make(O, cube, 'blue'))
    # cubeVol = skuList[0][0] * skuList[0][1] * skuList[0][2]
    # 把堆叠后产生的新的点，加入放置点列表
    for new_O in newsite(O_items[0], skuList[0]):
        # 保证放入的可用点是不重复的
        if new_O not in O_items:
            O_items.append(new_O)
    used_point.append(O)
    placed_sku.append(skuList[0])
    O_items = list(filter(lambda x: x not in used_point, O_items))

    # 放置货物的朝向
    face = ['abc','acb','bac','bca','cab', 'cba']

    # 第2到最后一个SKU
    for i in range(1, len(skuList)):
        # 初始化cube为三边叠加的最大立方体
        curr_sku = skuList[i]
        choose_point = 0
        choose_face = 'abc'
        # 每增加一个货物，初始化当前cube为最大立方体
        curr_cube = (cube[0] + curr_sku[0], cube[1] + curr_sku[1], cube[2] + curr_sku[2])
        # curr_cube_vol = (cube[0] + curr_sku[0]) * (cube[1] + curr_sku[1]) * (cube[2] + curr_sku[2])

        for point in O_items:
            for f in face:
                curr_sku = exchange(skuList[i], f)
                # print('point: ', point, 'curr_sku: ', curr_sku)
                # v = geneMinCubeAndVol(cube, point, curr_sku)[1]   # 返回当前放置方式的最小cube体积
                # if v < curr_cube_vol:     # 此摆放方式体积更小，则更新摆放点，摆放方式和当前体积

                # 判断选择当前放置点会否与其他SKU重合
                isOverlapFlag = 0
                for k in range(len(used_point)):
                    if isOverlap(point, curr_sku, used_point[k], placed_sku[k]):
                        isOverlapFlag += 1

                if isOverlapFlag > 0:  # 如果当前放置点及朝向有重叠，则跳过
                    continue
                else:

                    '''最长边最小'''
                    c = gene_min_cube(cube, point, curr_sku)
                    if max(c) < max(curr_cube):

                        choose_point = point  # 更新摆放点
                        choose_face = f       # 更新摆放方式
                        curr_cube = c         # 更新当前cube
                        # curr_cube_vol = c[0] * c[1] * c[2]    # 更新当前cube体积

        curr_placed_sku = exchange(skuList[i], choose_face)
        show_num.append(make(choose_point, curr_placed_sku, 'blue'))
        # print('choose point: ', choose_point, 'curr_sku: ', placed_sku)
        # 添加新的放置点
        for new_O in newsite(choose_point, curr_placed_sku):
            if new_O not in O_items:
                O_items.append(new_O)
        used_point.append(choose_point)
        placed_sku.append(curr_placed_sku)
        cube = gene_min_cube(cube, choose_point, curr_placed_sku)
        O_items = list(filter(lambda x: x not in used_point, O_items))
        O_items = sorted(O_items, key=lambda x: distance(x))  # 按与原点的距离升序排列，优先使用靠近原点的点
        # ### 清理覆盖点
        # if len(O_items) > 1:
        #     O_items = clear_newsite(O_items)

    show_num.append(make((0,0,0), cube, 'green'))

    # 显示图片
    if show:
        make_pic(show_num)

    # 最小cube按三边长度重排序
    cube = tuple(sorted(cube, reverse=True))
    return cube

# 生成最小cube, 返回最小cube和体积
def geneMinCubeAndVol(cube, O, sku):
    current = [round(i + j, 2) for i, j in zip(O, sku)]
    new_cube = tuple([max(i, j) for i, j in zip(cube, current)])
    vol = new_cube[0] * new_cube[1] * new_cube[2]
    return new_cube, vol

## 生成最小cube, 返回最小cube
def gene_min_cube(cube, O, sku):
    current = [ round(i + j , 2) for i, j in zip(O, sku)]
    new_cube = tuple([max(i, j) for i, j in zip(cube, current)])
    return new_cube

def clear_newsite(O_items):
    '''
    清除多余的放置点，即每个轴线及平面上只可能存在一个放置点，第一象限内可存在多个放置点
    :param O_items: 原始放置点
    :return: 清除覆盖点后的放置点
    '''
    # 3条轴线上的点
    X_axis = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] != 0]
    Y_axis = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] != 0]
    Z_axis = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] == 0]

    # 3个平面上的点
    XOY = [i for i in O_items if i[0] == 0 and i[1] == 0 and i[2] != 0]
    XOZ = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] == 0]
    YOZ = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] == 0]

    # 其他象限中的点
    other = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] != 0]

    # 轴线及平面上的点
    current = [XOY, YOZ, XOZ, X_axis, Y_axis, Z_axis]

    new_O_items = []
    for axis in current:
        if len(axis)>0:  # 列表不为空时才取最大值
            new_O_items.append(get_max_point(axis))

    for point in other:
        new_O_items.append(point)

    return new_O_items


def get_max_point(matrix):
    '''
    得到矩阵中每一列最大的值
    '''
    res_list=[]
    for j in range(3):
        one_list=[]
        for i in range(len(matrix)):
            one_list.append(matrix[i][j])
        res_list.append(max(one_list))
    return tuple(res_list)


def exchange(sku, change): #change='abc','acb','bac','bca','cba','cab' 有6种对调可能，默认为abc
    if change == 'acb':
        new_sku = (sku[0], sku[2], sku[1])
    elif change == 'bac':
        new_sku = (sku[1],sku[0],sku[2])
    elif change == 'bca':
        new_sku = (sku[0], sku[2], sku[1])
    elif change == 'cba':
        new_sku = (sku[2], sku[1], sku[0])
    elif change == 'cab':
        new_sku = (sku[2], sku[0], sku[1])
    else:
        return sku
    return new_sku


def stackHeight(skuList):
    length = []
    width = []
    H = 0
    for sku in skuList:
        sku = sorted(sku, reverse=True)
        length.append(sku[0])
        width.append(sku[1])
        H += min(sku)
    L = max(length)
    W = max(width)
    H = round(H, 2)

    # 最小cube三边重排序
    cube = tuple(sorted((L,W,H), reverse=True))
    return cube


#<<<---写一个函数专门用来调整方向和计算剩余货物
def surplus(num, Box_list, change): #change='ab','bc','ac',0有三组对调可能，共6种朝向
    # print('num, Box_list, change: ', num, Box_list, change)

    new_Box_list = Box_list[num-1:-1]
    # print('in surplus new_box_list: ', new_Box_list)
    if num == 0:
        new_Box_list = Box_list
    if change == 'ab':
        for i in range(0,len(new_Box_list)):
            new_Box_list[i]=(new_Box_list[i][1],new_Box_list[i][0],new_Box_list[i][2])
    elif change == 'bc':
        for i in range(0,len(new_Box_list)):
            new_Box_list[i]=(new_Box_list[i][0],new_Box_list[i][2],new_Box_list[i][1])
    elif change == 'ac':
        for i in range(0,len(new_Box_list)):
            new_Box_list[i]=(new_Box_list[i][2],new_Box_list[i][1],new_Box_list[i][0])
    elif change == 0:
        return new_Box_list
    else:
        return new_Box_list
    return new_Box_list

#残余点二次分配函数
def twice(show_num, packed_result_list, O_pop, C, Box_list, used_point):
    # print('in twice function： ', show_num,packedNum, O_pop,C,Box_list)
    for a2 in O_pop:
        if a2[0]==0 and a2[1]==0:
            Plan = packing3D(packed_result_list, show_num,a2,C,Box_list, used_point)
            Box_list = surplus(packed_result_list[0],Box_list,0)
        elif a2[1]==0 and a2[2]==0:
            Plan = packing3D(packed_result_list, show_num,a2,C,Box_list, used_point)
            Box_list = surplus(packed_result_list[0],Box_list,0)
        elif a2[0]==0 and a2[2]==0:
            Plan = packing3D(packed_result_list, show_num,a2,C,Box_list, used_point)
            # print('in twice Plan 3: ', Plan)
            Box_list = surplus(packed_result_list[0],Box_list,0)
    return packed_result_list

def gene_skuSize(skuList):
    '''
    将合并的skulist转化为packing能识别的参数 eg: [[(58.0, 17.0, 5.5)], [(16.5, 16.5, 6.0)]] → [(58.0, 17.0, 5.5), (16.5, 16.5, 6.0)]
    :param skuList:
    :return:
    '''
    n = len(skuList)
    if n==1:
        return skuList[0]
    else:
        new_skuList = []
        for item in skuList:
            for sku in item:
                new_skuList.append(sku)

        return new_skuList



def load_data(file_path, file_name, isMulti=True, ctn_list=None):
    if ".xlsx" in file_name:
        df = pd.read_excel('{}{}'.format(file_path, file_name))
    else:
        try:
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='utf-8')
        except:
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='gbk')

    shape1 = df.shape

    print('============', '数据导入完成！', '============ ')
    print('原始数据行数： ', shape1[0])
    print('原始订单数： ', df['订单号'].nunique())

    # 剔除sku尺寸异常的订单
    df = df.drop(df[(df['实际长cm'] <= 1) & (df['实际宽cm'] <= 1) & (df['实际高cm'] <= 1)].index)

    shape2 = df.shape

    print('剔除sku尺寸异常数据行数： ', shape1[0]-shape2[0])
    print('剔除异常数据后的订单数： ', df['订单号'].nunique())

    # 合并长宽高，按长度降序排列，格式为元祖
    df['l_w_h'] = df[['实际长cm', '实际宽cm', '实际高cm']].apply(lambda x: tuple(sorted(x, reverse=True)),axis=1)
    df['lineVol'] = df['实际长cm'] * df['实际宽cm'] * df['实际高cm'] * df['产品内件数']
    df['lineWt'] = df['实际重量kg'] * df['产品内件数']


    df['skuSize_temp'] = (df['l_w_h'] * df['产品内件数']).apply(lambda x: [x[i:i + 3] for i in range(0, len(x), 3)])



    # 合并多品订单中SKU尺寸，合并为tuple的列表, 按SKU尺寸降序
    # 按订单号合并skuSize, skuSize_temp列形式为[[(58.0, 17.0, 5.5)], [(16.5, 16.5, 6.0)]]
    order_df= df.groupby('订单号')['skuSize_temp'].apply(lambda x: list(sorted(x, reverse=True))).reset_index()


    order_df['skuSize'] = order_df['skuSize_temp'].apply(gene_skuSize)
    order_df['sku'] = order_df['skuSize_temp'].apply(len)
    order_df['qty'] = order_df['skuSize'].apply(len)

    order_df2 = df.groupby('订单号')[['lineVol', 'lineWt']].sum().reset_index()
    order_df2.columns = ['订单号', 'orderVol', 'orderWt']

    order_df = pd.merge(order_df, order_df2, on=['订单号'], how='left')

    if isMulti:
        # 剔除件数单件订单
        order_df = order_df.drop(order_df[order_df['qty'] ==1].index)
        order_df['订单结构'] = '单品多件'
        order_df.loc[(order_df['sku']>1) & (order_df['qty']>1), ['订单结构']] = '多品多件'
        # order_df.loc[(order_df['sku'] > 10) | (order_df['qty'] > 20), ['订单结构']] = '批量订单'
    else:
        order_df['订单结构'] = '单品多件'
        order_df.loc[(order_df['sku'] > 1) & (order_df['qty'] > 1), ['订单结构']] = '多品多件'
        order_df.loc[(order_df['qty'] == 1), ['订单结构']] = '单品单件'

    df = pd.merge(order_df[['订单号', 'qty', 'orderVol']], df, on=['订单号'], how='left')
    # df = df.drop(df[df['qty'] ==1].index)
    print(df.columns)

    # 合并多品订单中SKU货型，合并为字符串
    # ‘产品货型’ 为系统按尺寸和重量计算的货型
    order_size_df = df.groupby('订单号')['产品货型'].apply(lambda x: np.unique(x)).reset_index()
    # order_size_df = df.groupby(['订单号'])['产品货型'].unique().agg('-'.join).reset_index()

    # 'new_sku_size' 为按sku尺寸计算的货型
    order_size_df2 = df.groupby('订单号')['new_sku_size'].apply(lambda x: np.unique(x)).reset_index()

    order_size_df = pd.merge(order_size_df, order_size_df2, on=['订单号'])

    if '物流产品' in df.columns and '服务渠道' in df.columns:
        order_detail = df[['订单号', '客户代码', '服务渠道', '物流产品', '创建时间 仓库当地', '物理仓编码', 'Area']].drop_duplicates()
    else:
        order_detail = df[['订单号', '客户代码', '创建时间 仓库当地', '物理仓编码', 'Area']].drop_duplicates()

    temp_df = pd.merge(order_detail, order_size_df, on=['订单号'], how='left')
    order_df = pd.merge(order_df, temp_df, on=['订单号'], how='left').reset_index()

    # 删除多品订单件数为1的行
    # 由于单品单件和单品多件都需要 试装箱，可以不剔除

    print('============', '数据处理完成！', '============ ')
    print('单品多件&多品多件订单数： ', order_df.shape[0])

    '''
    箱型匹配
    '''
    if ctn_list is not None:
        print('======================= ', '箱型1')
        order_df['r1'] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[0]))

        print('======================= ', '箱型2')
        order_df['r2'] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[1]))

        print('======================= ', '箱型3')
        order_df['r3'] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[2]))

        print('======================= ', '箱型4')
        order_df['r4'] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[3]))

        print('======================= ', '箱型5')
        order_df['r5'] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[4]))

        print('======================= ', '箱型6')
        order_df['r6'] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[5]))

        # 推荐箱型
        ratio_col = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6']
        carton_trans = {'r1': '1号箱', 'r2': '2号箱', 'r3': '3号箱', 'r4': '4号箱', 'r5': '5号箱', 'r6': '6号箱', 'Null': 'Null'}


        order_df['推荐箱型'] = order_df[ratio_col].idxmax(axis=1)   # 满箱率最大值对应的列名
        order_df.loc[(order_df[ratio_col].sum(axis=1) == 0), ['推荐箱型']] = 'Null'
        order_df['推荐箱型'] = order_df['推荐箱型'].map(carton_trans)

        order_df['满箱率'] = order_df[ratio_col].max(axis=1)

        re_df = pd.pivot_table(order_df[['订单号', '推荐箱型', '满箱率']],
                               index=['推荐箱型'],
                               values=['订单号', '满箱率'],
                               aggfunc={'订单号': len, '满箱率': np.mean},
                               margins=True,
                               margins_name='合计').reset_index()

        re_df.columns = ['推荐箱型', '平均满箱率', '订单数']
        re_df['订单数%'] = re_df['订单数'] / (re_df['订单数'].sum() / 2)

        time = datetime.now()
        str_time = time.strftime('%Y_%m_%d_%H_%M')
        order_df.to_csv('{}{}'.format(file_path, '多品多件装箱_明细{}.csv'.format(str_time)), index=False, na_rep='Null')
        re_df.to_csv('{}{}'.format(file_path, '多品多件装箱_结果{}.csv'.format(str_time)), index=False, na_rep='Null')

    return order_df


def load_carton(file_path, file_name):
    if ".xlsx" in file_name:
        df = pd.read_excel('{}{}'.format(file_path, file_name))
    else:
        try:
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='utf-8')
        except:
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='gbk')

    # 将箱子的长，宽，高合并为元组，不改变三边的朝向
    df['箱型尺寸'] = df[['Length', 'Width', 'Height']].apply(lambda x: tuple(x),axis=1)

    ctn_dict = dict(zip(df['Ratio'],df['CartonName']))

    # 返回所有箱型的列表
    return list(df['箱型尺寸']), ctn_dict, df[['CartonName', '箱型尺寸']]


def run_packing(order_df, ctn_df, ctn_list, file_path, ctn_dict=None, carton_type=None, isCalcuMinCube=False):
    '''
    计算订单匹配的箱型
    :param order_df: 订单数据的dataframe
    :param order_df: 包含箱型尺寸的dataframe
    :param ctn_list: 候选箱型类表
    :return:
    '''

    # 不同箱型满箱率对应字段，命名为'r1', 'r2','r3'...
    ratio_col = []
    n = len(ctn_list)

    # 根据箱型列表，匹配订单最合适的箱型
    for i in range(n):

        if i+1<10:
            num = '0{}'.format(i+1)
        else:
            num = str(i+1)

        print('='*15, '箱型{}: '.format(i+1), ctn_list[i])
        order_df['r{}'.format(num)] = order_df['skuSize'].apply(lambda x: packing3D_improve(x[:], ctn_list[i]))
        ratio_col.append('r{}'.format(num))

    # 推荐箱型
    # ratio_col = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6']
    # carton_trans = {'r1': '1号箱', 'r2': '2号箱', 'r3': '3号箱', 'r4': '4号箱', 'r5': '5号箱', 'r6': '6号箱', 'Null': 'Null'}

    if ctn_dict is None:
        carton_trans = {}  # 满箱率列名与箱型的对应字典
        carton_list = [x.replace('r', 'Size') for x in ratio_col ]  # 将满箱率列名中的'r'替换为'箱型'
        for i in range(n):
            carton_trans[ratio_col[i]] = carton_list[i]  # 字典增加键值对
    else:
        carton_trans = ctn_dict


    order_df['推荐箱型'] = order_df[ratio_col].idxmax(axis=1)   # 满箱率最大值对应的列名
    order_df.loc[(order_df[ratio_col].sum(axis=1) == 0), ['推荐箱型']] = 'NotMatch'
    order_df['推荐箱型'] = order_df['推荐箱型'].map(carton_trans)

    order_df = pd.merge(order_df, ctn_df, left_on=['推荐箱型'], right_on=['CartonName'], how='left')

    order_df['满箱率'] = order_df[ratio_col].max(axis=1)

    re_df = pd.pivot_table(order_df[['订单结构','订单号', '推荐箱型', '箱型尺寸', '满箱率']],
                           index=['订单结构', '推荐箱型', '箱型尺寸'],
                           values=['订单号', '满箱率'],
                           aggfunc={'订单号': len, '满箱率': np.mean},
                           margins=True,
                           margins_name='合计').reset_index()
    print(ratio_col)
    print(carton_trans)
    print(re_df.columns)
    re_df.columns = ['订单结构', '推荐箱型', '箱型尺寸', '平均满箱率', '订单数']
    re_df['订单数%'] = re_df['订单数'] / (re_df['订单数'].sum() / 2)

    if isCalcuMinCube:
        '''
        匹配订单的最小cube
        '''
        print('=' * 15, '计算订单的最小cube')
        order_df['minCube'] = order_df['skuSize'].apply(lambda x: minCube(x[:]))
        order_df['minCubeVol'] = order_df['minCube'].apply(lambda x: x[0]*x[1]*x[2])
        order_df['minCubeRate'] = 1.00 * order_df['orderVol'] / order_df['minCubeVol']

        '''
        GC现在用的高叠加算法
        '''
        print('=' * 15, '高叠加算法的cube')
        order_df['heightStackCube'] =  order_df['skuSize'].apply(lambda x: stackHeight(x))
        order_df['heightStackCubeVol'] = order_df['heightStackCube'].apply(lambda x: x[0] * x[1] * x[2])
        order_df['heightStackRate'] = 1.00 * order_df['orderVol'] / order_df['heightStackCubeVol']

        '''比较2种算法选择的体积'''
        order_df['diffRatio'] = (order_df['minCubeVol']  -  order_df['heightStackCubeVol'])/order_df['heightStackCubeVol']


    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    order_df.to_csv('{}{}'.format(file_path, '多件装箱明细_{}_{}.csv'.format(carton_type, str_time)), index=False, na_rep='Null')
    re_df.to_csv('{}{}'.format(file_path, '多件装箱结果_{}_{}.csv'.format(carton_type, str_time)), index=False, na_rep='Null')


def run_min_cube(order_df, file_path):
    '''
    根据订单计算匹配的最小Cube
    :param order_df: 订单数据的dataframe
    :return:
    '''

    '''
    匹配订单的最小cube
    '''
    print('=' * 15, '计算订单的最小cube')
    order_df['minCube'] = order_df['skuSize'].apply(lambda x: minCube(x[:]))
    order_df['minCubeVol'] = order_df['minCube'].apply(lambda x: x[0] * x[1] * x[2])
    order_df['minCubeRate'] = 1.00 * order_df['orderVol'] / order_df['minCubeVol']

    # 最小cube的长宽高
    order_df['cube_L'] = order_df['minCube'].apply(lambda x: x[0])
    order_df['cube_W'] = order_df['minCube'].apply(lambda x: x[1])
    order_df['cube_H'] = order_df['minCube'].apply(lambda x: x[2])

    '''
    GC现在用的高叠加算法
    '''
    print('=' * 15, '高叠加算法的cube')
    order_df['高叠加'] = order_df['skuSize'].apply(lambda x: stackHeight(x))
    order_df['高叠加体积'] = order_df['高叠加'].apply(lambda x: x[0] * x[1] * x[2])
    order_df['高叠加满箱率'] = 1.00 * order_df['orderVol'] / order_df['高叠加体积']

    # 高叠加的长宽高
    order_df['高叠加_L'] = order_df['高叠加'].apply(lambda x: x[0])
    order_df['高叠加_W'] = order_df['高叠加'].apply(lambda x: x[1])
    order_df['高叠加_H'] = order_df['高叠加'].apply(lambda x: x[2])

    '''比较2种算法选择的体积'''
    order_df['差异率'] = (order_df['minCubeVol'] - order_df['高叠加体积']) / order_df['高叠加体积']

    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    order_df.to_csv('{}{}'.format(file_path, '多件单最小Cube明细_{}.csv'.format(str_time)), index=False, na_rep='Null')


if __name__ == '__main__':

    # print('\n')
    # startTime = datetime.now()
    # print('-' * 20 + '程序开始' + '-' * 20 + '\n')
    #
    # # 谷仓现有6种箱型
    # # size1 = (19, 14, 9)
    # # size2 = (29, 19, 14)
    # # size3 = (34, 24, 19)
    # # size4 = (39, 29, 19)
    # # size5 = (49, 39, 29)
    # # size6 = (59, 39, 29)
    # #
    # # ctn_list = [size1, size2, size3, size4, size5, size6]
    # # ctn_list = (19, 14, 9)
    #
    # # 文件路径
    # file_path = 'D:/Documents/Desktop/箱型推荐/'
    #
    # # file_name = 'multiQty_3.csv'
    # # file_name = 'multiQtyOrderWithArea_12&3.csv'
    # # file_name = '全球4月_多件单.csv'
    # file_name = 'targetCustomer.csv'
    #
    # carton_type = '目标客户'
    # carton_file_name = 'Mixed carton size_欧洲.csv'
    #
    #
    # order_df = load_data(file_path, file_name, isMulti=False)
    # carton_list , ctn_dict, ctn_df = load_carton(file_path, carton_file_name)
    #
    # # 计算匹配箱型及最小cube
    # # run_packing(order_df=order_df, ctn_df=ctn_df, ctn_list=carton_list, file_path=file_path, ctn_dict=ctn_dict, carton_type=carton_type, isCalcuMinCube=False)
    #
    # # 计算订单匹配的最小cube
    # run_min_cube(order_df=order_df, file_path = file_path)
    #
    # print('\n')
    # print('='*15, '订单数据预览', '='*15)
    # print(order_df.head(10))
    #
    #
    # print('-' * 20 + '程序运行完成！' + '-' * 20 + '\n')
    # endTime = datetime.now()
    # print('-' * 50)
    # print('程序运行总时间：', (endTime - startTime).seconds, ' S')

    # pack = Packing(pltSize)
    # pack.run()

    # sku_list = [(33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0),
    #             (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0),
    #             (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0),
    #             (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0)]

    sku_list = [(51,41,28), (51,41,28),(51,41,28),(51,41,28),(51,41,28)]
    #
    # cube = (52, 52, 49)
    #
    # ratio = packing(sku_list, cube)
    # print('满箱率： ', ratio)

    c = minCube(skuList=sku_list, show=True)
    print('sku list: ', sku_list)
    print('minimal cube: ', c)







