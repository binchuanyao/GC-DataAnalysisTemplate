# -*- coding: utf-8 -*-
# @File   : 3D-carton
# @Time   : 2022/04/14 20:02 
# @Author : BCY

from matplotlib import pyplot as plt
#设置图表刻度等格式
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class Draw():
    def __init__(self, plt=None, ctn=None):
        if plt is None:
            self.pltSize = (120, 100, 160)
        else:
            self.pltSize = plt

        if ctn is None:
            self.ctnSize = (40, 30, 30)
        else:
            self.ctnSize = ctn

    def run(self):
        # 1.给定空间容器C      4.2*1.9*1.8
        # C = (120, 100, 160)  # 箱体长宽高
        color = 'red'  # 箱体颜色

        # 显示箱体
        O = (0, 0, 0)  # 原点坐标
        show_num = [self.make(O, self.pltSize, color)]

        # 2.给定有限量个方体 500个(60,40,50)的方体，当方体大小存在差异时，我们将按照体积大小降序排列，优先摆放大体积的
        B = [(50, 20, 60) for num in range(0, 100)]

        # 把货物第一次装箱
        Plan1 = self.packing3D(show_num, 'blue', (0, 0, 0), self.pltSize, B)
        # print(len(show_num))

        # 把剩下的货物分出来
        B2 = self.surplus(Plan1[0], B, 'ab')

        # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
        self.twice(show_num, 'blue', Plan1[2], self.pltSize, B2)

        self.make_pic(show_num)


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
    #显示图形的函数：Items = [[num[0],num[1],num[2],num[3],num[4],num[5],num[6]],]
    def make_pic(self, Items):
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.yaxis.set_major_locator(MultipleLocator(50))
        ax.zaxis.set_major_locator(MultipleLocator(50))
        for num in Items:
            self.box(ax,num[0],num[1],num[2],num[3],num[4],num[5],num[6])
        plt.title('Cube')
        plt.show()

    #把尺寸数据生成绘图数据
    def make(self, O,C,color):
        data = [O[0],O[1],O[2],C[0],C[1],C[2],color]
        return data
    #可用点的生成方法
    def newsite(self, O,B_i):
        # 在X轴方向上生成
        O1 = (O[0]+B_i[0],O[1],O[2])
        # 在Y轴方向上生成
        O2 = (O[0],O[1]+B_i[1],O[2])
        # 在Z轴方向上生成
        O3 = (O[0],O[1],O[2]+B_i[2])
        return [O1,O2,O3]

    #3.拟人化依次堆叠方体
    def packing3D(self, show_num,color,O,C,Box_list):
        fullPalletNum = 0
        O_items = [O]
        O_pop = []
        for i in range(0,len(Box_list)):
            #货物次序应小于等于可用点数量，如：第四个货物i=3，使用列表内的第4个放置点O_items[3]，i+1即常见意义的第几个，len即总数，可用点总数要大于等于目前个数
            if i+1 <= len(O_items):
                #如果放置点放置货物后，三个方向都不会超过箱体限制,则认为可以堆放
                if O_items[i-1][0]+Box_list[i][0]<=C[0] and O_items[i-1][1]+Box_list[i][1]<=C[1] and O_items[i-1][2]+Box_list[i][2]<=C[2]:
                    #使用放置点，添加一个图显信息
                    new_show = self.make(O_items[i-1],Box_list[i],color)
                    if new_show not in show_num:
                        show_num.append(self.make(O_items[i-1],Box_list[i],color))
                    #计数加1
                    print('1 show_num: ', len(show_num))
                    fullPalletNum = len(show_num) - 1
                    #把堆叠后产生的新的点，加入放置点列表
                    for new_O in self.newsite(O_items[i-1],Box_list[i]):
                        #保证放入的可用点是不重复的
                        if new_O not in O_items:
                            O_items.append(new_O)
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
                            new_show = self.make(O_items[i-1],Box_list[i],color)
                            if new_show not in show_num:
                                show_num.append(self.make(O_items[i-1],Box_list[i],color))
                            #计数加1
                            print('2 show_num: ', len(show_num))
                            fullPalletNum = len(show_num) - 1
                            #把堆叠后产生的新的点，加入放置点列表
                            for new_O in self.newsite(O_items[i-1],Box_list[i]):
                                #保证放入的可用点是不重复的
                                if new_O not in O_items:
                                    O_items.append(new_O)
        return fullPalletNum,O_items,O_pop

    #<<<---写一个函数专门用来调整方向和计算剩余货物
    def surplus(self, num,Box_list,change):#change='ab','bc','ac',0有三组对调可能，共6种朝向
        new_Box_list = Box_list[num-1:-1]
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
    def twice(self, show_num,color,O_pop,C,Box_list):
        for a2 in O_pop:
            if a2[0]==0 and a2[1]==0:
                Plan = self.packing3D(show_num,color,a2,C,Box_list)
                Box_list = self.surplus(Plan[0],Box_list,0)
            elif a2[1]==0 and a2[2]==0:
                Plan = self.packing3D(show_num,color,a2,C,Box_list)
                Box_list = self.surplus(Plan[0],Box_list,0)
            elif a2[0]==0 and a2[2]==0:
                Plan = self.packing3D(show_num,color,a2,C,Box_list)
                Box_list = self.surplus(Plan[0],Box_list,0)
        return Box_list



if __name__ == '__main__':
    pltSize = (120, 100, 150)
    ctnSize = (50, 20, 30)

    draw = Draw(pltSize, ctnSize)
    draw.run()




