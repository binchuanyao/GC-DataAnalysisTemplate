# -*- coding: utf-8 -*-
# @File   : inventory
# @Time   : 2022/02/14 10:44
# @Author : BCY


from inventory import *
from outbound import *
from inbound import *
import warnings
warnings.filterwarnings('ignore')

import sys
import company

from PyQt5.QtWidgets import QApplication,QMainWindow


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#
#     print('\n')
#     startTime = datetime.now()
#     print('-' * 20 + '程序开始' + '-' * 20 + '\n')
#
#
#     file_path = 'D:/Documents/Desktop/Python DA data/'
#
#
#     '''库存分析'''
#
#     inventory_file_name = '在库批次库存数据明细_美东8仓.csv'
#
#     ### 导入数据
#     df = load_inventory_data(file_path, inventory_file_name)
#     sku_info_df = load_sku_data(file_path, inventory_file_name)
#     customer_pivot = get_customer_pivot(df)
#
#
#     # ### 计算推荐库位，将分析结果写入excel文件
#     df = calculate_single_location(df, file_path)
#     sku_pivot = get_sku_pivot(df)
#
#
#
#     '''出库分析'''
#
#     outbound_file_name = '出库数据_美东8仓.csv'
#     time_file_name = '出库时间_美东8仓.csv'
#
#     ob_df = load_outbound_data(file_path, outbound_file_name, time_file_name)
#
#
#     outbound_analyse(ob_df, file_path, customer_pivot, sku_pivot)
#
#
#     '''入库分析'''
#     inbound_file_name = '入库数据_美东8仓.csv'
#
#     inbound_df =  load_inbound_data(file_path, inbound_file_name)
#
#     inbound_analyse(inbound_df, output_path=file_path)
#
#
#
#     print('-' * 20 + '程序运行完成！' + '-' * 20 + '\n')
#     endTime = datetime.now()
#     print('-' * 50)
#     print('程序运行总时间：', (endTime - startTime).seconds, ' S')
#
#
#     # input('Press ENTER to Exit !!!')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = company.Ui_MainWindow()
    # 向主窗口上添加控件
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())



