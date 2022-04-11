# -*- coding: utf-8 -*-
# @File   : inbound
# @Time   : 2022/02/15 13:57 
# @Author : BCY
import pandas as pd

from inventory import *


def load_inbound_data(file_path, inventory_fileName):
    '''
    从本地路径导入原始数据
    :param inventory_fileName: 完整的路径+文件名
    :return: 原始数据的dataframe形式
    '''
    # import inBound and outBound source data
    if ".xlsx" in inventory_fileName:
        data = pd.read_excel('{}{}'.format(file_path,inventory_fileName))
    else:
        data = pd.read_csv('{}{}'.format(file_path,inventory_fileName))



    ### 交互界面，输入EIQ分析的有效字段编号
    print('\n')
    print('请按以下字段顺序输入 入库明细 对应的列号：（列号从0开始，以空格隔开以enter结束）')
    print('收货日期 最早签收日期 入库单号 入库单类型 货运方式 海柜号 跟踪号 客户代码 箱号 产品代码 产品货型 收货数量 收货体积')

    # column_index = [int(x) for x in input().split()]
    detail_index = [16, 8, 6, 7, 3, 14, 20, 10, 17, 4, 19, 24, 21]
    column_name = data.columns.tolist()

    # print('column_index: ', detail_index)

    detail_columns = []
    for i in detail_index:
        detail_columns.append(column_name[i])

    # print('detail_columns: ', detail_columns)

    detail_data = data[detail_columns]
    valid_columns_name = ['date', 'receive_time','inboundID', 'inbound_type', 'delivery_mode', 'containerNO', 'trackingNO',
                          'customer', 'cartonNO', 'sku', 'sku_size', 'quantity', 'Vol(m³)']
    detail_data.columns = valid_columns_name

    ### 日期列转化为Python日期格式
    detail_data['date'] = pd.to_datetime(detail_data['date'])
    detail_data['receive_time'] = pd.to_datetime(detail_data['receive_time'])
    detail_data['receive_date'] = detail_data['receive_time'].dt.date
    detail_data['month'] = detail_data['date'].dt.month

    detail_data['deliveryNO'] = detail_data['containerNO']
    detail_data.loc[(detail_data['containerNO'].str.len()<=1), ['deliveryNO']] = detail_data['trackingNO']

    print(detail_data.dtypes)
    print(detail_data.head(10))
    return detail_data



def inbound_analyse(df, output_path):
    '''
    入库分析
    :param df: 入库分析数据源
    :param output_path: 结果写入目录
    :return:
    '''

    print('*' * 10, '入库分析数据量', '*' * 10)
    print(df.shape)
    print('*' * 10, '入库数据字段及类型', '*' * 10)
    print(df.dtypes)
    print('*' * 10, '入库分析数据源预览', '*' * 10)
    print(df.head(10))

    '''C01 入库货型分布'''

    inbound_dist_df = get_inbound_distribution(df, period=['2022-02-15', '2022-03-01'])


    ''' C02 入库箱型及SKU分布'''
    carton_df, sku_df, daily_container_df = get_carton_distribution(df, period=['2022-02-15', '2022-03-01'])

    '''
    计算结果写入Excel表格
    '''
    ### write to file
    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}入库分析_{}.xlsx'.format(output_path, str_time))

    format_data(writer=writer, df=inbound_dist_df, sheet_name='C01-入库货型')
    format_data(writer=writer, df=carton_df, sheet_name='C02-箱型分布')
    format_data(writer=writer, df=sku_df, sheet_name='C03-单箱SKU分布')
    format_data(writer=writer, df=daily_container_df, sheet_name='C04-日来柜数量')

    writer.save()


def get_inbound_distribution(df, month=None, date=None, period=None):
    '''
    计算海柜及跟踪号的件型分布
    '''
    index = ['deliveryNO', 'delivery_mode']

    if month is not None:
        df = df.query('month == {}'.format(month))
        index = ['month'] + index
    elif date is not None:
        df = df.query('date == "{}"'.format(date))
        index = ['date'] + index
    elif period is not None:
        if len(period) == 2:
            df = df.query('date >= "{}" & date <= "{}"'.format(period[0], period[1]))
            index = ['date'] + index
    else:
        pass

    sort_size = ['XL', 'L2', 'L1', 'M', 'S', 'XS']
    df['sku_size'] = pd.Categorical(df['sku_size'], sort_size)

    ## 客户在库体积及在库件数
    delivery_df = pd.pivot_table(df, index=index,
                                 values=['Vol(m³)', 'quantity'],
                                 columns=['sku_size'],
                                 aggfunc='sum',
                                 margins=True,
                                 margins_name='All',
                                 fill_value=0).reset_index()

    ## 按客户总体积排序
    delivery_df = delivery_df.sort_values(by=('Vol(m³)', 'All'), ascending=False, ignore_index=True)

    ### 多级索引转成单层索引
    col = []
    for (s1, s2) in delivery_df.columns:
        if len(s2) > 0:
            col.append(s1 + '_' + str(s2))
        else:
            col.append(s1)
    # delivery_df.columns = [ s1 + '_' + str(s2) for (s1, s2) in delivery_df.columns]
    delivery_df.columns = col


    ## 计算体积货型占比
    for item in sort_size:
        delivery_df[('Vol(m³)_{}%'.format(item))] = delivery_df[('Vol(m³)_{}'.format(item))] / delivery_df[('Vol(m³)_All')]

    ## 计算件数货型占比
    for item in sort_size:
        delivery_df[('quantity_{}%'.format(item))] = delivery_df[('quantity_{}'.format(item))] / delivery_df[('quantity_All')]

    print(delivery_df.dtypes)
    print('delivery_df.shape ', delivery_df.shape)
    print(delivery_df.head(10))

    return delivery_df


def get_carton_distribution(df, month=None, date=None, period=None):
    index = ['cartonNO']
    if month is not None:
        df = df.query('month == {}'.format(month))
        index = ['month'] + index
    elif date is not None:
        df = df.query('date == "{}"'.format(date))
        index = ['date'] + index
    elif period is not None:
        if len(period) == 2:
            df = df.query('date >= "{}" & date <= "{}"'.format(period[0], period[1]))
            index = ['date'] + index
    else:
        pass

    carton_df = pd.pivot_table(df, index=index,
                               values=['quantity', 'sku'],
                               aggfunc={'quantity':np.sum, 'sku':pd.Series.nunique},
                               fill_value=0).reset_index()

    carton_df['carton_type'] = '异常'

    carton_df.loc[(carton_df['quantity'] == 1) & (carton_df['sku'] == 1), ['carton_type']] = '单箱单件'
    carton_df.loc[(carton_df['quantity'] > 1) & (carton_df['sku'] == 1), ['carton_type']] = '单箱单品'
    carton_df.loc[(carton_df['quantity'] > 1) & (carton_df['sku'] > 1), ['carton_type']] = '单箱多品'

    print('carton_type value count: ', df)

    carton_df['sku_type'] = carton_df['sku'].astype(np.str) + 'SKU'
    carton_df.loc[(carton_df['sku'] > 10), ['sku_type']] = '>10SKU'

    marge_index = ['cartonNO', 'carton_type', 'sku_type']

    df = pd.merge(df, carton_df[marge_index], on=['cartonNO'], how='left')

    # print('carton_type value count: ', df['carton_type'].value_counts())
    # print('sku_type value count: ', df['sku_type'].value_counts())


    '''箱型分布'''
    carton_type_pivot = pd.pivot_table(df, index=['deliveryNO', 'delivery_mode'],
                                   values=['Vol(m³)', 'cartonNO', 'quantity'],
                                   columns=['carton_type'],
                                   aggfunc={'Vol(m³)':np.sum, 'cartonNO':pd.Series.nunique, 'quantity':np.mean},
                                   fill_value=0).reset_index()

    carton_type =['单箱单件', '单箱单品', '单箱多品', '异常']


    ### 多级索引转成单层索引
    carton_type_col = []
    for (s1, s2) in carton_type_pivot.columns:
        if len(s2) > 0:
            carton_type_col.append(s1 + '_' + str(s2))
        else:
            carton_type_col.append(s1)
    carton_type_pivot.columns = carton_type_col


    ## 增加 均箱体积
    for t in carton_type[:3]:
        carton_type_pivot['均箱体积_{}'.format(t)] = carton_type_pivot['Vol(m³)_{}'.format(t)]/carton_type_pivot['cartonNO_{}'.format(t)]
        carton_type_pivot['均箱体积_{}'.format(t)] = carton_type_pivot['均箱体积_{}'.format(t)].fillna(0)

    # 总体积及总箱数
    carton_type_pivot['总体积'] = sum([carton_type_pivot['Vol(m³)_{}'.format(t)] for t in carton_type])
    carton_type_pivot['总箱数'] = sum([carton_type_pivot['cartonNO_{}'.format(t)] for t in carton_type])
    carton_type_pivot['总均箱体积'] = carton_type_pivot['总体积'] / carton_type_pivot['总箱数']

    # print('箱型分布')
    # print(carton_type_pivot.shape)
    # print(carton_type_pivot.head(20))


    '''箱内SKU分布'''
    sku_index = ['deliveryNO', 'delivery_mode']
    sku_type_pivot = pd.pivot_table(df, index=sku_index,
                                   values=['cartonNO'],
                                   columns=['sku_type'],
                                   aggfunc={'cartonNO':pd.Series.nunique},
                                   fill_value=0).reset_index()
    ### 多级索引转成单层索引
    sku_type_col = []
    for (s1, s2) in sku_type_pivot.columns:
        if len(s2) > 0:
            sku_type_col.append(s1 + '_' + str(s2))
        else:
            sku_type_col.append(s1)
    sku_type_pivot.columns = sku_type_col

    # 增加总箱数
    sku_type_pivot['总箱数'] = sku_type_pivot.sum(axis=1)

    ### 最早签收时间
    earliest_time = pd.pivot_table(df, index=['deliveryNO'],
                                   values=['receive_date'],
                                   aggfunc=np.min,
                                   fill_value=0).reset_index()

    sku_type_pivot = pd.merge(sku_type_pivot, earliest_time, on=['deliveryNO'], how='left')
    sku_type_pivot = sku_type_pivot.sort_values(by='receive_date', ignore_index=True)



    '''日来柜数量'''
    daily_container_df = pd.pivot_table(df, index=['receive_date'],
                                        values=['containerNO', 'deliveryNO' , 'trackingNO'],
                                        aggfunc=pd.Series.nunique,
                                        fill_value=0).reset_index()


    ### 去掉海柜号或跟踪号为空的计数
    daily_container_df['trackingNO'] = daily_container_df['trackingNO'] - 1
    daily_container_df['containerNO'] = daily_container_df['deliveryNO'] - daily_container_df['trackingNO']

    ### 重排列
    daily_container_df = daily_container_df[['receive_date', 'containerNO', 'trackingNO', 'deliveryNO']]

    daily_container_df['receive_interval_days'] = pd.to_timedelta(daily_container_df['receive_date'] - daily_container_df['receive_date'].shift(1)).dt.days

    daily_container_df = daily_container_df.fillna(0)


    # print(sku_type_pivot.dtypes)
    # print(sku_type_pivot.shape)
    # print(sku_type_pivot.head(10))

    return carton_type_pivot, sku_type_pivot, daily_container_df
