# -*- coding: utf-8 -*-
# @File   : config
# @Time   : 2022/02/14 11:28 
# @Author : BCY

import numpy as np
import pandas as pd


class Config:
    def __init__(self):
        # inventory location type
        # 库位类型

        # 卡板区
        self.PALLET = {
            'length': 1200,
            'width': 1000,
            'plt_height': 150,
            'height': 1650,
            'ratio': 0.65,
            'sku_max': 1,
            'weight_max': 500,
            'valid_vol': 0.00,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 1.9
        }

        # 原箱区
        self.BOX = {
            'length': 580,
            'width': 1200,
            'height': 680,
            'ratio': 0.3,
            'sku_max': 3,
            'weight_max': 500,
            'valid_vol': 0.0,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 0.8
        }

        # 储位盒区
        self.CARTON = {
            'length': 580,
            'width': 1200,
            'height': 370,
            'ratio': 0.3,
            'sku_max': 3,
            'weight_max': 500,
            'valid_vol': 0.00,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 0.7
        }

        # 料箱区——暂时未使用
        self.TOTE = {
            'length': 600,
            'width': 400,
            'height': 330,
            'ratio': 0.3,
            'sku_max': 3,
            'weight_max': 500,
            'valid_vol': 0.0,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 0.8
        }

        # 平铺区
        self.PP = {
            'length': 1200,
            'width': 1100,
            'height': 1650,
            'ratio': 3,
            'sku_max': 3,
            'weight_max': 500,
            'valid_vol': 0.0,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 3.0
        }

        # 异型平铺区
        self.PP_YX = {
            'length': 1200,
            'width': 1100,
            'height': 1650,
            'ratio': 3,
            'sku_max': 3,
            'weight_max': 500,
            'valid_vol': 0.0,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 2.0
        }

        # 超长平铺区
        self.PP_CC = {
            'length': 2000,
            'width': 1700,
            'height': 1650,
            'ratio': 3,
            'sku_max': 3,
            'weight_max': 500,
            'valid_vol': 0.0,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 2.0
        }

        # 异型高架区
        self.YX_GJ = {
            'length': 1200,
            'width': 1500,
            'height': 1400,
            'ratio': 1,
            'sku_max': 1,
            'weight_max': 500,
            'valid_vol': 0.0,
            'min_ratio': 0.5,
            'min_vol': 0.0,
            '库容坪效系数': 1.5
        }


        # sku货型及属性判断参数
        self.CARGO_TYPE = {
            'type': ['XS', 'S', 'M', 'L1', 'L2', 'XL'],
            'length': [15, 30, 60, 100, 120, np.NaN],
            'weight': [0.5, 3, 10, 23, 40, np.NaN]
        }

        self.SUPER_LONG_PARAM = 170
        self.BATCH_PARAM = 30


        # 卡板深度分级
        self.PALLET_INTERVAL = [0, 1, 5, 10, np.inf]
        self.PALLET_CLASS = []

        # 库位类型参数
        self.LOCATION_COLUMN = ['储位类型', '长(cm)', '宽(cm)', '高(cm)', '库容利用率', '有效库容(m³)', 'sku限制', '库容坪效系数']
        self.LOCATION_DF = pd.DataFrame(columns=self.LOCATION_COLUMN)


        ## 库龄等级
        self.AGE_INTERVAL = [0, 30, 60, 90,120,180,360,np.inf]
        self.AGE_CLASS = []


    def update_location_volume(self):
        '''
        根据库位类型的长宽高及容积率，更新库位类型的有效库容
        若存在最小容积率参数，计算库容下限
        :return:
        '''
        # 计算不同库位的有效库容
        self.PALLET['valid_vol'] = self.PALLET['length'] * pow(10, -3) * self.PALLET['width'] * pow(10, -3) * self.PALLET['height'] * self.PALLET['ratio'] * pow(10, -3)
        self.BOX['valid_vol'] = self.BOX['length'] * pow(10, -3) * self.BOX['width'] * pow(10, -3) * self.BOX['height'] * self.BOX['ratio'] * pow(10, -3)
        self.CARTON['valid_vol'] = self.CARTON['length'] * pow(10, -3) * self.CARTON['width'] * pow(10, -3) * self.CARTON['height'] * self.CARTON['ratio'] * pow(10, -3)
        self.TOTE['valid_vol'] = self.TOTE['length'] * pow(10, -3) * self.TOTE['width'] * pow(10, -3) * self.TOTE['height'] * self.TOTE['ratio'] * pow(10, -3)

        self.PP['valid_vol'] = self.PP['length'] * pow(10, -3) * self.PP['width'] * pow(10, -3) * self.PP['height'] * self.PP['ratio'] * pow(10, -3)
        self.PP_YX['valid_vol'] = self.PP_YX['length'] * pow(10, -3) * self.PP_YX['width'] * pow(10, -3) * self.PP_YX['height'] * self.PP_YX['ratio'] * pow(10, -3)
        self.PP_CC['valid_vol'] = self.PP_CC['length'] * pow(10, -3) * self.PP_CC['width'] * pow(10, -3) * self.PP_CC['height'] * self.PP_CC['ratio'] * pow(10, -3)
        self.YX_GJ['valid_vol'] = self.YX_GJ['length'] * pow(10, -3) * self.YX_GJ['width'] * pow(10, -3) * self.YX_GJ['height'] * self.YX_GJ['ratio'] * pow(10, -3)

        # 计算不同库位的最小库容
        self.PALLET['min_vol'] = self.PALLET['valid_vol'] * self.PALLET['min_ratio']
        self.BOX['min_vol'] = self.BOX['valid_vol'] * self.BOX['min_ratio']
        self.CARTON['min_vol'] = self.CARTON['valid_vol'] * self.CARTON['min_ratio']
        self.TOTE['min_vol'] = self.TOTE['valid_vol'] * self.TOTE['min_ratio']

        self.PP['min_vol'] = self.PP['valid_vol'] * self.PP['min_ratio']
        self.PP_YX['min_vol'] = self.PP_YX['valid_vol'] * self.PP_YX['min_ratio']
        self.PP_CC['min_vol'] = self.PP_CC['valid_vol'] * self.PP_CC['min_ratio']
        self.YX_GJ['min_vol'] = self.YX_GJ['valid_vol'] * self.YX_GJ['min_ratio']


    def get_pallet_classification(self):
        len_interval = len(self.PALLET_INTERVAL)-1


        for i in range(len_interval):
            tmp = []
            if i == len_interval - 1:
                tmp.append("P" + str(i + 1) + "(" + str(self.PALLET_INTERVAL[i]) + ",+)")
                tmp.append(self.PALLET_INTERVAL[i])
                tmp.append(np.inf)
                self.PALLET_CLASS.append(tmp)
            elif i < 9:
                tmp.append(
                    "P" + str(i + 1) + "(" + str(self.PALLET_INTERVAL[i]) + "," + str(
                        self.PALLET_INTERVAL[i + 1]) + "]")
                tmp.append(self.PALLET_INTERVAL[i])
                tmp.append(self.PALLET_INTERVAL[i + 1])
                self.PALLET_CLASS.append(tmp)
            else:
                tmp.append(
                    "P" + str(i + 1) + "(" + str(self.PALLET_INTERVAL[i]) + "," + str(
                        self.PALLET_INTERVAL[i + 1]) + "]")
                tmp.append(self.PALLET_INTERVAL[i])
                tmp.append(self.PALLET_INTERVAL[i + 1])
                self.PALLET_CLASS.append(tmp)

        # print(self.PALLET_CLASS)


    def get_location_type(self):

        # 写入不同存储类型的参数
        self.LOCATION_DF.at[0, self.LOCATION_COLUMN] = ['卡板区', self.PALLET['length'], self.PALLET['width'], self.PALLET['height'],
                                                        self.PALLET['ratio'], self.PALLET['valid_vol'], self.PALLET['sku_max'], self.PALLET['库容坪效系数']]
        self.LOCATION_DF.at[1, self.LOCATION_COLUMN] = ['原箱区', self.BOX['length'], self.BOX['width'], self.BOX['height'],
                                                        self.BOX['ratio'], self.BOX['valid_vol'], self.BOX['sku_max'], self.BOX['库容坪效系数']]
        self.LOCATION_DF.at[2, self.LOCATION_COLUMN] = ['储位盒区', self.CARTON['length'], self.CARTON['width'], self.CARTON['height'],
                                                        self.CARTON['ratio'], self.CARTON['valid_vol'], self.CARTON['sku_max'],self.CARTON['库容坪效系数']]
        self.LOCATION_DF.at[3, self.LOCATION_COLUMN] = ['料箱区', self.TOTE['length'], self.TOTE['width'], self.TOTE['height'],
                                                        self.TOTE['ratio'], self.TOTE['valid_vol'], self.TOTE['sku_max'],self.TOTE['库容坪效系数']]

        self.LOCATION_DF.at[4, self.LOCATION_COLUMN] = ['批量平铺区', self.PP['length'], self.PP['width'], self.PP['height'],
                                                        self.PP['ratio'], self.PP['valid_vol'], self.PP['sku_max'],self.PP['库容坪效系数']]
        self.LOCATION_DF.at[5, self.LOCATION_COLUMN] = ['超长平铺区', self.PP_CC['length'], self.PP_CC['width'], self.PP_CC['height'],
                                                        self.PP_CC['ratio'], self.PP_CC['valid_vol'], self.PP_CC['sku_max'],self.PP_CC['库容坪效系数']]
        self.LOCATION_DF.at[6, self.LOCATION_COLUMN] = ['异形平铺区', self.PP_YX['length'], self.PP_YX['width'], self.PP_YX['height'],
                                                        self.PP_YX['ratio'], self.PP_YX['valid_vol'], self.PP_YX['sku_max'],self.PP_YX['库容坪效系数']]
        self.LOCATION_DF.at[7, self.LOCATION_COLUMN] = ['异形高架区', self.YX_GJ['length'], self.YX_GJ['width'], self.YX_GJ['height'],
                                                        self.YX_GJ['ratio'], self.YX_GJ['valid_vol'], self.YX_GJ['sku_max'],self.YX_GJ['库容坪效系数']]


    def get_age_type(self):
        len_interval = len(self.AGE_INTERVAL) - 1

        for i in range(len_interval):
            tmp = []
            if i == len_interval - 1:
                tmp.append("D" + str(i + 1) + "(" + str(self.AGE_INTERVAL[i]) + ",+)")
                tmp.append(self.AGE_INTERVAL[i])
                tmp.append(np.inf)
                self.AGE_CLASS.append(tmp)
            elif i < 9:
                tmp.append(
                    "D" + str(i + 1) + "(" + str(self.AGE_INTERVAL[i]) + "," + str(
                        self.AGE_INTERVAL[i + 1]) + "]")
                tmp.append(self.AGE_INTERVAL[i])
                tmp.append(self.AGE_INTERVAL[i + 1])
                self.AGE_CLASS.append(tmp)
            else:
                tmp.append(
                    "P" + str(i + 1) + "(" + str(self.AGE_INTERVAL[i]) + "," + str(
                        self.AGE_INTERVAL[i + 1]) + "]")
                tmp.append(self.AGE_INTERVAL[i])
                tmp.append(self.AGE_INTERVAL[i + 1])
                self.AGE_CLASS.append(tmp)

        # print(self.AGE_CLASS)


    def run(self):
        self.update_location_volume()
        self.get_pallet_classification()
        self.get_location_type()
        self.get_age_type()





# if __name__ == '__main__':
#     config = Config()
#     config.run()

