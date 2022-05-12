# -*- coding: utf-8 -*-
# @File   : PalletizeDemo
# @Time   : 2022/04/14 14:23 
# @Author : BCY
import os.path

import numpy as np
import pandas as pd

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QStatusBar
from PyQt5.QtCore import QAbstractTableModel, Qt
from palletize import Ui_MainWindow


from matplotlib import pyplot as plt #设置图表刻度等格式
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D


import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure




class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self.setupUi(self)
        self.setWindowTitle('垛型分析')


        self.statusBar.showMessage('谷仓-仓储管理部-规划实施部')
        self.statusBar.addPermanentWidget(QLabel("垛型分析V1.0"), stretch=0)  # 比例
        # self.statusBar.addPermanentWidget(self.show_2, stretch=0)


        self.df = pd.DataFrame()

        # 单个箱规计算
        self.ok_btn.clicked.connect(self.calculateSingle)
        self.reset_btn.clicked.connect(self.reset)

        self.show_btn.clicked.connect(self.show_palletize)

        # 加载数据窗口与事件函数的连接
        self.upload_btn.clicked.connect(self.load_data)

        self.process_btn.clicked.connect(self.calculateDF)
        self.download_btn.clicked.connect(self.save_data)
        self.clearall_btn.clicked.connect(self.clear_all)



    def calculateSingle(self):
        '''
        计算单个箱规的码垛方式
        :return:
        '''

        try:

            # 托盘尺寸
            L = int(self.plt_length.text())  # 托盘长
            W = int(self.plt_width.text())   # 托盘宽
            H = int(self.plt_height.text())  # 托盘高

            plt_l_gap = int(self.plt_l_gap.text())  # 托盘长边距
            plt_w_gap = int(self.plt_w_gap.text())  # 托盘宽边距

            # 可码垛区域为原始边长 - 边缘长度
            L = L - plt_l_gap
            W = W - plt_w_gap

            l = int(self.ctn_length.text())  # 箱长
            w = int(self.ctn_width.text())   # 箱宽
            h = int(self.ctn_height.text())  # 箱高

            # # 若箱间距不为0， 则更新箱子码垛后的长度
            # ctn_gap = int(self.ctn_gap.text())  # 箱间距


            # print('pallet L, W, H: ', L, W, H)
            # print('carton L, W, H: ', l, w, h)

            num1 = self.get_layer(L, W)  # method 1
            num2 = self.get_layer(W, L)  # method 2

            layer = int(H/h)

            print('每层箱数：', num1, num2)
            print('层数：', layer)

            max_num = max(num1, num2)

            plt_carton = max_num * layer

            print('托规箱数为 ', plt_carton)

            ctn_vol = l*w*h
            plt_vol = L*W*H

            pallet_height = layer * h
            height_ratio = pallet_height/H
            ratio = plt_carton*ctn_vol/plt_vol

            msg1 = '码垛方式: \n 每层箱数:{} \t层数:{} \n 码托高度:{} \t高度利用率:{:.2%} \n 托规(箱):{} \t码托利用率:{:.2%} '.format(max_num, layer, pallet_height, height_ratio, plt_carton, ratio)

            self.resultText1.setText(msg1)

        # 如果出错，弹出提醒窗口
        except:
            self.show_error_dialog('请填写正确的托盘尺寸或箱规尺寸!')


    def calculateDF(self):
        # 托盘尺寸
        try:
            L = int(self.plt_length.text())  # 托盘长
            W = int(self.plt_width.text())  # 托盘宽
            H = int(self.plt_height.text())  # 托盘高

            plt_l_gap = int(self.plt_l_gap.text())  # 托盘长边距
            plt_w_gap = int(self.plt_w_gap.text())  # 托盘宽边距


            L = L - plt_l_gap
            W = W - plt_w_gap

            # 获取箱规长宽高对应的列编号，从0开始
            # print('in function calculateDF')
            # print('箱长列： ', self.length_col.text())
            # print(self.df.columns)
            ctn_l_col = self.df.columns[int(self.length_col.text())]
            ctn_w_col = self.df.columns[int(self.width_col.text())]
            ctn_h_col = self.df.columns[int(self.height_col.text())]


            # 判断数据中箱的长宽高尺寸单位, 托盘尺寸为cm
            if self.mm_radio_btn.isChecked() == True:
                L = L*10
                W = W*10
                H = H*10

            pltVol = L*W*H
            # print('L,W,H: ', L,W,H,  pltVol)

            ctn_num_col = self.df.columns[int(self.cartonNum_col.text())]

            # print('df[ctn_num_col]: ', self.df[ctn_num_col])


            self.df['num1'] = np.floor(L / self.df[ctn_l_col]) * np.floor(W / self.df[ctn_w_col]) + \
                           np.floor((L - np.floor(L / self.df[ctn_l_col]) * self.df[ctn_l_col]) / self.df[ctn_w_col]) * np.floor(W / self.df[ctn_l_col])


            self.df['num2'] = np.floor(W / self.df[ctn_l_col]) * np.floor(L / self.df[ctn_w_col]) + \
                           np.floor((W - np.floor(W / self.df[ctn_l_col]) * self.df[ctn_l_col]) / self.df[ctn_w_col]) * np.floor(L / self.df[ctn_l_col])

            self.df['每层箱数'] = self.df[['num1', 'num2']].max(axis=1)

            self.df['层数'] = np.floor( H/self.df[ctn_h_col])

            self.df['托规(箱)'] = self.df['每层箱数'] * self.df['层数']

            '''
            判断是否需要计算托重
            '''

            # 获取箱重对应的列编号， or  获取单sku重和件箱规对应的列编号, 若两组都不为空，以箱重计算
            if self.sku_wt_col.text().isdigit() and self.fullCartonQty_col.text().isdigit():
                # 获取列名
                sku_wt_col = self.df.columns[int(self.sku_wt_col.text())]
                fullCartonQty_col = self.df.columns[int(self.fullCartonQty_col.text())]

                # 判断数据中重量单位, 转化为kg, 默认为kg
                if self.g_radio_btn.isChecked() == True:
                    self.df['托重(kg)'] = self.df['托规(箱)'] * self.df[sku_wt_col] * self.df[fullCartonQty_col] * 1000
                else:
                    self.df['托重(kg)'] = self.df['托规(箱)'] * self.df[sku_wt_col] * self.df[fullCartonQty_col]

            elif self.ctn_wt_col.text().isdigit():

                ctn_wt_col = self.df.columns[int(self.ctn_wt_col.text())]

                # 判断数据中重量单位, 转化为kg, 默认为kg
                if self.g_radio_btn.isChecked() == True:
                    self.df['托重(kg)'] = self.df['托规(箱)'] * self.df[ctn_wt_col] / 1000
                else:
                    self.df['托重(kg)'] = self.df['托规(箱)'] * self.df[ctn_wt_col]
            else:
                pass


            self.df['码托高度'] = self.df['层数'] * self.df[ctn_h_col]
            self.df['码托利用率'] = (self.df['托规(箱)']*self.df[ctn_l_col]*self.df[ctn_w_col]*self.df[ctn_h_col]/pltVol).apply(lambda x: format(x, '.2%'))

            self.df['托数'] = (self.df[ctn_num_col] / self.df['托规(箱)']).apply(lambda x: format(x, '.2f')) 
            self.df['整托数'] = np.floor(self.df[ctn_num_col] / self.df['托规(箱)'])
            self.df['散箱数'] = self.df[ctn_num_col] - self.df['整托数']*self.df['托规(箱)']

            self.df = self.df.drop(['num1', 'num2'], axis=1)

            model = dfModel(self.df)
            self.tableView.setModel(model)

        except:
            self.show_error_dialog('请填写正确的列编号!')
        else:
            self.show_info_dialog('计算完成！')


    def get_layer(self, L, W):
        l = int(self.ctn_length.text())
        w = int(self.ctn_width.text())

        ctn_gap = int(self.ctn_gap.text())
        l = l + ctn_gap

        l_num = int(L / l)  # 托盘长边方向的摆放数
        w_num = int(W / w)  # 托盘短边方向的摆放数

        rmd_l_num = int((L - int(L / l) * l) / w)  # 托盘长边方向的剩余摆放数
        rmd_w_num = int(W / l)  # 托盘短边方向的剩余摆放数

        layer = l_num * w_num + rmd_l_num * rmd_w_num
        return layer


    def reset(self):
        # self.plt_length.clear()
        # self.plt_width.clear()
        # self.plt_height.clear()
        self.ctn_length.clear()
        self.ctn_width.clear()
        self.ctn_height.clear()

        self.plt_l_gap.setText('0')
        self.plt_w_gap.setText('0')
        self.ctn_gap.setText('0')

        self.resultText1.clear()


    def show_palletize(self):

        # 托盘尺寸
        L = int(self.plt_length.text())  # 托盘长
        W = int(self.plt_width.text())  # 托盘宽
        H = int(self.plt_height.text())  # 托盘高

        plt_l_gap = int(self.plt_l_gap.text())  # 托盘长边距
        plt_w_gap = int(self.plt_w_gap.text())  # 托盘宽边距

        L = L - plt_l_gap
        W = W - plt_w_gap

        # 箱尺寸
        l = int(self.ctn_length.text())
        w = int(self.ctn_width.text())
        h = int(self.ctn_height.text())

        ctn_gap = int(self.ctn_gap.text())
        l = l + ctn_gap

        pltSize = (L, W, H)
        ctnSize = (l, w, h)

        draw = Draw(pltSize, ctnSize)
        draw.run()


    def load_data(self):
        # dialog = QFileDialog()
        # dialog.setFileMode(QFileDialog.AnyFile)
        # dialog.setFilter(QDir.Files)
        filenames = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.xlsx , *.xls, *.csv)')
        # global filename  ##声明全局变量
        filename = filenames[0]

        if 'csv' in filename:
            try:
                self.df = pd.read_csv(filename, encoding='utf-8')
            except:
                self.df = pd.read_csv(filename, encoding='gbk')
            # 删除有空值的行
            self.df.dropna(how='any', inplace=True)
            model = dfModel(self.df.head(100))
            self.tableView.setModel(model)
        elif 'xlsx' in filename:
            self.df = pd.read_excel(filename)
            # 删除有空值的行
            self.df.dropna(how='any', inplace=True)
            model = dfModel(self.df.head(100))
            self.tableView.setModel(model)
        else:
            self.show_error_dialog('请选择csv或xlsx文件类型!')

    def save_data(self):
        filePath, ok2 = QFileDialog.getSaveFileName(None, caption='保存文件', filter='Excel files(*.xlsx , *.xls, *.csv)')
        # print(filePath)  # 打印保存文件的全部路径（包括文件名和后缀名）
        if 'csv' in filePath:
            self.df.to_csv(filePath, index=False)
        elif 'xls' in filePath:
            self.df.to_excel(filePath, sheet_name='垛型分析', index=False)
        else:
            self.show_info_dialog('请保存为指定的文件类型！')

    def clear_all(self):
        # print('in clear_all function')
        # df = pd.DataFrame()
        # model = dfModel(df)
        self.tableView.setModel(dfModel(pd.DataFrame()))

    def show_error_dialog(self, msg):
        QMessageBox.critical(self, '错误', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def show_info_dialog(self, msg):
        QMessageBox.information(self, '消息', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def resource_path(self, relative_path):
        '''将相对路径转为运行时资源文件的绝对路径'''
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.')
        return os.path.join(base_path, relative_path)

class dfModel(QAbstractTableModel):

    def __init__(self, data, showAllColumn=False):
        QAbstractTableModel.__init__(self)
        self.showAllColumn = showAllColumn
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if type(self._data.columns[col]) == tuple:
                return self._data.columns[col][-1]
            else:
                return self._data.columns[col]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return (self._data.axes[0][col])
        return None

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

        self.fullPalletNum = 0

    def run(self):
        # 1.给定空间容器C      4.2*1.9*1.8
        # C = (120, 100, 160)  # 箱体长宽高
        color = 'red'  # 箱体颜色

        # 显示箱体
        O = (0, 0, 0)  # 原点坐标
        show_num = [self.make(O, self.pltSize, color)]

        # 2.给定有限量个方体 500个(60,40,50)的方体，当方体大小存在差异时，我们将按照体积大小降序排列，优先摆放大体积的
        B = [self.ctnSize for num in range(0, 10000)]

        # 把货物第一次装箱
        Plan1 = self.packing3D(show_num, 'blue', (0, 0, 0), self.pltSize, B)
        # print(len(show_num))

        # 把剩下的货物分出来
        B2 = self.surplus(Plan1[0], B, 'ab')

        # 把剩下的货物再次尝试装箱，针对三个在轴线上的点为新的原点
        self.twice(show_num, 'orange', Plan1[2], self.pltSize, B2)

        self.make_pic(show_num)


    #make_pic内置函数
    def box(self, ax,x, y, z, dx, dy, dz, color='red'):
        xx = [x, x, x+dx, x+dx, x]
        yy = [y, y+dy, y+dy, y, y]
        kwargs = {'alpha': 2, 'color': color}
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
        # plt.title('Palletize Model')
        # plt.text('托盘尺寸： {} \n货物尺寸： {} \n码托箱数： {}'.format(self.pltSize, self.ctnSize, self.fullPalletNum))
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
                    self.fullPalletNum = len(show_num) - 1
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
                            self.fullPalletNum = len(show_num) - 1
                            #把堆叠后产生的新的点，加入放置点列表
                            for new_O in self.newsite(O_items[i-1],Box_list[i]):
                                #保证放入的可用点是不重复的
                                if new_O not in O_items:
                                    O_items.append(new_O)
        return self.fullPalletNum, O_items, O_pop

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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ui = MainWindow()
    icon = ui.resource_path(os.path.join('images', 'goodcang.ico'))
    app.setWindowIcon(QIcon(icon))
    ui.show()
    sys.exit(app.exec_())