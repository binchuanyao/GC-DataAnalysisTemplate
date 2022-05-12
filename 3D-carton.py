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

# class Draw():
#     def __init__(self, plt=None, ctnList=None):
#         if plt is None:
#             self.pltSize = (120, 100, 160)
#         else:
#             self.pltSize = plt
#
#         if ctnList is None:
#             self.ctnList = [(50, 20, 60) for num in range(0, 100)]
#         else:
#             self.ctnList = ctnList
#
#     def run(self):
#         # 1.给定空间容器C      4.2*1.9*1.8
#         # C = (120, 100, 160)  # 箱体长宽高
#         color = 'red'  # 箱体颜色
#
#         # 显示箱体
#         O = (0, 0, 0)  # 原点坐标
#         show_num = [self.make(O, self.pltSize, color)]
#
#         # 2.给定有限量个方体 500个(60,40,50)的方体，当方体大小存在差异时，我们将按照体积大小降序排列，优先摆放大体积的
#         B = [(50, 20, 60) for num in range(0, 100)]
#
#         # 把货物第一次装箱
#         Plan1 = self.packing3D(show_num, 'blue', (0, 0, 0), self.pltSize, self.ctnList)
#         # print(len(show_num))
#
#         # 把剩下的货物分出来
#         B2 = self.surplus(Plan1[0], B, 'ab')
#
#         # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
#         self.twice(show_num, 'blue', Plan1[2], self.pltSize, B2)
#
#         self.make_pic(show_num)
#
#
#     #make_pic内置函数
#     def box(self, ax,x, y, z, dx, dy, dz, color='red'):
#         xx = [x, x, x+dx, x+dx, x]
#         yy = [y, y+dy, y+dy, y, y]
#         kwargs = {'alpha': 1, 'color': color}
#         ax.plot3D(xx, yy, [z]*5, **kwargs)#下底
#         ax.plot3D(xx, yy, [z+dz]*5, **kwargs)#上底
#         ax.plot3D([x, x], [y, y], [z, z+dz], **kwargs)
#         ax.plot3D([x, x], [y+dy, y+dy], [z, z+dz], **kwargs)
#         ax.plot3D([x+dx, x+dx], [y+dy, y+dy], [z, z+dz], **kwargs)
#         ax.plot3D([x+dx, x+dx], [y, y], [z, z+dz], **kwargs)
#         return ax
#     #显示图形的函数：Items = [[num[0],num[1],num[2],num[3],num[4],num[5],num[6]],]
#     def make_pic(self, Items):
#         fig = plt.figure()
#         ax = Axes3D(fig)
#         ax.xaxis.set_major_locator(MultipleLocator(50))
#         ax.yaxis.set_major_locator(MultipleLocator(50))
#         ax.zaxis.set_major_locator(MultipleLocator(50))
#         for num in Items:
#             self.box(ax,num[0],num[1],num[2],num[3],num[4],num[5],num[6])
#         plt.title('Cube')
#         plt.show()
#
#     #把尺寸数据生成绘图数据
#     def make(self, O,C,color):
#         data = [O[0],O[1],O[2],C[0],C[1],C[2],color]
#         return data
#     #可用点的生成方法
#     def newsite(self, O,B_i):
#         # 在X轴方向上生成
#         O1 = (O[0]+B_i[0],O[1],O[2])
#         # 在Y轴方向上生成
#         O2 = (O[0],O[1]+B_i[1],O[2])
#         # 在Z轴方向上生成
#         O3 = (O[0],O[1],O[2]+B_i[2])
#         return [O1,O2,O3]
#
#     #3.拟人化依次堆叠方体
#     def packing3D(self, show_num,color,O,C,Box_list):
#         fullPalletNum = 0
#         O_items = [O]  # 放置点列表
#         O_pop = []     # 把当前不可用放置点弹出
#         for i in range(0,len(Box_list)):
#             #货物次序应小于等于可用点数量，如：第四个货物i=3，使用列表内的第4个放置点O_items[3]，i+1即常见意义的第几个，len即总数，可用点总数要大于等于目前个数
#             if i+1 <= len(O_items):
#                 #如果放置点放置货物后，三个方向都不会超过箱体限制,则认为可以堆放
#                 if O_items[i-1][0]+Box_list[i][0]<=C[0] and O_items[i-1][1]+Box_list[i][1]<=C[1] and O_items[i-1][2]+Box_list[i][2]<=C[2]:
#                     #使用放置点，添加一个图显信息
#                     new_show = self.make(O_items[i-1],Box_list[i],color)
#                     if new_show not in show_num:
#                         show_num.append(self.make(O_items[i-1],Box_list[i],color))
#                     #计数加1
#                     print('1 fullPalletNum: ', fullPalletNum)
#                     fullPalletNum = len(show_num) - 1
#                     #把堆叠后产生的新的点，加入放置点列表
#                     for new_O in self.newsite(O_items[i-1],Box_list[i]):
#                         #保证放入的可用点是不重复的
#                         if new_O not in O_items:
#                             O_items.append(new_O)
#                 #如果轮到的这个放置点不可用
#                 else:
#                     #把这个可用点弹出弃用
#                     O_pop.append(O_items.pop(i-1))
#                     #弃用可用点后，货物次序应小于等于剩余可用点数量
#                     if i+1 <= len(O_items):# and len(O_items)-1>=0:
#                         #当可用点一直不可用时
#                         while O_items[i-1][0]+Box_list[i][0]>C[0] or O_items[i-1][1]+Box_list[i][1]>C[1] or O_items[i-1][2]+Box_list[i][2]>C[2]:
#                             #一直把可用点弹出弃用
#                             O_pop.append(O_items.pop(i-1))
#                             #如果弹出后货物次序超出剩余可用点，则认为无法继续放置
#                             if i-1 > len(O_items)-1:
#                                 break
#                         #货物次序应小于等于剩余可用点数量
#                         if i+1 <= len(O_items):
#                             #如果不再超出限制，在这个可用点上堆叠
#                             new_show = self.make(O_items[i-1],Box_list[i],color)
#                             if new_show not in show_num:
#                                 show_num.append(self.make(O_items[i-1],Box_list[i],color))
#                             #计数加1
#                             print('2 fullPalletNum: ', fullPalletNum)
#                             fullPalletNum = len(show_num) - 1
#                             #把堆叠后产生的新的点，加入放置点列表
#                             for new_O in self.newsite(O_items[i-1],Box_list[i]):
#                                 #保证放入的可用点是不重复的
#                                 if new_O not in O_items:
#                                     O_items.append(new_O)
#         return fullPalletNum,O_items,O_pop
#
#     #<<<---写一个函数专门用来调整方向和计算剩余货物
#     def surplus(self, num,Box_list,change):#change='ab','bc','ac',0有三组对调可能，共6种朝向
#         new_Box_list = Box_list[num-1:-1]
#         if num == 0:
#             new_Box_list = Box_list
#         if change == 'ab':
#             for i in range(0,len(new_Box_list)):
#                 new_Box_list[i]=(new_Box_list[i][1],new_Box_list[i][0],new_Box_list[i][2])
#         elif change == 'bc':
#             for i in range(0,len(new_Box_list)):
#                 new_Box_list[i]=(new_Box_list[i][0],new_Box_list[i][2],new_Box_list[i][1])
#         elif change == 'ac':
#             for i in range(0,len(new_Box_list)):
#                 new_Box_list[i]=(new_Box_list[i][2],new_Box_list[i][1],new_Box_list[i][0])
#         elif change == 0:
#             return new_Box_list
#         else:
#             return new_Box_list
#         return new_Box_list
#     #残余点二次分配函数
#     def twice(self, show_num,color,O_pop,C,Box_list):
#         for a2 in O_pop:
#             if a2[0]==0 and a2[1]==0:
#                 Plan = self.packing3D(show_num,color,a2,C,Box_list)
#                 Box_list = self.surplus(Plan[0],Box_list,0)
#             elif a2[1]==0 and a2[2]==0:
#                 Plan = self.packing3D(show_num,color,a2,C,Box_list)
#                 Box_list = self.surplus(Plan[0],Box_list,0)
#             elif a2[0]==0 and a2[2]==0:
#                 Plan = self.packing3D(show_num,color,a2,C,Box_list)
#                 Box_list = self.surplus(Plan[0],Box_list,0)
#         return Box_list


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

        self.packedNum = 0

        self.containerVol = self.pltSize[0] * self.pltSize[1] * self.pltSize[2]
        self.boxVol = 0
        self.ratio = 0

        self.used_point = []

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

        # 把剩下的货物分出来
        print('2222222222222: before B2', self.ctnList)
        B2 = self.surplus(self.packedNum, self.ctnList, 'bc')
        # B2 = self.surplus(Plan1[0], self.ctnList, 'bc')
        print('2222222222222: B2', B2)

        # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
        self.twice(show_num=show_num, O_pop=O_pop, C=self.pltSize, Box_list=B2, color='orange')
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
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.yaxis.set_major_locator(MultipleLocator(50))
        ax.zaxis.set_major_locator(MultipleLocator(50))

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
        current = [i + j for i, j in zip(O, sku)]
        self.cube = tuple([max(i, j) for i, j in zip(self.cube, current)])


    #可用点的生成方法
    def newsite(self, O,B_i):
        # 在X轴方向上生成
        O1 = (O[0]+B_i[0],O[1],O[2])
        # 在Y轴方向上生成
        O2 = (O[0],O[1]+B_i[1],O[2])
        # 在Z轴方向上生成
        O3 = (O[0],O[1],O[2]+B_i[2])
        return [O1,O2,O3]

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
                    new_show = self.make(O_items[i-1],Box_list[i], color)
                    last_show = self.make(O_items[i-1],Box_list[i-1], color)
                    print('----------放置点：', O_items[i - 1])
                    print('----------new_show：', new_show)
                    print('----------last_show：', last_show)

                    if new_show not in show_num:
                        # print('1 new_show: ', new_show)
                        show_num.append(self.make(O_items[i-1],Box_list[i], color))
                        self.geneMinCube(O_items[i - 1], Box_list[i])

                        self.used_point.append(O_items[i-1])   # 在已用点列表中增加当前图显点
                        # 计数加1
                        print('222 current Box: ', Box_list[i])

                        self.packedNum += 1
                        self.boxVol += Box_list[i][0] * Box_list[i][1] * Box_list[i][2]
                    #把堆叠后产生的新的点，加入放置点列表
                    for new_O in self.newsite(O_items[i-1],Box_list[i]):
                        #保证放入的可用点是不重复的
                        if new_O not in O_items:
                            O_items.append(new_O)

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
                                self.geneMinCube(O_items[i - 1], Box_list[i])
                                self.used_point.append(O_items[i - 1])  # 在已用点列表中增加当前图显点
                                #计数加1
                                # print('2 self.packedNum: ', self.packedNum)
                                print('3 current Box: ', Box_list[i])

                                self.packedNum +=  1
                                self.boxVol += Box_list[i][0] * Box_list[i][1] * Box_list[i][2]

                            #把堆叠后产生的新的点，加入放置点列表
                            for new_O in self.newsite(O_items[i-1],Box_list[i]):
                                #保证放入的可用点是不重复的
                                if new_O not in O_items:
                                    O_items.append(new_O)
                            # 将已用点从放置点列表中删除
                            O_items = list(filter(lambda x: x not in self.used_point, O_items))

        return O_items,O_pop

    #<<<---写一个函数专门用来调整方向和计算剩余货物
    def surplus(self,num, Box_list,change):#change='ab','bc','ac',0有三组对调可能，共6种朝向
        # new_Box_list = Box_list[num-1:-1]
        new_Box_list = Box_list[num:]

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


class MinCube():
    def __init__(self, skuList=None):
        if skuList is None:
            self.skuList = [(20, 20, 10) for num in range(10)]
        else:
            self.skuList = skuList

        self.skuList = self.sortList(self.skuList)

        self.skuVol = 0
        self.ratio = 0
        self.used_point = []

        for sku in skuList:
            self.skuVol += sku[0]*sku[1]*sku[2]

        # 最小cube
        self.cube = (0, 0, 0)
        self.cubeVol = 0


    def run(self, show=True):
        O = (0, 0, 0)  # 原点坐标
        show_num = []

        self.packing3D(show_num=show_num, O=O, skuList=self.skuList, color='blue')

        # 添加最小cube图显信息
        show_num.append(self.make(O, self.cube, 'green'))

        if show:
            self.make_pic(show_num)

        print('SKU list: ', self.skuList)
        print('Min cube:', self.cube)
        print('最小Cube满箱率: ', self.skuVol / (self.cube[0] * self.cube[1] * self.cube[2]))



    def packing3D(self, show_num, O, skuList, color):
        O_items = [O]
        O_pop = []

        # 初始化最小cube为第一个sku
        self.cube = skuList[0]
        self.cubeVol = skuList[0][0] * skuList[0][1] * skuList[0][2]
        show_num.append(self.make(O_items[0], skuList[0], color))
        # 把堆叠后产生的新的点，加入放置点列表
        for new_O in self.newsite(O_items[0], skuList[0]):
            # 保证放入的可用点是不重复的
            if new_O not in O_items:
                O_items.append(new_O)
        self.used_point.append(O)
        # 将已用点从放置点列表中删除
        # O_pop.append(filter(lambda x: x in self.used_point, O_items))
        O_items = list(filter(lambda x: x not in self.used_point, O_items))

        # 放置货物的朝向
        face = ['abc','acb','bac','bca','cab', 'cba']

        # 第2到最后一个SKU
        for i in range(1, len(skuList)):
            # 初始化cube为三边叠加的最大立方体
            curr_sku = skuList[i]
            choose_point = 0
            choose_face = 'abc'
            curr_cube = 0
            # 每增加一个货物，初始化当前cube为最大立方体
            curr_cube_vol = (self.cube[0] + curr_sku[0]) * (self.cube[1] + curr_sku[1]) * (self.cube[2] + curr_sku[2])

            for point in O_items:
                for f in face:
                    curr_sku = self.exchange(skuList[i], f)
                    # print('point: ', point, 'curr_sku: ', curr_sku)
                    [c, v] = self.geneMinCube(point, curr_sku)
                    if v < curr_cube_vol:
                        # 使用当前放置点，添加一个图显信息
                        choose_point = point
                        choose_face = f
                        curr_cube = c
                        curr_cube_vol = v

            placed_sku = self.exchange(skuList[i], choose_face)
            print('choose point: ', choose_point, 'curr_sku: ', placed_sku)
            show_num.append(self.make(choose_point, placed_sku, color))
            # 添加新的放置点
            for i in self.newsite(choose_point, placed_sku):
                O_items.append(i)
            self.used_point.append(choose_point)
            self.cube = self.geneMinCube(choose_point, placed_sku)[0]
            self.cubeVol = curr_cube_vol
            O_items = list(filter(lambda x: x not in self.used_point, O_items))



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
        return [O1, O2, O3]

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
    def make_pic(self, Items):
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.yaxis.set_major_locator(MultipleLocator(50))
        ax.zaxis.set_major_locator(MultipleLocator(50))

        # print 画图的点
        print('---- show num: ')
        print(Items)

        for num in Items:
            self.box(ax, num[0], num[1], num[2], num[3], num[4], num[5], num[6])
        plt.show()

    # 把尺寸数据生成绘图数据
    def make(self, O, C, color):
        data = [O[0], O[1], O[2], C[0], C[1], C[2], color]
        return data

    # 生成最小cube
    def geneMinCube(self, O, sku):
        current = [i + j for i, j in zip(O, sku)]
        cube = tuple([max(i, j) for i, j in zip(self.cube, current)])
        vol = cube[0] * cube[1] * cube[2]
        return cube, vol

    def sortList(self, skuList):
        re = []
        for i in skuList:
            re.append(tuple(sorted(i, reverse=True)))
        return sorted(re, key=(lambda x:(x[0],x[1],x[2])),reverse=True)


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

    # sku_list = [(20.0, 16.0, 5.5), (20.0, 12.5, 5.0), (20.0, 12.5, 25.0)]


    sku_list = [(20.0, 16.0, 5.5), (25.0, 20.0, 12.5),  (20.0, 12.5, 5.0)]

    # sku_list = [(35.8, 12.0, 8.3)]

    size43 = (45.1, 36.2, 21.0)
    # size43 = (40.6, 22.9, 10.2)

    # ===================================
    # ============TESTING================
    # ===================================


    # pack1 = Packing(size5, sku_list.copy())
    # pack1.run(True)


    # pack2 = Packing(size43, sku_list.copy())
    # pack2.run(True)

    pack3 = MinCube(sku_list)
    pack3.run()






