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


def packing(skuList, ctnSize=None):
    # print('---------------------------------- ')
    # print('skuList: ', skuList)
    # print('ctnSize: ', ctnSize)

    containerVol = ctnSize[0] * ctnSize[1] * ctnSize[2]

    # 已装sku数量 packed_list = [packedNum, packedVol]
    packed_result_list = [0, 0]
    usedPoint = []
    skuNum = len(skuList)

    O = (0, 0, 0)  # 原点坐标
    show_num = [make(O, ctnSize)]


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
            return ratio
        else:
            return 0



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
def make(O,C):
    data = [O[0],O[1],O[2],C[0],C[1],C[2]]
    return data

#可用点的生成方法
def newsite(O,B_i):
    # 在X轴方向上生成
    O1 = (O[0]+B_i[0],O[1],O[2])
    # 在Y轴方向上生成
    O2 = (O[0],O[1]+B_i[1],O[2])
    # 在Z轴方向上生成
    O3 = (O[0],O[1],O[2]+B_i[2])
    return [O1,O2,O3]

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
                new_show = make(O_items[i-1],Box_list[i])
                if new_show not in show_num:
                    show_num.append(make(O_items[i-1],Box_list[i]))
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
                        new_show = make(O_items[i-1],Box_list[i])
                        if new_show not in show_num:
                            show_num.append(make(O_items[i-1],Box_list[i]))
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


def load_data(file_path, file_name, isMulti=True, ctn_list=None):
    if ".xlsx" in file_name:
        df = pd.read_excel('{}{}'.format(file_path, file_name))
    else:
        try:
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='utf-8')
        except:
            df = pd.read_csv('{}{}'.format(file_path, file_name), encoding='gbk')

    print('============', '数据导入完成！', '============ ')
    print('原始数据行数： ', df.shape[0], '\t数据列数： ', df.shape[1])
    print('原始订单数： ', df['订单号'].nunique())

    # 合并长宽高，按长度降序排列，格式为元祖
    df['l_w_h'] = df[['实际长cm', '实际宽cm', '实际高cm']].apply(lambda x: tuple(sorted(x, reverse=True)),axis=1)

    df['skuSize_temp'] = (df['l_w_h'] * df['产品内件数']).apply(lambda x: [x[i:i + 3] for i in range(0, len(x), 3)])
    df['skuSize'] = df['skuSize_temp'].apply(lambda x: x[0])


    # 合并多品订单中SKU尺寸，合并为tuple的列表, 按SKU尺寸降序
    # order_df = df.groupby('订单号')['skuSize'].apply(list).reset_index()
    order_df= df.groupby('订单号')['skuSize'].apply(lambda x: list(sorted(x, reverse=True))).reset_index()
    order_df['qty'] = order_df['skuSize'].apply(len)

    if isMulti:
        order_df = order_df.drop(order_df[order_df['qty'] ==1].index)
        order_df['订单结构'] = '多件'

    df = pd.merge(order_df[['订单号', 'qty']], df, on=['订单号'], how='left')
    df = df.drop(df[df['qty'] ==1].index)
    print(df.columns)

    # 合并多品订单中SKU货型，合并为字符串
    # ‘产品货型’ 为系统按尺寸和重量计算的货型
    order_size_df = df.groupby('订单号')['产品货型'].apply(lambda x: np.unique(x)).reset_index()
    # order_size_df = df.groupby(['订单号'])['产品货型'].unique().agg('-'.join).reset_index()

    # 'new_sku_size' 为按sku尺寸计算的货型
    order_size_df2 = df.groupby('订单号')['new_sku_size'].apply(lambda x: np.unique(x)).reset_index()

    order_size_df = pd.merge(order_size_df, order_size_df2, on=['订单号'])


    order_detail = df[['订单号', '客户代码', '创建时间 仓库当地', '区域仓编码']].drop_duplicates()

    temp_df = pd.merge(order_detail, order_size_df, on=['订单号'], how='left')
    order_df = pd.merge(order_df, temp_df, on=['订单号'], how='left').reset_index()

    # 删除多品订单件数为1的行
    # 由于单品单件和单品多件都需要 试装箱，可以不剔除

    print('============', '数据处理完成！', '============ ')
    print('多件订单数： ', order_df.shape[0])

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


def run_packing(order_df, ctn_df, ctn_list, ctn_dict=None, carton_type=None):
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

    for i in range(n):

        if i+1<10:
            num = '0{}'.format(i+1)
        else:
            num = str(i+1)

        print('='*15, '箱型{}: '.format(i+1), ctn_list[i])
        order_df['r{}'.format(num)] = order_df['skuSize'].apply(lambda x: packing(x[:], ctn_list[i]))
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

    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    order_df.to_csv('{}{}'.format(file_path, '多件装箱明细_{}_{}.csv'.format(carton_type, str_time)), index=False, na_rep='Null')
    re_df.to_csv('{}{}'.format(file_path, '多件装箱结果_{}_{}.csv'.format(carton_type, str_time)), index=False, na_rep='Null')


if __name__ == '__main__':

    print('\n')
    startTime = datetime.now()
    print('-' * 20 + '程序开始' + '-' * 20 + '\n')

    # 谷仓现有6种箱型
    # size1 = (19, 14, 9)
    # size2 = (29, 19, 14)
    # size3 = (34, 24, 19)
    # size4 = (39, 29, 19)
    # size5 = (49, 39, 29)
    # size6 = (59, 39, 29)
    #
    # ctn_list = [size1, size2, size3, size4, size5, size6]
    # ctn_list = (19, 14, 9)

    # 文件路径
    file_path = 'D:/Documents/Desktop/箱型推荐/'

    # file_name = 'multiTest.csv'
    # file_name = 'multiQty_March.csv'
    file_name = 'multiQtyOrder_12&3.csv'

    carton_type = 'Mixed-2'
    carton_file_name = 'Mixed-2 carton size.csv'


    order_df = load_data(file_path, file_name)
    carton_list , ctn_dict, ctn_df = load_carton(file_path, carton_file_name)

    run_packing(order_df=order_df, ctn_df=ctn_df, ctn_list=carton_list, ctn_dict=ctn_dict, carton_type=carton_type)

    print('\n')
    print('='*15, '订单数据预览', '='*15)
    print(order_df.head(10))


    print('-' * 20 + '程序运行完成！' + '-' * 20 + '\n')
    endTime = datetime.now()
    print('-' * 50)
    print('程序运行总时间：', (endTime - startTime).seconds, ' S')

    # pack = Packing(pltSize)
    # pack.run()






