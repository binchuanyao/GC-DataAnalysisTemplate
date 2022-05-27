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
import decimal
from collections import Counter


class Packing():
    def __init__(self, plt=None, ctnList=None):
        if plt is None:
            self.pltSize = (120, 100, 160)
        else:
            self.pltSize = plt

        if ctnList is None:
            self.ctnList = [(20, 20, 10) for num in range(50)]
        else:
            self.ctnList = ctnList

        self.skuNum = len(ctnList)
        self.packedNum = 0

        self.containerVol = self.pltSize[0] * self.pltSize[1] * self.pltSize[2]
        self.boxVol = 0
        self.ratio = 0

        self.used_point = [] # 已用sku放置点，即第i个sku的坐标


        # 最小cube
        self.cube = (0, 0, 0)

        print('===== current Carton: ', self.pltSize)
        print('===== current Box list: ', self.ctnList)

    def run(self, show=False):

        O = (0, 0, 0)  # 原点坐标
        show_num = [self.make(O, self.pltSize, 'red')]

        # 2.给定有限量个方体 500个(60,40,50)的方体，当方体大小存在差异时，我们将按照体积大小降序排列，优先摆放大体积的
        # B = [(50, 20, 60) for num in range(0, 100)]

        # print('self.ctnList: ', self.ctnList)
        # 把货物第一次装箱
        O_items, O_pop = self.packing3D(show_num, (0, 0, 0), self.pltSize, self.ctnList, 'blue')
        print('11111111111  packing3D results O_items', O_items)
        print('11111111111  packing3D results O_pop',  O_pop)

        # 放置货物的朝向
        face = ['acb', 'bac', 'bca', 'cab', 'cba']

        # 把剩下的货物分出来

        for f in face:

            print('2222222222222: before B2', self.ctnList)
            B2 = self.surplus(self.packedNum, self.ctnList, f)
            # B2 = self.surplus(Plan1[0], self.ctnList, 'bc')
            print('2222222222222: B2', B2)

            # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
            self.twice(show_num=show_num, O_pop=O_pop, C=self.pltSize, Box_list=B2, color='orange')

            if self.packedNum == self.skuNum:
                break

            # print('2222222222222  Plan1: ', Plan1)

        self.ratio = self.boxVol / self.containerVol

        print('2222222222222  show_num: ', show_num)

        # 添加最小cube图显信息
        show_num.append(self.make(O, self.cube, 'green'))

        if show:
            self.make_pic(show_num)

        print('装箱件数： ', self.packedNum)
        print('满箱率： ', self.ratio)
        print('订单适配的最小Cube: ', self.cube)
        print('最小Cube满箱率: ', self.boxVol/(self.cube[0]*self.cube[1]*self.cube[2]))



    #make_pic内置函数
    def box(self, ax,x, y, z, dx, dy, dz, color='red'):
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

    # 显示图形的函数：Items = [[num[0],num[1],num[2],num[3],num[4],num[5],num[6]],]
    def make_pic(self, Items):
        fig = plt.figure()
        ax = Axes3D(fig)
        # ax.xaxis.set_major_locator(MultipleLocator(50))
        # ax.yaxis.set_major_locator(MultipleLocator(50))
        # ax.zaxis.set_major_locator(MultipleLocator(50))


        Xmax = (int(max(Items[0][0:6]) / 10) + 1) * 10   # xyz最大刻度为纸箱最长边
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
            self.box(ax, num[0], num[1], num[2], num[3], num[4], num[5], num[6])
        plt.show()

    #把尺寸数据生成绘图数据
    def make(self, O, C, color):
        data = [O[0],O[1],O[2],C[0],C[1],C[2], color]
        return data

    def geneMinCube(self, O, sku):
        current = [ round(i + j , 2) for i, j in zip(O, sku)]
        self.cube = tuple([max(i, j) for i, j in zip(self.cube, current)])


    #可用点的生成方法
    def newsite(self, O, B_i):
        # 在X轴方向上生成
        O1 = (O[0]+B_i[0],O[1],O[2])
        # 在Y轴方向上生成
        O2 = (O[0],O[1]+B_i[1],O[2])
        # 在Z轴方向上生成
        O3 = (O[0],O[1],O[2]+B_i[2])
        return [O3, O2, O1]

    def newsite1(self, O_items, O, B_i):  # O_items为可用点列表，O为当前放置点，B_i为放入货位的尺寸
        # 在X轴方向上生成
        O1 = (O[0] + B_i[0], O[1], O[2])
        if O1 not in O_items and O[1] == 0 and O[2] == 0:
            O_items.append(O1)
        # 在Y轴方向上生成
        O2 = (O[0], O[1] + B_i[1], O[2])
        if O2 not in O_items:
            O_items.append(O2)
        # 在Z轴方向上生成
        O3 = (O[0], O[1], O[2] + B_i[2])
        if O3 not in O_items:
            O_items.append(O3)
        # 这里加入一步排序，让我们优先级的放置点排到前面先被使用
        return sorted(O_items, key=lambda x: (x[0], x[2], x[1]))


    #3.拟人化依次堆叠方体, 返回已码数量、放置点，弃用点
    def packing3D(self, show_num, O, C, Box_list, color):
        O_items = [O]
        O_pop = []
        for i in range(len(Box_list)):
            #货物次序应小于等于可用点数量，如：第四个货物i=3，使用列表内的第4个放置点O_items[3]，i+1即常见意义的第几个，len即总数，可用点总数要大于等于目前个数
            if i+1 <= len(O_items):
                #如果放置点放置货物后，三个方向都不会超过箱体限制,则认为可以堆放

                if O_items[i-1][0]+Box_list[i][0]<=C[0] and O_items[i-1][1]+Box_list[i][1]<=C[1] and O_items[i-1][2]+Box_list[i][2]<=C[2]:
                    #使用放置点，添加一个图显信息
                    new_show = self.make(O_items[i-1], Box_list[i], color)

                    if new_show not in show_num:
                        # print('1 new_show: ', new_show)
                        show_num.append(self.make(O_items[i-1],Box_list[i], color))
                        self.make_pic(show_num)
                        self.geneMinCube(O_items[i - 1], Box_list[i])

                        self.used_point.append(O_items[i-1])   # 在已用点列表中增加当前图显点
                        # 计数加1
                        print('222 current Box: ', Box_list[i])

                        self.packedNum += 1
                        self.boxVol += Box_list[i][0] * Box_list[i][1] * Box_list[i][2]

                    ### 把堆叠后产生的新的点，加入放置点列表
                    for new_O in self.newsite(O_items[i-1],Box_list[i]):
                        #保证放入的可用点是不重复的
                        if new_O not in O_items:
                            O_items.append(new_O)

                    # O_items = self.newsite1(O_items, O_items[i-1], Box_list[i])

                    # 将已用点从放置点列表中删除
                    O_items = list(filter(lambda x: x not in self.used_point, O_items))


                    # O_items.pop(i)  # 当前放置点若已堆叠，则弹出当前点
                    # print('----------2222放置点：', O_items)


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
                            new_show = self.make(O_items[i-1],Box_list[i], color)
                            if new_show not in show_num:
                                show_num.append(self.make(O_items[i-1],Box_list[i], color))
                                self.make_pic(show_num)
                                self.geneMinCube(O_items[i - 1], Box_list[i])
                                self.used_point.append(O_items[i - 1])  # 在已用点列表中增加当前图显点
                                #计数加1
                                # print('2 self.packedNum: ', self.packedNum)
                                print('3 current Box: ', Box_list[i])

                                self.packedNum +=  1
                                self.boxVol += Box_list[i][0] * Box_list[i][1] * Box_list[i][2]

                            ## 把堆叠后产生的新的点，加入放置点列表
                            for new_O in self.newsite(O_items[i-1],Box_list[i]):
                                #保证放入的可用点是不重复的
                                if new_O not in O_items:
                                    O_items.append(new_O)

                            # O_items = self.newsite1(O_items, O_items[i - 1], Box_list[i])
                            # 将已用点从放置点列表中删除
                            O_items = list(filter(lambda x: x not in self.used_point, O_items))

        return O_items,O_pop

    #<<<---写一个函数专门用来调整方向和计算剩余货物
    def surplus(self,num, Box_list,change):#change='ab','bc','ac',0有三组对调可能，共6种朝向
        # new_Box_list = Box_list[num-1:-1]
        new_Box_list = Box_list[num:]

        if num == 0:
            new_Box_list = Box_list
        if change == 'bac':
            for i in range(0,len(new_Box_list)):
                new_Box_list[i]=(new_Box_list[i][1],new_Box_list[i][0],new_Box_list[i][2])
        elif change == 'acb':
            for i in range(0,len(new_Box_list)):
                new_Box_list[i]=(new_Box_list[i][0],new_Box_list[i][2],new_Box_list[i][1])
        elif change == 'cab':
            for i in range(0,len(new_Box_list)):
                new_Box_list[i]=(new_Box_list[i][2],new_Box_list[i][0],new_Box_list[i][1])
        elif change == 'cba':
            for i in range(0,len(new_Box_list)):
                new_Box_list[i]=(new_Box_list[i][2],new_Box_list[i][1],new_Box_list[i][0])
        elif change == 'bca':
            for i in range(0,len(new_Box_list)):
                new_Box_list[i]=(new_Box_list[i][1],new_Box_list[i][2],new_Box_list[i][0])
        elif change == 0:
            return new_Box_list
        else:
            return new_Box_list
        return new_Box_list

    # Plan1:  (1, [], [(35.8, 0, 0), (0, 12.0, 0), (0, 0, 8.3)])

    #残余点二次分配函数
    def twice(self, show_num,O_pop,C,Box_list, color):
        for a2 in O_pop:
            if a2[0]==0 and a2[1]==0:
                print('111 O_pop: ', O_pop)
                Plan = self.packing3D(show_num,a2,C,Box_list, color)
                # Box_list = self.surplus(self.packedNum,Box_list,0)
            elif a2[1]==0 and a2[2]==0:
                print('222 O_pop: ', O_pop)
                Plan = self.packing3D(show_num,a2,C,Box_list, color)
                # Box_list = self.surplus(self.packedNum,Box_list,0)
            elif a2[0]==0 and a2[2]==0:
                print('333 O_pop: ', O_pop)
                Plan = self.packing3D(show_num,a2,C,Box_list, color)
                # Box_list = self.surplus(self.packedNum,Box_list,0)
        return Box_list


class PackingImprove():
    def __init__(self, ctn=None, skuList=None):
        if ctn is None:
            self.ctn = (120, 100, 160)
        else:
            self.ctn = ctn

        if skuList is None:
            self.skuList = [(20, 20, 10) for num in range(50)]
        else:
            self.skuList = skuList

        self.skuNum = len(self.skuList)
        self.packedNum = 0

        self.ctnVol = self.ctn[0] * self.ctn[1] * self.ctn[2]
        self.packedVol = 0
        self.ratio = 0

        self.used_point = [] # 已用sku放置点，即第i个sku的坐标
        self.placed_sku = []  # 已装sku


        # 最小cube
        self.cube = (0, 0, 0)

        print('===== current Carton: ', self.ctn)
        print('===== current Box list: ', self.skuList)
        # print('===== minimal cube: ', self.cube)


    def run(self, show=False):

        # 添加箱型的图显信息
        show_num = [self.make((0,0,0), self.ctn, 'red')]

        # 调用三维装箱算法，计算sku列表是否能装入指定纸箱
        self.packing3D_improve(show_num, self.ctn, self.skuList)

        # 判断是否已全部装入纸箱，是则计算满箱率
        if self.packedNum == self.skuNum:
            self.ratio = self.packedVol / self.ctnVol
            print('装箱件数： ', self.packedNum)
            print('满箱率： ', self.ratio)
            print('订单适配的最小Cube: ', self.cube)
            print('最小Cube满箱率: ', self.packedVol / (self.cube[0] * self.cube[1] * self.cube[2]))

            # 添加最小cube图显信息
            show_num.append(self.make((0,0,0), self.cube, 'green'))

            # 根据show参数，判断是否显示图片
            if show:
                self.make_pic(show_num)

            return self.ratio

        else:
            print('目标箱型尺寸： ', self.ctn)
            print('订单sku列表： ', self.skuList)
            print('订单总件数： ', self.skuNum, '已装件数', self.packedNum)
            print('='*15, '当前订单无法匹配目标箱型!', '='*15)
            return 0


    #make_pic内置函数
    def box(self, ax,x, y, z, dx, dy, dz, color='red'):
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

    # 显示图形的函数：Items = [[num[0],num[1],num[2],num[3],num[4],num[5],num[6]],]
    def make_pic(self, Items):
        fig = plt.figure()
        ax = Axes3D(fig)
        # ax.xaxis.set_major_locator(MultipleLocator(50))
        # ax.yaxis.set_major_locator(MultipleLocator(50))
        # ax.zaxis.set_major_locator(MultipleLocator(50))


        Xmax = (int(max(Items[0][0:6]) / 10) + 1) * 10   # xyz最大刻度为纸箱最长边
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
            self.box(ax, num[0], num[1], num[2], num[3], num[4], num[5], num[6])
        plt.show()

    #把尺寸数据生成绘图数据
    def make(self, O, C, color):
        data = [O[0],O[1],O[2],C[0],C[1],C[2], color]
        return data

    def geneMinCube(self, O, sku):
        current = [ round(i + j , 2) for i, j in zip(O, sku)]
        self.cube = tuple([max(i, j) for i, j in zip(self.cube, current)])

    def distance(self, x):  # 返回与原点的欧式距离
        return x[0]*x[0] + x[1]*x[1] + x[2]*x[2]

    #可用点的生成方法
    def newsite(self, O, B_i):
        # 在X轴方向上生成
        O1 = (O[0]+B_i[0],O[1],O[2])
        # 在Y轴方向上生成
        O2 = (O[0],O[1]+B_i[1],O[2])
        # 在Z轴方向上生成
        O3 = (O[0],O[1],O[2]+B_i[2])
        return [O3, O2, O1]

    def newsite1(self, O_items, O, B_i):  # O_items为可用点列表，O为当前放置点，B_i为放入货位的尺寸
        # 在X轴方向上生成
        O1 = (O[0] + B_i[0], O[1], O[2])
        if O1 not in O_items and O[1] == 0 and O[2] == 0:
            O_items.append(O1)
        # 在Y轴方向上生成
        O2 = (O[0], O[1] + B_i[1], O[2])
        if O2 not in O_items:
            O_items.append(O2)
        # 在Z轴方向上生成
        O3 = (O[0], O[1], O[2] + B_i[2])
        if O3 not in O_items:
            O_items.append(O3)
        # 这里加入一步排序，让我们优先级的放置点排到前面先被使用
        return sorted(O_items, key=lambda x: (x[0], x[2], x[1]))

    def clear_newsite3(self, O_items):
        '''
        清除多余的放置点，即每个轴线及平面上只可能存在一个放置点，第一象限内可存在多个放置点
        :param O_items: 原始放置点
        :return: 清除覆盖点后的放置点
        '''

        O_items = list(set(O_items))  # 初始点去重

        # 3条轴线上的点
        X_axis = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] == 0]
        Y_axis = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] == 0]
        Z_axis = [i for i in O_items if i[0] == 0 and i[1] == 0 and i[2] != 0]

        O_items = list(filter(lambda x: x not in X_axis and x not in Y_axis and x not in Z_axis, O_items))
        print('放置点数量： ', len(O_items), '去掉轴线上的点： ', O_items)

        # 3个平面上的点
        # XOY = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] == 0]
        # XOZ = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] != 0]
        # YOZ = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] != 0]

        # O_items = list(filter(lambda x: x not in X_axis and x not in Y_axis and x not in Z_axis, O_items))
        # print('去掉轴线上的点： ', O_items)

        # 找出存在2个轴相等的点的组合
        equal_XY = [item for item, count in Counter(x[0:2] for x in O_items).items() if count > 1]  # XY相等的点组合
        equal_YZ = [item for item, count in Counter(x[1:] for x in O_items).items() if count > 1]  # YZ相等的点组合
        equal_XZ = [item for item, count in Counter((x[0], x[2]) for x in O_items).items() if count > 1]  # XZ相等的点组合

        # 轴线及平面上的点
        axis = [X_axis, Y_axis, Z_axis]
        # plane = [XOY, YOZ, XOZ, other]
        # current = [X_axis, Y_axis, Z_axis]

        new_O_items = []

        # 轴线上取最大的点
        for i in axis:
            if len(i) > 0:  # 列表不为空时才取最大值
                new_O_items.append(self.get_max_point(i))

        # 去除轴线上的点
        O_items = [x for x in O_items if x not in X_axis and x not in Y_axis and x not in Z_axis]

        # 当放置点有2边相等时，取第三边更大的点，第三边小的点已被覆盖
        for point in equal_XY:
            temp = list(filter(lambda x: x[0:2] in [point], O_items))
            print('--------000000 XY相等： ', temp)
            O_items = [x for x in O_items if x not in temp]
            if len(temp) > 0:
                new_O_items.append(max(temp))  # 有两边相等，取第三边最大值，即取整个列表的最大值
            print('--------000000 O_items 数量： ', len(O_items))

        for point in equal_YZ:
            temp = list(filter(lambda x: x[1:] in [point], O_items))
            print('--------111111 YZ相等： ', temp)
            O_items = [x for x in O_items if x not in temp]
            if len(temp) > 0:
                new_O_items.append(max(temp))  # 有两边相等，取第三边最大值，即取整个列表的最大值
            print('--------111111 O_items 数量： ', len(O_items))

        for point in equal_XZ:
            temp = list(filter(lambda x: (x[0], x[2]) in [point], O_items))
            print('--------222222 XZ相等： ', temp)
            O_items = [x for x in O_items if x not in temp]
            if len(temp) > 0:
                new_O_items.append(max(temp))  # 有两边相等，取第三边最大值，即取整个列表的最大值
            print('--------222222 O_items 数量： ', len(O_items))

        # 平面上只保留最小的点，即最靠左下的点
        # for j in plane:
        #     if len(j)>0:  # 列表不为空时才取最大值
        #         print('当前平面上的点：', j)
        #         new_O_items.append(self.get_min_point(j))

        # for j in plane:
        #     if len(j)>0:
        #         j = sorted(j, key=lambda x: (x[2], x[0], x[1]))
        #         for p in j:
        #             new_O_items.append(p)

        # other = sorted(other, key=lambda x: (x[2], x[1], x[2]))
        # for point in other:
        #     new_O_items.append(point)

        O_items = sorted(O_items, key=lambda x: (x[2], x[1], x[0]))
        if len(O_items) > 0:
            for p in O_items:
                new_O_items.append(p)

        new_O_items = list(set(new_O_items))
        new_O_items = sorted(new_O_items)
        print('in clear: ', new_O_items)

        return new_O_items


    def get_max_point(self, matrix):
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



    #3.拟人化依次堆叠方体, 返回已码数量、放置点，弃用点
    def packing3D_improve(self, show_num, C, sku_list):
        '''
        按朝向和放置点，遍历搜索是否能放入
        :param show_num: 图显信息
        :param C: 待装纸箱
        :param sku_list: sku列表
        :return:
        '''
        original = (0,0,0)  #初始放置点为 原点（0,0,0)
        O_items = [original]
        # 放置货物的朝向
        # face = ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
        # face = ['abc', 'bac', 'acb']
        color_dict = {'abc': 'blue', 'bac': 'orange', 'acb': 'yellow'}

        for i in range(len(sku_list)):
            # 遍历SKU的可选朝向, 每换一个sku, face重新初始化
            face = ['abc', 'bac', 'acb']
            for choose_face in face:
                curr_sku = self.exchange(sku_list[i], choose_face)

                for point in O_items:

                    # 判断如果当前放置点及朝向有重叠，则跳过
                    isOverlapFlag = 0
                    if len(self.placed_sku) > 0:
                        for j in range(len(self.used_point)):
                            if self.isOverlap(point, curr_sku, self.used_point[j], self.placed_sku[j]):
                                isOverlapFlag += 1

                    if isOverlapFlag > 0:
                        continue
                    # 如果放置点放置货物后，三个方向都不会超过箱体限制,则认为可以堆放
                    elif point[0]+curr_sku[0]<=C[0] and point[1]+curr_sku[1]<=C[1] and point[2]+curr_sku[2]<=C[2]:
                        #使用放置点，添加一个图显信息
                        new_show = self.make(point, curr_sku, color_dict[choose_face])

                        if new_show not in show_num:
                            # print('1 new_show: ', new_show)
                            show_num.append(new_show)
                            self.make_pic(show_num)
                            self.used_point.append(point)      # 在已用点列表中增加当前放置点
                            self.placed_sku.append(curr_sku)   # 在已放sku列表中增加当前sku
                            # 计数加1
                            print('222 current face: ', choose_face,  '222 current Box: ', curr_sku)

                            self.packedNum += 1
                            self.packedVol += curr_sku[0] * curr_sku[1] * curr_sku[2]
                            self.geneMinCube(point, curr_sku)

                            ## 把堆叠后产生的新的点，加入放置点列表
                            for new_O in self.newsite(point, curr_sku):
                                # 保证放入的可用点是不重复的
                                if new_O not in O_items:
                                    O_items.append(new_O)

                            # 将已用点从放置点列表中删除
                            O_items = list(filter(lambda x: x not in self.used_point, O_items))
                            O_items = sorted(O_items, key=lambda x: self.distance(x))   # 按与原点的距离升序排列，优先使用靠近原点的点

                            # if len(O_items) > 1:
                            #     O_items = self.clear_newsite3(O_items)

                        # 如果当前sku能放入，则跳出选点的循环
                        break

                # 如果已装数量 大于当前列表index+1，表示当前sku已经装入，跳出旋转的循环
                if self.packedNum >= i+1:
                    break


    def geneMinCube(self, O, sku):
        current = [ round(i + j , 2) for i, j in zip(O, sku)]
        self.cube = tuple([max(i, j) for i, j in zip(self.cube, current)])

    def distance(self, x):  # 返回与原点的欧式距离
        return x[0]*x[0], x[1]*x[1], x[2]*x[2]


    def exchange(self, sku, change):  # change='abc','acb','bac','bca','cba','cab' 有6种对调可能，默认为abc
        if change == 'abc':
            return sku
        elif change == 'acb':
            return (sku[0], sku[2], sku[1])
        elif change == 'bac':
            return (sku[1], sku[0], sku[2])
        elif change == 'bca':
            return (sku[0], sku[2], sku[1])
        elif change == 'cba':
            return (sku[2], sku[1], sku[0])
        elif change == 'cab':
            return (sku[2], sku[0], sku[1])
        else:
            return sku

    def isOverlap(self, aCoord, aSize, bCoord, bSize):
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




class MinCube():
    def __init__(self, skuList=None):
        if skuList is None:
            self.skuList = [(20, 20, 10) for num in range(10)]
        else:
            self.skuList = skuList

        self.skuList = self.sortList(self.skuList)

        self.skuVol = 0
        self.ratio = 0
        self.used_point = []  # 已用放置点
        self.placed_sku = []  # 已装sku
        self.placedVol = 0    # 已装sku总体积

        self.skuRatio = 0   # 货物体积
        self.fitRatio = 0   # 立方体拟合体积
        self.flag = False
        self.MINCUBE = (0,0,0)

        for sku in skuList:
            self.skuVol += sku[0]*sku[1]*sku[2]

        # 最小cube
        self.cube = (0, 0, 0)
        self.cubeVol = 0


    def run(self, show=True):
        O = (0, 0, 0)  # 原点坐标
        show_num = []
        if set(self.skuList) ==1:
            self.minCubeForSingleSKU(show_num=show_num, O=O, skuList=self.skuList, color='blue')
        else:
            self.packingMinCube(show_num=show_num, O=O, skuList=self.skuList, color='blue')

        # 添加最小cube图显信息
        show_num.append(self.make(O, self.cube, 'green'))

        print('SKU list: ', self.skuList)
        print('Min cube:', sorted(self.cube, reverse=True))
        print('最小Cube满箱率: ', self.skuVol / (self.cube[0] * self.cube[1] * self.cube[2]))


        if show:
            self.make_pic(show_num, max(self.cube))



    def packingMinCube(self, show_num, O, skuList, color):
        O_items = [O]

        # 初始化最小cube为第一个sku
        self.cube = skuList[0]
        self.cubeVol = skuList[0][0] * skuList[0][1] * skuList[0][2]
        show_num.append(self.make(O_items[0], skuList[0], color))
        self.make_pic(Items=show_num, maxSize=70)
        # 把堆叠后产生的新的点，加入放置点列表
        for new_O in self.newsite(O_items[0], skuList[0]):
            # 保证放入的可用点是不重复的
            if new_O not in O_items:
                O_items.append(new_O)

        # 更新属性
        self.used_point.append(O)
        self.placed_sku.append(skuList[0])
        self.placedVol += skuList[0][0] * skuList[0][1] * skuList[0][2]


        # self.skuRatio = self.placedVol / self.skuVol  # 当前已装体积/总体积

        '''试算类三菱锥和立方体比例'''
        # self.skuRatio = skuList[0][0] * skuList[0][1] * skuList[0][2] / self.placedVol  # 当前sku体积/已装体积
        # self.fitRatio = (1/3)*(1/2) * self.cubeVol / max(self.cube) * max(self.cube) * max(self.cube)   # 当前类三菱锥体积/当前最大立方体
        # if self.skuRatio > self.fitRatio:
        #     self.flag = True

        # 将已用点从放置点列表中删除
        O_items = list(filter(lambda x: x not in self.used_point, O_items))

        # 放置货物的朝向
        face = ['abc','acb','bac','bca','cab', 'cba']

        # 第2到最后一个SKU
        for i in range(1, len(skuList)):
            # 初始化cube为三边叠加的最大立方体
            curr_sku = skuList[i]
            choose_point = O_items[0]
            choose_face = 'abc'
            # # 每增加一个货物，初始化当前cube为最大立方体
            # curr_cube_vol = (self.cube[0] + curr_sku[0]) * (self.cube[1] + curr_sku[1]) * (self.cube[2] + curr_sku[2])

            # 新增加一个货物，初始化当前cube为最大cube
            curr_cube = (self.cube[0]+curr_sku[0], self.cube[1]+curr_sku[1], self.cube[2] + curr_sku[2])
            curr_cube = tuple(sorted(curr_cube, reverse=True))  # 按三边长度重排序
            curr_cube_vol = curr_cube[0] * curr_sku[1] * curr_sku[2]

            for point in O_items:
                for f in face:
                    curr_sku = self.exchange(skuList[i], f)
                    # print('point: ', point, 'curr_sku: ', curr_sku)

                    # 判断选择当前放置点会否与其他SKU重合
                    isOverlapFlag = 0
                    for k in range(len(self.used_point)):
                        if self.isOverlap(point, curr_sku, self.used_point[k], self.placed_sku[k]):
                            isOverlapFlag += 1

                    if isOverlapFlag>0:  # 如果当前放置点及朝向有重叠，则跳过
                        continue
                    else:
                        c, v = self.geneMinCube(point, curr_sku)

                        '''
                        评价指标
                        1. 体积最小 → 达到某一临界值之后，只往一边延伸
                        2. 表面积最小 
                        3. 三边之和最小 → 达到某一临界值之后，跟放置点的选择相关，延长的边相同时和不变，不会更新值
                        4. 最长边最小  → 均匀的往三边延伸
                        '''

                        # if v < curr_cube_vol and v < curr_cube_vol and max(c) < max(curr_cube):    # 1.体积&最长边最小
                        # if c[0]*c[1]+c[0]*c[2]+c[1]*c[2] < curr_cube[0]*curr_cube[1]+curr_cube[0]*curr_cube[2]+curr_cube[1]*curr_cube[2]:  # 2.表面积最小

                        sum_c = c[0] + c[1] + c[2]
                        sum_current = curr_cube[0] + curr_cube[1] + curr_cube[2]

                        # if sum_c < sum_current:       # 3.三边之和最小
                        if max(c) < max(curr_cube):     # 4.最长边最小
                            # 判断在当前放置点会否与其他SKU重合
                            choose_point = point
                            choose_face = f
                            curr_cube_vol = v
                            curr_cube = c
                        # elif sum_c == sum_current and max(c) < max(curr_cube):
                        #     choose_point = point
                        #     choose_face = f
                        #     curr_cube_vol = v
                        #     curr_cube = c


            curr_placed_sku = self.exchange(skuList[i], choose_face)
            # print('choose point: ', choose_point, 'curr_sku: ', curr_placed_sku)
            show_num.append(self.make(choose_point, curr_placed_sku, color))
            self.make_pic(show_num, 60)
            # 添加新的放置点
            for j in self.newsite(choose_point, curr_placed_sku):
                O_items.append(j)

            # 更新属性
            self.used_point.append(choose_point)
            self.placed_sku.append(curr_placed_sku)
            self.placedVol += curr_placed_sku[0] * curr_placed_sku[1] * curr_placed_sku[2]

            # self.skuRatio = self.placedVol / self.skuVol  # 当前已装体积/总体积
            # self.skuRatio = curr_placed_sku[0] * curr_placed_sku[1] * curr_placed_sku[2] / self.placedVol  # 当前sku体积/已装体积
            # self.fitRatio = ((1 / 3) * (1 / 2) * self.cubeVol) / (max(self.cube) * max(self.cube) * max(self.cube))  # 当前类三菱锥体积/当前最大立方体

            # if self.skuRatio < self.fitRatio:  # 当sku比例大于拟合比例时
            #     self.flag = True

            # if self.flag:
            #     self.MINCUBE = self.cube   # 当两个比较出现交叉时，记录当前cube，作为试装箱型

            self.cube = self.geneMinCube(choose_point, curr_placed_sku)[0]
            self.cubeVol = curr_cube_vol

            O_items = list(filter(lambda x: x not in self.used_point, O_items))
            O_items = sorted(O_items, key=lambda x: self.distance(x))  # 按与原点的距离升序排列，优先使用靠近原点的点
            # 清理覆盖点
            # print('------------000 当前放置点：', choose_point)
            # print('------------000 已用放置点：', self.used_point)
            # print('------------111 清理前：', O_items)
            # if len(O_items)>1:
            #     O_items = self.clear_newsite(O_items)
            # print('------------222 清理后：', O_items)
            # print('--------------第{}个sku'.format(i+2), O_items)

    def minCubeForSingleSKU(self, show_num, O, skuList, color):
        '''
        单品多件根据sku列表生成最小cube
        :param skuList:sku列表，sku为元组形式
        :return: 最小Cube, permutation [1,2,0,5] 第0个元素*第1个元素+第2个元素=每层摆放数量，第3个元素为摆放层数
        '''

        N = len(skuList)  # 单品件数
        l, w, h = skuList[0][0], skuList[0][1], skuList[0][2]
        permutation = [1, 1, 0, N]
        # 如果高叠加的最长边小于SKU最长边，则高叠加最优
        if h * N <= l:
            return tuple(sorted((l, w, h * N), reverse=True))
        # 高叠加最长边超过SKU长
        else:
            # 初始化cube为高叠加的L，W，H
            cube = [l, w, h * N]

            for num in range(2, N):
                if np.mod(N, num) == 0:
                    layer = int(N / num)  # 放的层数
                else:
                    layer = int(N / num) + 1
                curr_cube = [0, 0, h * layer]
                # 每一层放的sku数量num已定时，初始化平面的长和宽
                groups = self.crack(num)
                # print('每层个数： ', num, '\t摆放组合： ', groups)
                for group in groups:
                    if group[2] == 0:  # 能摆成矩形, 其中group为3个元素的列表，group[0]<=group[1]， group[2]为剩余数量
                        curr_cube[0] = max(l * min(group[0:2]), w * max(group[0:2]))
                        curr_cube[1] = min(l * min(group[0:2]), w * max(group[0:2]))
                    else:  # 不能摆成矩形, 有剩余的rect
                        # 先确定能摆成矩形部分的形状——大矩形
                        tempL = max(l * min(group[0:2]), w * max(group[0:2]))  # 长边
                        tempW = min(l * min(group[0:2]), w * max(group[0:2]))  # 短边

                        # 判断多出的rect是否能旋转放置, 如果旋转后表面积更小，则旋转放置
                        if l * group[2] <= tempL and (tempL + w) * tempW < tempL * (tempW + w):
                            curr_cube[0] = tempL + w
                            curr_cube[1] = tempW
                        # 不旋转剩余的rect
                        elif (tempL + l) * tempW < tempL * (tempW + w):
                            curr_cube[0] = tempL + l  # 多余的rect加在长边
                            curr_cube[1] = tempW
                        else:
                            curr_cube[0] = tempL
                            curr_cube[1] = tempW + w  # 多余的rect加在短边
                    # print('每层个数： ', num, '摆放方式： ', group, 'cube: ', curr_cube)
                    if max(curr_cube) < max(cube):
                        cube = curr_cube
                        permutation[0:3] = group
                        permutation[3] = layer

        ## 返回最小cube和摆放方式
        self.cube = tuple(sorted(cube, reverse=True))



        # ## 返回最小cube和摆放方式
        # self.cube = tuple(sorted(cube, reverse=True))
        # return tuple(sorted(cube, reverse=True)), permutation



    def crack(self, integer):
        '''
        将正整数拆解成2数之积+余数 eg 10=2*5+0, 10=3*3+1
        :param integer:
        :return:
        '''
        sqrt_num = int(np.sqrt(integer))
        groups = []
        for n in range(1, sqrt_num + 1):
            factor = int(integer / n)
            remainder = np.mod(integer, n)
            groups.append([n, factor, remainder])
        return groups

    def isOverlap(self, aCoord, aSize, bCoord, bSize):
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




    def stackHeight(self, skuList):
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
        cube = tuple(sorted((L, W, H), reverse=True))
        return cube

    def exchange(self, sku, change): #change='abc','acb','bac','bca','cba','cab' 有6种对调可能，默认为abc
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

    # 可用点的生成方法
    def newsite(self, O, B_i):
        # 在X轴方向上生成
        O1 = (O[0] + B_i[0], O[1], O[2])
        # 在Y轴方向上生成
        O2 = (O[0], O[1] + B_i[1], O[2])
        # 在Z轴方向上生成
        O3 = (O[0], O[1], O[2] + B_i[2])
        # return [O1, O2, O3]
        return [O3, O2, O1]

    # 第三种衍生方法，不仅仅限制长方向上的衍生，也限制高方向的衍生
    # 在测试中发现，如果在高上继续衍生放置点，当后面的货物比前面小的时候，会因为前面更大的物体产生的悬空放置点发生重叠情况
    # 所以不限制高上衍生仅在前一个物体比后一个物体大的情况，其余情况限制只有在贴边时允许向上蔓延
    # 缺点是因为算力和逻辑严谨性，没有对比前后两个货物的高度差，也就是可能出现当前面的物体高度较大，后面当面的物体只摆了两层的情况
    def newsite3(self, current, O, B_i):
        # 在X轴方向上生成
        O1 = (O[0] + B_i[0], O[1], O[2])
        if O1 not in current and O[1] == 0 and O[2] == 0:
            current.append(O1)
        # 在Y轴方向上生成
        O2 = (O[0], O[1] + B_i[1], O[2])
        if O2 not in current:
            current.append(O2)
        # 在Z轴方向上生成
        O3 = (O[0], O[1], O[2] + B_i[2])
        if O3 not in current and O[1] == 0:
            current.append(O3)
        return sorted(current, key=lambda x: (x[0], x[2], x[1]))


    # make_pic内置函数
    def box(self, ax, x, y, z, dx, dy, dz, color='red'):
        xx = [x, x, x + dx, x + dx, x]
        yy = [y, y + dy, y + dy, y, y]
        kwargs = {'alpha': 1, 'color': color}
        ax.plot3D(xx, yy, [z] * 5, **kwargs)  # 下底
        ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)  # 上底
        ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
        ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
        ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
        ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)
        return ax

    # 显示图形的函数：Items = [[num[0],num[1],num[2],num[3],num[4],num[5],num[6]],]
    def make_pic(self, Items, maxSize):
        global fig
        fig = plt.figure()
        ax = Axes3D(fig)
        # ax.xaxis.set_major_locator(MultipleLocator(10))
        # ax.yaxis.set_major_locator(MultipleLocator(10))
        # ax.zaxis.set_major_locator(MultipleLocator(10))

        # ax.xaxis.set_units(10)
        # ax.yaxis.set_units(10)
        # ax.zaxis.set_units(10)

        Xmax = (int(maxSize/10) + 1)* 10
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
            self.box(ax, num[0], num[1], num[2], num[3], num[4], num[5], num[6])
        plt.show()


    def make_singe_pic(self, Item):  # 需添加的图案
        ax = Axes3D(fig)

        self.box(ax, Item[0], Item[1], Item[2], Item[3], Item[4], Item[5], Item[6])


    # 把尺寸数据生成绘图数据
    def make(self, O, C, color):
        data = [O[0], O[1], O[2], C[0], C[1], C[2], color]
        return data

    # 生成最小cube
    def geneMinCube(self, O, sku):
        current = [ round(i + j, 2) for i, j in zip(O, sku) ]
        cube = tuple([max(i, j) for i, j in zip(self.cube, current)])
        # cube = tuple(sorted(cube, reverse=True))
        vol = cube[0] * cube[1] * cube[2]
        return cube, vol

    def geneCurrCube(self, O, sku):
        current = [round(i + j, 2) for i, j in zip(O, sku)]
        cube = tuple([max(i, j) for i, j in zip(self.cube, current)])
        # cube = tuple(sorted(cube, reverse=True))
        vol = cube[0] * cube[1] * cube[2]
        return cube, vol

    def sortList(self, skuList):
        re = []
        for i in skuList:
            re.append(tuple(sorted(i, reverse=True)))
        return sorted(re, key=(lambda x:(x[0],x[1],x[2])),reverse=True)

    def clear_newsite(self, O_items):
        '''
        清除多余的放置点，即每个轴线及平面上只可能存在一个放置点，第一象限内可存在多个放置点
        :param O_items: 原始放置点
        :return: 清除覆盖点后的放置点
        '''
        # 3个平面上的点
        XOY = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] == 0]
        XOZ = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] != 0]
        YOZ = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] != 0]

        # 3条轴线上的点
        Z_axis = [i for i in O_items if i[0] == 0 and i[1] == 0 and i[2] != 0]
        Y_axis = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] == 0]
        X_axis = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] == 0]

        # 其他象限中的点
        other = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] != 0]

        # 轴线及平面上的点
        # current = [XOY, YOZ, XOZ, Z_axis, Y_axis, X_axis]

        # 其他象限中的点
        other = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] != 0]

        # 轴线及平面上的点
        current = [XOY, YOZ, XOZ, X_axis, Y_axis, Z_axis]
        # current = [Z_axis, Y_axis, X_axis, XOY, XOZ, YOZ]

        new_O_items = []
        for axis in current:
            if len(axis) > 0:  # 列表不为空时才取最大值
                new_O_items.append(self.get_max_point(axis))

        for point in other:
            new_O_items.append(point)

        return new_O_items


    def clear_newsite2(self, O_items):
        '''
        清除多余的放置点，即每个轴线及平面上只可能存在一个放置点，第一象限内可存在多个放置点
        :param O_items: 原始放置点
        :return: 清除覆盖点后的放置点
        '''

        O_items= list(set(O_items))  # 初始点去重

        # 3条轴线上的点
        X_axis = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] == 0]
        Y_axis = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] == 0]
        Z_axis = [i for i in O_items if i[0] == 0 and i[1] == 0 and i[2] != 0]


        ###  3个平面上的点
        XOY = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] == 0]
        XOZ = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] != 0]
        YOZ = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] != 0]

        XOY = sorted(XOY, key=lambda x: (x[0], x[1]))
        XOZ = sorted(XOZ, key=lambda x: (x[0], x[2]))
        YOZ = sorted(YOZ, key=lambda x: (x[1], x[2]))


        other = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] != 0]


        # 轴线及平面上的点
        axis = [X_axis, Y_axis, Z_axis]
        plane = [XOY, YOZ, XOZ]
        # current = [X_axis, Y_axis, Z_axis]

        new_O_items = []

        # 轴线上取最大的点
        for i in axis:
            if len(i)>0:  # 列表不为空时才取最大值
                new_O_items.append(self.get_max_point(i))

        # 平面上只保留最小的点，即最靠左下的点
        if len(XOY)>0:
            new_O_items.append(XOY[0])
        if len(XOZ) > 0:
            new_O_items.append(XOZ[0])
        if len(YOZ) > 0:
            new_O_items.append(YOZ[0])

        # 其他点按Z轴排序
        other = sorted(other, key=lambda x: (x[2], x[1], x[0]))
        for point in other:
            new_O_items.append(point)

        # new_O_items = list(set(new_O_items))
        # new_O_items = sorted(new_O_items)
        print('in clear: ', new_O_items)

        return new_O_items


    def clear_newsite3(self, O_items):
        '''
        清除多余的放置点，即每个轴线及平面上只可能存在一个放置点，第一象限内可存在多个放置点
        :param O_items: 原始放置点
        :return: 清除覆盖点后的放置点
        '''

        O_items = list(set(O_items))  # 初始点去重

        # 3条轴线上的点
        X_axis = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] == 0]
        Y_axis = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] == 0]
        Z_axis = [i for i in O_items if i[0] == 0 and i[1] == 0 and i[2] != 0]

        O_items = list(filter(lambda x: x not in X_axis and x not in Y_axis and x not in Z_axis, O_items))
        print('放置点数量： ', len(O_items), '去掉轴线上的点： ', O_items)

        # 3个平面上的点
        # XOY = [i for i in O_items if i[0] != 0 and i[1] != 0 and i[2] == 0]
        # XOZ = [i for i in O_items if i[0] != 0 and i[1] == 0 and i[2] != 0]
        # YOZ = [i for i in O_items if i[0] == 0 and i[1] != 0 and i[2] != 0]

        # O_items = list(filter(lambda x: x not in X_axis and x not in Y_axis and x not in Z_axis, O_items))
        # print('去掉轴线上的点： ', O_items)

        # 找出存在2个轴相等的点的组合
        equal_XY = [item for item, count in Counter(x[0:2] for x in O_items).items() if count > 1]  # XY相等的点组合
        equal_YZ = [item for item, count in Counter(x[1:] for x in O_items).items() if count > 1]  # YZ相等的点组合
        equal_XZ = [item for item, count in Counter((x[0], x[2]) for x in O_items).items() if count > 1]  # XZ相等的点组合

        # 轴线及平面上的点
        axis = [X_axis, Y_axis, Z_axis]
        # plane = [XOY, YOZ, XOZ, other]
        # current = [X_axis, Y_axis, Z_axis]

        new_O_items = []

        # 轴线上取最大的点
        for i in axis:
            if len(i) > 0:  # 列表不为空时才取最大值
                new_O_items.append(self.get_max_point(i))

        # 去除轴线上的点
        O_items = [x for x in O_items if x not in X_axis and x not in Y_axis and x not in Z_axis]

        # 当放置点有2边相等时，取第三边更大的点，第三边小的点已被覆盖
        for point in equal_XY:
            temp = list(filter(lambda x: x[0:2] in [point], O_items))
            print('--------000000 XY相等： ', temp)
            O_items = [x for x in O_items if x not in temp]
            if len(temp) > 0:
                new_O_items.append(max(temp))  # 有两边相等，取第三边最大值，即取整个列表的最大值
            print('--------000000 O_items 数量： ', len(O_items))

        for point in equal_YZ:
            temp = list(filter(lambda x: x[1:] in [point], O_items))
            print('--------111111 YZ相等： ', temp)
            O_items = [x for x in O_items if x not in temp]
            if len(temp) > 0:
                new_O_items.append(max(temp))  # 有两边相等，取第三边最大值，即取整个列表的最大值
            print('--------111111 O_items 数量： ', len(O_items))

        for point in equal_XZ:
            temp = list(filter(lambda x: (x[0], x[2]) in [point], O_items))
            print('--------222222 XZ相等： ', temp)
            O_items = [x for x in O_items if x not in temp]
            if len(temp) > 0:
                new_O_items.append(max(temp))  # 有两边相等，取第三边最大值，即取整个列表的最大值
            print('--------222222 O_items 数量： ', len(O_items))

        # 平面上只保留最小的点，即最靠左下的点
        # for j in plane:
        #     if len(j)>0:  # 列表不为空时才取最大值
        #         print('当前平面上的点：', j)
        #         new_O_items.append(self.get_min_point(j))

        # for j in plane:
        #     if len(j)>0:
        #         j = sorted(j, key=lambda x: (x[2], x[0], x[1]))
        #         for p in j:
        #             new_O_items.append(p)

        # other = sorted(other, key=lambda x: (x[2], x[1], x[2]))
        # for point in other:
        #     new_O_items.append(point)

        O_items = sorted(O_items, key=lambda x: (x[2], x[1], x[0]))
        if len(O_items) > 0:
            for p in O_items:
                new_O_items.append(p)

        new_O_items = list(set(new_O_items))
        new_O_items = sorted(new_O_items)
        print('in clear: ', new_O_items)

        return new_O_items


    def get_max_point(self, matrix):
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

    def get_min_point(self, matrix):
        '''
        得到矩阵中每一列最小的值
        '''
        res_list = []
        for j in range(3):
            one_list = []
            for i in range(len(matrix)):
                one_list.append(matrix[i][j])
            res_list.append(min(one_list))
        return tuple(res_list)

    def distance(self, x):  # 返回与原点的欧式距离
        return x[0]*x[0], x[1]*x[1], x[2]*x[2]



def load_data(file_path, file_name, ctn_list):
    if ".xlsx" in file_name:
        df = pd.read_excel('{}{}'.format(file_path, file_name))
    else:
        try:
            print('*' * 10, 'utf-8', '*' * 10)
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='utf-8')
        except:
            print('*' * 10, 'gbk-8', '*' * 10)
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='gbk')

    df['skuSize'] = df[['实际长cm', '实际宽cm', '实际高cm']].apply(tuple,axis=1)

    order_df = df.groupby('订单号')['skuSize'].apply(list).reset_index()
    order_df['qty'] = order_df['skuSize'].apply(len)

    print('订单数量： ', order_df.shape[0])

    order_df['ctnSize'] = np.NAN
    order_df['carton'] = np.NAN
    order_df['ratio'] = 0


    # 计算每个订单匹配的箱型
    for index, row in order_df.iterrows():
        sku_list = row['skuSize']
        # print('sku_list: ', sku_list)
        qty = int(row['qty'])

        ratio = 0.0
        for i in range(len(ctn_list)):
            pack = Packing(ctn_list[i], sku_list)
            pack.run()

            # 放入箱内的数量
            if pack.packedNum == qty:
                # print('能装下')
                if pack.ratio > ratio:
                    order_df.loc[index, ['ctnSize']] = 'size{}'.format(i+1)
                    order_df.loc[index, ['carton']] = str(ctn_list[i])
                    order_df.loc[index, ['ratio']] = pack.ratio
            # elif pack.packedNum == 0:
            #     row['ctnSize'] = '箱型太小'
            #     row['carton'] = None
            #     row['ratio'] = 0
            # elif pack.packedNum > qty:
            #     row['ctnSize'] = 'Error'
            #     row['carton'] = None
            #     row['ratio'] = 0
            # else:
            #     row['ctnSize'] = 'Null'
            #     row['carton'] = None
            #     row['ratio'] = 0

        order_df.to_csv('{}{}'.format(file_path, '装箱结果.csv'))
    return order_df



if __name__ == '__main__':
    # pltSize = (120, 100, 150)
    # ctnSize = (50, 20, 30)

    # draw = Draw(pltSize, ctnSize)
    # draw.run()

    # 谷仓现有6种箱型
    size1 = (19, 14, 9)
    size2 = (29, 19, 14)
    size3 = (34, 24, 19)
    size4 = (39, 29, 19)
    size5 = (49, 39, 29)
    size6 = (59, 39, 29)
    #
    # size_list = [size1, size2, size3, size4, size5, size6]

    # # 文件路径
    # file_path = 'D:/Documents/Desktop/箱型推荐/'
    #
    # # file_name = 'multiTest.csv'
    # file_name = 'multiOrder.csv'
    # # df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='utf-8')
    #
    # order_df = load_data(file_path, file_name, size_list)
    # print(order_df.head(10))
    #
    # order_df.to_csv(file_path)


    '''
    单个订单测试
    '''

    # sku_list = [(25.0, 20.0, 8), (15.0, 10.0, 5.5)]


    # sku_list = [(37.0, 34.0, 16.0), (30.0, 26.0, 8.0), (26.0, 11.0, 3.0)]

    # sku_list = [(45.7, 23.0, 4.3), (45.7, 23.0, 4.3), (45.7, 23.0, 4.3)]

    # sku_list = [(14.0, 13.0, 9.0), (14.0, 13.0, 9.0), (14.0, 13.0, 9.0), (14.0, 13.0, 9.0), (14.0, 13.0, 9.0)]

    # sku_list = [(33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0),
    #             (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0), (33.0, 18.0, 11.0),
    #             (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0),
    #             (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0), (19.0, 14.0, 5.0)]

    sku_list =[(21.0, 13.5, 4.8), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0),
    (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 4.0, 3.0), (8.0, 3.5, 3.5), (8.0, 3.5, 3.5),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0),
    (5.0, 2.0, 2.0), (5.0, 2.0, 2.0), (5.0, 2.0, 2.0)]


    size43 = (52, 52, 49.0)
    # size43 = (40.6, 22.9, 10.2)


    # ===================================
    # ============TESTING================
    # ===================================


    # pack1 = Packing(size5, sku_list.copy())
    # pack1.run(True)

    ### 装箱testing
    # pack2 = Packing(size43, sku_list.copy())
    # pack2.run(True)


    # ### 改进装箱testing
    # pack4 = PackingImprove(size43, sku_list.copy())
    # pack4.run(True)

    ## 最小cube Testing
    pack3 = MinCube(sku_list)
    pack3.run()


    ### 单品多件Testing
    # skuList = [(18, 16, 7), (18, 16, 7), (18, 16, 7), (18, 16, 7), (18, 16, 7),
    #             (18, 16, 7), (18, 16, 7), (18, 16, 7), (18, 16, 7), (18, 16, 7)]
    #
    #
    # pack4 = MinCube(skuList)
    # pack4.run()
    #
    # print('单品多件SKU： ', skuList)
    # print('单品多件的cube为： ', cube)






