# -*- coding: utf-8 -*-
# @File   : testDemo
# @Time   : 2022/05/19 15:12 
# @Author : BCY

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#! /usr/bin/python

import os
import csv
import datetime
from matplotlib.animation import FuncAnimation
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker



def times(n):
    re = 1
    re = re * pow(3*6, n)
    if n>=1:
        while n>1:
            re = re * n
            n = n - 1
        return re
    else:
        return 0

# 显示图形的函数：Items = [[num[0],num[1],num[2],num[3],num[4],num[5],num[6]],]
def make_pic(Items, maxSize):
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

    # ax.set_xlim3d(0, 260)
    # ax.set_ylim3d(0, 50)
    # ax.set_zlim3d(0, 50)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # print 画图的点
    print('---- show num: ')
    print(Items)

    for num in Items:
        box(ax, num[0], num[1], num[2], num[3], num[4], num[5], num[6])
    plt.show()

# make_pic内置函数
def box(ax, x, y, z, dx, dy, dz, color='red'):
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



class streamDetectionPlot(object):
    """
    Anomaly plot output.
    """

    # initial the figure parameters.
    def __init__(self):
        # Turn matplotlib interactive mode on.
        plt.ion()
        # initial the plot variable.
        self.timestamp = []
        self.actualValue = []
        self.predictValue = []
        self.anomalyScore = []
        self.tableValue = [[0, 0, 0, 0]]
        self.highlightList = []
        self.highlightListTurnOn = True
        self.anomalyScoreRange = [0, 1]
        self.actualValueRange = [0, 1]
        self.predictValueRange = [0, 1]
        self.timestampRange = [0, 1]
        self.anomalyScatterX = []
        self.anomalyScatterY = []

        # initial the figure.
        global fig
        fig = plt.figure(figsize=(18, 8), facecolor="white")
        fig.subplots_adjust(left=0.06, right=0.70)
        self.actualPredictValueGraph = fig.add_subplot(2, 1, 1)
        self.anomalyScoreGraph = fig.add_subplot(2, 1, 2)
        self.anomalyValueTable = fig.add_axes([0.8, 0.1, 0.2, 0.8], frameon=False)

    # define the initial plot method.
    def initPlot(self):
        # initial two lines of the actualPredcitValueGraph.
        self.actualLine, = self.actualPredictValueGraph.plot_date(self.timestamp, self.actualValue, fmt="-",
                                                                  color="red", label="actual value")
        self.predictLine, = self.actualPredictValueGraph.plot_date(self.timestamp, self.predictValue, fmt="-",
                                                                   color="blue", label="predict value")
        self.actualPredictValueGraph.legend(loc="upper right", frameon=False)
        self.actualPredictValueGraph.grid(True)

        # initial two lines of the anomalyScoreGraph.
        self.anomalyScoreLine, = self.anomalyScoreGraph.plot_date(self.timestamp, self.anomalyScore, fmt="-",
                                                                  color="red", label="anomaly score")
        self.anomalyScoreGraph.legend(loc="upper right", frameon=False)
        self.baseline = self.anomalyScoreGraph.axhline(0.8, color='black', lw=2)

        # set the x/y label of the first two graph.
        self.anomalyScoreGraph.set_xlabel("datetime")
        self.anomalyScoreGraph.set_ylabel("anomaly score")
        self.actualPredictValueGraph.set_ylabel("value")

        # configure the anomaly value table.
        self.anomalyValueTableColumnsName = ["timestamp", "actual value", "expect value", "anomaly score"]
        self.anomalyValueTable.text(0.05, 0.99, "Anomaly Value Table", size=12)
        self.anomalyValueTable.set_xticks([])
        self.anomalyValueTable.set_yticks([])

        # axis format.
        self.dateFormat = DateFormatter("%m/%d %H:%M")
        self.actualPredictValueGraph.xaxis.set_major_formatter(ticker.FuncFormatter(self.dateFormat))
        self.anomalyScoreGraph.xaxis.set_major_formatter(ticker.FuncFormatter(self.dateFormat))


    # define the output method.
    def anomalyDetectionPlot(self, timestamp, actualValue, predictValue, anomalyScore):

        # update the plot value of the graph.
        self.timestamp.append(timestamp)
        self.actualValue.append(actualValue)
        self.predictValue.append(predictValue)
        self.anomalyScore.append(anomalyScore)

        # update the x/y range.
        self.timestampRange = [min(self.timestamp), max(self.timestamp)+datetime.timedelta(minutes=10)]
        self.actualValueRange = [min(self.actualValue), max(self.actualValue)+1]
        self.predictValueRange = [min(self.predictValue), max(self.predictValue)+1]

        # update the x/y axis limits
        self.actualPredictValueGraph.set_ylim(
            min(self.actualValueRange[0], self.predictValueRange[0]),
            max(self.actualValueRange[1], self.predictValueRange[1])
        )
        self.actualPredictValueGraph.set_xlim(
            self.timestampRange[1] - datetime.timedelta(days=1),
            self.timestampRange[1]
        )
        self.anomalyScoreGraph.set_xlim(
            self.timestampRange[1]- datetime.timedelta(days=1),
            self.timestampRange[1]
        )
        self.anomalyScoreGraph.set_ylim(
            self.anomalyScoreRange[0],
            self.anomalyScoreRange[1]
        )

        # update the two lines of the actualPredictValueGraph.
        self.actualLine.set_xdata(self.timestamp)
        self.actualLine.set_ydata(self.actualValue)
        self.predictLine.set_xdata(self.timestamp)
        self.predictLine.set_ydata(self.predictValue)

        # update the line of the anomalyScoreGraph.
        self.anomalyScoreLine.set_xdata(self.timestamp)
        self.anomalyScoreLine.set_ydata(self.anomalyScore)

        # update the scatter.
        if anomalyScore >= 0.8:
            self.anomalyScatterX.append(timestamp)
            self.anomalyScatterY.append(actualValue)
            self.actualPredictValueGraph.scatter(
                self.anomalyScatterX,
                self.anomalyScatterY,
                s=50,
                color="black"
            )

        # update the highlight of the anomalyScoreGraph.
        if anomalyScore >= 0.8:
            self.highlightList.append(timestamp)
            self.highlightListTurnOn = True
        else:
            self.highlightListTurnOn = False
        if len(self.highlightList) != 0 and self.highlightListTurnOn is False:
            self.anomalyScoreGraph.axvspan(
                self.highlightList[0] - datetime.timedelta(minutes=10),
                self.highlightList[-1] + datetime.timedelta(minutes=10),
                color="r",
                edgecolor=None,
                alpha=0.2
            )
            self.highlightList = []
            self.highlightListTurnOn = True

        # update the anomaly value table.
        if anomalyScore >= 0.8:
            # remove the table and then replot it
            self.anomalyValueTable.remove()
            self.anomalyValueTable = fig.add_axes([0.8, 0.1, 0.2, 0.8], frameon=False)
            self.anomalyValueTableColumnsName = ["timestamp", "actual value", "expect value", "anomaly score"]
            self.anomalyValueTable.text(0.05, 0.99, "Anomaly Value Table", size=12)
            self.anomalyValueTable.set_xticks([])
            self.anomalyValueTable.set_yticks([])
            self.tableValue.append([
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                actualValue,
                predictValue,
                anomalyScore
            ])
            if len(self.tableValue) >= 40: self.tableValue.pop(0)
            self.anomalyValueTable.table(cellText=self.tableValue,
                                         colWidths=[0.35] * 4,
                                         colLabels=self.anomalyValueTableColumnsName,
                                         loc=1,
                                         cellLoc="center"
                                         )

        # plot pause 0.0001 second and then plot the next one.
        plt.pause(0.0001)
        plt.draw()

    def close(self):
        plt.ioff()
        plt.show()



if __name__ == '__main__':
    for i in range(1, 10):
    # n = 6
        x = times(i)
        print('商品列表： ', i, '解空间： ', x)

    # 欧洲箱型
    # Box003EL(21.4, 21.4, 10.1)
    # Size18(30.5, 22.9, 13.3)
    # Size32(34.3, 28.6, 24.8)
    # Size44(40.6, 30.5, 10.2)
    # Size55(45.1, 36.2, 21.0)
    # Size78(52.7, 45.1, 39.4)

    show_num = []

    ## 美洲箱型
    # Box003EL	(21.4, 21.4, 10.1)
    # Size25	(33.0, 28.6, 8.9)
    # Size44	(40.6, 30.5, 10.2)
    # Size55	(45.1, 36.2, 21.0)
    # Size58	(45.7, 57.8, 9.5)
    # Size83	(55.9, 45.7, 30.5)
    #
    # show_num.append([0,0,0, 21.4, 21.4, 10.1, 'blue'])
    #
    # show_num.append([25, 0, 0, 33.0, 28.6, 8.9, 'blue'])
    #
    # show_num.append([60, 0, 0, 40.6, 30.5, 10.2, 'blue'])
    #
    # show_num.append([105, 0, 0, 45.1, 36.2, 21.0, 'blue'])
    #
    # show_num.append([155, 0, 0, 45.7, 57.8, 9.5, 'blue'])
    #
    # show_num.append([205, 0, 0, 55.9, 45.7, 30.5, 'blue'])
    #
    # make_pic(show_num, 250)


    ### 是否重叠 testing

    # aSize = (33, 18, 11)
    # bSize = (33,18,11)
    #
    # aCoord = (0,0,0)
    # bCoord = (0,0,15)
    #
    # l = isOverlap(aCoord, aSize, bCoord, bSize)
    # print('是否重叠： ', l)


