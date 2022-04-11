# -*- coding: utf-8 -*-
# @File   : inventory
# @Time   : 2022/02/14 10:44 
# @Author : BCY
import pandas as pd

from config import *
from datetime import datetime


# 实例化配置参数, 全局变量
config = Config()
config.run()

pd.set_option('display.max_columns', None)

def load_inventory_data(file_path, inventory_file_name, date=None):
    '''
    从本地路径导入原始数据
    :param inventory_fileName: 完整的路径+文件名
    :return: 原始数据的dataframe形式
    '''
    # import inBound and outBound source data
    if ".xlsx" in inventory_file_name:
        data = pd.read_excel('{}{}'.format(file_path,inventory_file_name))
    else:
        try:
            print('*' * 10, 'utf-8', '*' * 10)
            data = pd.read_csv('{}{}'.format(file_path,inventory_file_name), encoding='utf-8')
        except:
            print('*' * 10, 'gbk-8', '*' * 10)
            data = pd.read_csv('{}{}'.format(file_path, inventory_file_name), encoding='gbk')

    cols = data.columns
    if '在库体积(M³)' in cols:
        col = ['Month Key', '批次库存日期', '系统来源', '区域仓名称', '区域仓编码', '物理仓名称', '物理仓名称en', '物理仓编码', '客户代码',
               '上架日期', '产品代码', '货物属性', '一级品类', '二级品类', '三级品类', '产品货型',
               '储位类型', '层', '层级属性', '库位类型代码',
               '产品实际长(Cm)', '产品实际宽(Cm)', '产品实际高(Cm)', '产品实际重量(Kg)', '在库件数', '在库体积(M³)', '在库重量(Kg)']
    else:

        col = ['Month Key', '批次库存日期', '系统来源', '区域仓名称', '区域仓编码', '物理仓名称', '物理仓名称en', '物理仓编码', '客户代码',
               '上架日期', '产品代码', '货物属性', '一级品类', '二级品类', '三级品类', '产品货型',
               '储位类型', '层', '层级属性', '库位类型代码',
               '产品实际长(Cm)', '产品实际宽(Cm)', '产品实际高(Cm)', '产品实际重量(Kg)', '在库件数', '在库体积(M3)', '在库重量(Kg)']



    new_col = ['Month Key', '批次库存日期', '系统来源', '区域仓名称', '区域仓编码', '物理仓名称', '物理仓名称en', '物理仓编码', '客户代码',
           '上架日期', '产品代码', '货物属性', '一级品类', '二级品类', '三级品类', '产品货型',
           '储位类型', '层', '层级属性', '库位类型代码',
           '长(cm)',  '宽(cm)', '高(cm)', '重量(kg)', '在库件数', '在库体积(m³)', '在库重量(kg)']



    # print('\n', data.dtypes)
    df = data[col]
    df.columns = new_col

    date_col = []

    # 将日期格式列由字符转化日期格式
    # for x in df.columns.tolist():
    #     if '日期' in x:
    #         date_col.append(x)
    #
    # print(df[date_col])
    # df[date_col].apply(pd.to_datetime, format='%Y/%m/%d')

    df['批次库存日期'] = pd.to_datetime(df['批次库存日期'])
    df['上架日期'] = pd.to_datetime(df['上架日期'])

    print('*'*10, '数据导入', '*'*10, '\n')
    print('字段类型：')
    print(df.dtypes)

    # 返回指定日期的批次库存数据,否则返回所有数据
    if date is None:
        return df
    else:
        return df.where(data['批次库存日期'] == date)



def load_sku_data(file_path, inventory_file_name):
    '''
    从本地路径导入原始数据
    :param inventory_fileName: 完整的路径+文件名
    :return: 原始数据中sku-货型的dataframe形式
    '''
     # import inBound and outBound source data
    if ".xlsx" in inventory_file_name:
        data = pd.read_excel('{}{}'.format(file_path,inventory_file_name))
    else:
        try:
            data = pd.read_csv('{}{}'.format(file_path,inventory_file_name), encoding='utf-8')
        except:
            data = pd.read_csv('{}{}'.format(file_path, inventory_file_name), encoding='gbk')

    print(data.dtypes)
    print(data.shape)
    cols = ['产品代码', '产品货型', '产品实际长(Cm)', '产品实际宽(Cm)', '产品实际高(Cm)']

    sku_df = data[cols].drop_duplicates()
    print(sku_df.dtypes)
    print(sku_df.shape)
    sku_df.columns = ['sku', 'sku_size', 'length', 'width', 'height']

    sku_df['vol'] = sku_df['length'] * sku_df['width'] * sku_df['height'] * pow(10,-6)

    return sku_df


def get_customer_pivot(df):
    ### 客户维度的库存，sku数，库存深度
    customer_cols = ['客户代码', '产品代码', '在库件数', '在库体积(m³)']

    temp_df = df[customer_cols]

    customer_df = pd.pivot_table(df[customer_cols], index=['客户代码'],
                                 values=['产品代码', '在库件数', '在库体积(m³)'],
                                 aggfunc={'产品代码':pd.Series.nunique, '在库件数':np.sum, '在库体积(m³)':np.sum},
                                 margins=True,
                                 margins_name='总计',
                                 fill_value=0).reset_index()

    customer_df.columns = ['customer', 'sku数', '在库件数', '在库体积(m³)']
    customer_df['库存深度(件/sku)'] = customer_df['在库件数']/customer_df['sku数']
    customer_df['库存深度(m³/sku)'] = customer_df['在库体积(m³)'] / customer_df['sku数']

    return customer_df



def get_sku_pivot(df):
    '''

    :param df: 数据源
    :return: 返回sku维度的在库件数、在库体积、库龄的透视表
    '''

    ## sku在库体积及在库件数
    df_vol = pd.pivot_table(df, index=['产品代码'],
                            values=[ '在库件数', '在库体积(m³)'],
                            aggfunc=np.sum,
                            margins=False,
                            fill_value=0).reset_index()

    ## sku在库件数的加权库龄
    df_age = pd.pivot_table(df, index=['产品代码'],
                            values=['库龄'],
                            aggfunc=lambda rows: np.average(rows, weights=df.loc[rows.index, '在库件数']),
                            margins=False,
                            fill_value=0).reset_index()

    df_sku = pd.merge(df_vol, df_age, on=['产品代码'])

    ## 计算sku维度库龄类别   AGE_CLASS 数据结构为[['D1(0,30]', 0, 30], ['D2(30,60]', 30, 60]] 二维列表，其中的元素为【等级，左区间，右区间】
    df_sku['库龄等级'] = ''
    rank_num = len(config.AGE_CLASS)
    for i in range(rank_num):
        df_sku.loc[(df_sku['库龄'] > config.AGE_CLASS[i][1]) & (df_sku['库龄'] <= config.AGE_CLASS[i][2]), ['库龄等级']] = config.AGE_CLASS[i][0]

    sku_col = ['sku', 'inv_quantity', 'inv_Vol(m³)', 'age', 'age_class']
    df_sku.columns = sku_col

    return df_sku



def calculate_single_location(df, output_path):

    # df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWeight'] == 0), ['corrWeight']] = I_class_avg['weight']

    df['在库托数'] = df['在库体积(m³)'] / config.PALLET['valid_vol']

    df['是否超长']= 'N'
    df.loc[(df['长(cm)'] >= config.SUPER_LONG_PARAM) , ['是否超长']] = 'Y'

    df['是否批量'] = 'N'
    df.loc[(df['在库托数'] >= config.BATCH_PARAM), ['是否批量']] = 'Y'

    df['储位类型'] = np.NAN
    df.loc[(df['储位类型'].isna()) & (df['是否批量'] == 'Y') , ['储位类型']] = '批量平铺区'
    df.loc[(df['储位类型'].isna()) & (df['是否超长'] == 'Y'), ['储位类型']] = '超长平铺区'
    df.loc[(df['储位类型'].isna()) & (df['是否超长'] == 'N') & (df['产品货型'] == 'XL'), ['储位类型']] = '异形高架区'
    df.loc[(df['储位类型'].isna()) & (df['产品货型'] == 'L1') | (df['产品货型'] == 'L2'), ['储位类型']] = '卡板区'
    df.loc[(df['储位类型'].isna()) & (df['在库体积(m³)'] >= config.PALLET['min_vol']), ['储位类型']] = '卡板区'
    df.loc[(df['储位类型'].isna()) & (df['在库体积(m³)'] >= config.BOX['min_vol']), ['储位类型']] = '原箱区'
    df.loc[(df['储位类型'].isna()), ['储位类型']] = '储位盒区'

    df['储区类型'] = df['储位类型']
    # df.loc[(df['储位类型'] =='卡板区') & (df['在库托数']==1), ['储区类型']] = '单卡板区'
    # df.loc[(df['储位类型'] == '卡板区') & (df['在库托数'] >= config.PALLET_INTERVAL[2]) & (df['在库托数'] <= 2), ['储区类型']] = '单卡板区'
    pltClassNum = len(config.PALLET_CLASS)
    for i in range(pltClassNum):
        df.loc[(df['储位类型']=='卡板区') &
            (df['在库托数'] > config.PALLET_CLASS[i][1]) &
            (df['在库托数'] <= config.PALLET_CLASS[i][2]),
            ['储区类型']] = config.PALLET_CLASS[i][0]


    # 计算库龄
    df['库龄'] = pd.to_timedelta(df['批次库存日期'] - df['上架日期']).dt.days

    ## 计算库位维度库龄类别   AGE_CLASS 数据结构为[['D1(0,30]', 0, 30], ['D2(30,60]', 30, 60]] 二维列表，其中的元素为【等级，左区间，右区间】
    df['库龄等级'] = ''
    rank_num = len(config.AGE_CLASS)
    for i in range(rank_num):
        df.loc[(df['库龄'] > config.AGE_CLASS[i][1]) & (df['库龄'] <= config.AGE_CLASS[i][2]), ['库龄等级']] = config.AGE_CLASS[i][0]



    df_sku = get_sku_pivot(df)
    sku_col = ['产品代码', '在库件数',	'在库体积(m³)',	'库龄',	'库龄等级']
    df_sku.columns = sku_col


    '''
    将库存数据和sku维度数据，根据相关字段，提取透视表，写入文件
    '''
    # 以储位类型维度，统计库容、sku、库存深度等
    inventory_analysis(df, df_sku, output_path, index=['批次库存日期', '储位类型'])

    return df



def calculate_multi_location(df, output_path):
    # 实例化配置参数
    config = Config()
    config.run()

    print('data column: ', df.columns)



def inventory_analysis(df, df_sku, output_path, index=None, sku=None, pt_col=None):
    """
    :param df: 透视表原始数据
    :param df_sku: sku维度的库存原始数据
    :param output_path: 输出文件路径
    :param index: 透视的行
    :param sku: 是否添加 sku_ID 字段
    :param pt_col: 透视的 values，即透视字段
    :param isCumu: 默认为False, 是否计算累计比例
    :return:
    """

    if index is None:
        index = ['批次库存日期', '储位类型']

    if sku is None:
        sku = ['产品代码']

    if pt_col is None:
        pt_col = ['在库体积(m³)', '在库件数', '在库重量(kg)']

    # datetime64[ns]不能作为key,将日期列的格式转换为string
    df['批次库存日期'] = df['批次库存日期'].astype(str)
    df['上架日期'] = df['上架日期'].astype(str)
    df['Month Key'] = df['Month Key'].astype(str)


    # sku非重复计数
    dist_count_sku = df[index + sku].groupby(index).nunique()
    df_disCount = (pd.DataFrame(dist_count_sku)).reset_index()
    # print('sku非重复计数 \n', dist_count_sku)

    df_disCount = pd.pivot_table(df_disCount, index=index,
                                 aggfunc='sum',
                                 fill_value=0).reset_index()
    # 更新sku数列名
    sku = ['sku数']
    df_disCount.columns = index + sku

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0).reset_index()

    result_pt = pd.merge(df_disCount, tmp2, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + sku + pt_col]


    '''
    合并库位类型与透视结果
    '''
    print('库位类型： \n')
    print(config.LOCATION_DF)
    print('\n')

    df_location = pd.merge(config.LOCATION_DF, result_pt, on='储位类型', how='right', sort=False)

    # print('库存分析结果1： \n')
    # print(df_location.columns)
    # print('\n')


    # 计算库存深度
    df_location['库存深度(m³/sku)'] = df_location['在库体积(m³)']/df_location['sku数']
    df_location['库存深度(件/sku)'] = df_location['在库件数'] / df_location['sku数']

    df_location['单sku需求库位数'] = df_location['库存深度(m³/sku)'] / df_location['有效库容(m³)']
    df_location['库位需求1-库容最大化'] = np.ceil(df_location['在库体积(m³)'] / df_location['有效库容(m³)'])
    df_location['库位需求2-sku数最大化'] = np.ceil(df_location['在库体积(m³)'] / df_location['有效库容(m³)'])
    df_location['库位需求-现有库存'] = df_location[['库位需求1-库容最大化', '库位需求2-sku数最大化']].max(axis=1)
    df_location['库容饱和系数'] =  0.7
    df_location['规划库位需求数量'] = df_location['库位需求-现有库存'] / df_location['库容饱和系数']
    df_location['面积需求'] = df_location['在库体积(m³)'] / df_location['库容坪效系数']

    # index_num = len(index)
    # cols = list(result_pt.columns[index_num:])

    # 透视字段， 需计算总和及百分比的字段
    sum_col = ['sku数', '在库体积(m³)', '在库件数', '在库重量(kg)']

    row_n = df_location.shape[0]

    df_location.at[row_n, ['储位类型']] = '合计'
    df_location.at[row_n, sum_col] = df_location[sum_col].apply(lambda x: x.sum())

    df_location['库存深度(m³/sku)'] = df_location['在库体积(m³)']/df_location['sku数']
    df_location['库存深度(件/sku)'] = df_location['在库件数'] / df_location['sku数']


    sum_design_col = ['库位需求1-库容最大化', '库位需求2-sku数最大化', '库位需求-现有库存', '规划库位需求数量', '面积需求']
    df_location.at[row_n, sum_design_col] = df_location[sum_design_col].apply(lambda x: x.sum())



    # # 更新合计值
    # for i in range(len(sum_col)):
    #     df_location.loc[df_location[index[0]] == 'All', [sum_col[i]]] = df_location[sum_col[i]].sum()

    # 计算比例
    for i in range(len(sum_col)):
        df_location[sum_col[i] + '%'] = df_location[sum_col[i]] / (df_location[sum_col[i]].sum() / 2)


    # # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    # if isCumu:
    #     for i in range(len(sum_col)):
    #         # result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum().apply(lambda x: '%.2f%%' % (x * 100))
    #         df_location[sum_col[i] + '%_cumu'] = df_location[sum_col[i] + '%'].cumsum()

    '''
    库位需求结果 列重排
    '''

    re_columns = ['储位类型', '长(cm)', '宽(cm)', '高(cm)', '库容利用率', 'sku限制', '库容坪效系数',
                  '批次库存日期', '在库体积(m³)', '在库件数', 'sku数', '在库重量(kg)', '在库体积(m³)%', '在库件数%', 'sku数%', '在库重量(kg)%',
                  '库存深度(m³/sku)', '库存深度(件/sku)', '单sku需求库位数',
                  '库位需求1-库容最大化', '库位需求2-sku数最大化', '库位需求-现有库存', '库容饱和系数', '规划库位需求数量', '面积需求']

    df_location = df_location[re_columns]

    print('*'*10, '库存分析结果', '*'*10, '\n')
    print('字段名：')
    print(df_location.columns)
    print('\n')


    '''
    计算客户维度的件型分布
    '''

    sort_size = ['XL', 'L2', 'L1', 'M', 'S', 'XS']
    df['产品货型'] = pd.Categorical(df['产品货型'], sort_size)

    ## 客户在库体积及在库件数
    df_customer = pd.pivot_table(df, index=['客户代码'],
                                 values=['在库体积(m³)', '在库件数'],
                                 columns=['产品货型'],
                                 aggfunc='sum',
                                 margins=True,
                                 margins_name='总计',
                                 fill_value=0).reset_index()

    ## 按客户总体积排序
    df_customer = df_customer.sort_values(by=('在库体积(m³)', '总计'), ascending=False, ignore_index=True)

    ### 多级索引转成单层索引
    df_customer.columns = [s1 + '_' + str(s2) for (s1, s2) in df_customer.columns]


    ## 计算体积货型占比
    for item in sort_size:
        df_customer[('在库体积(m³)_{}%'.format(item))] = df_customer[('在库体积(m³)_{}'.format(item))] / df_customer[('在库体积(m³)_总计')]

    ## 计算件数货型占比
    for item in sort_size:
        df_customer[('在库件数_{}%'.format(item))] = df_customer[('在库件数_{}'.format(item))] / df_customer[('在库件数_总计')]



    ## 客户sku数
    # sku非重复计数
    customer_sku = df[['客户代码', '产品代码']].groupby('客户代码').nunique()
    customer_sku = (pd.DataFrame(customer_sku)).reset_index()



    customer_sku.columns = ['客户代码_', 'sku数']
    total_sku = sum(customer_sku['sku数'])

    ### 合并库存货型分布及sku数
    df_customer = pd.merge(df_customer, customer_sku, how='left', sort=False)

    ## 修改sku的总计值
    df_customer.loc[(df_customer['客户代码_'] =='总计'), ['sku数']] = total_sku

    ### 计算库存深度
    df_customer['库存深度(m³/sku)'] = df_customer['在库体积(m³)_总计'] / df_customer['sku数']
    df_customer['库存深度(件/sku)'] = df_customer['在库件数_总计'] / df_customer['sku数']

    df_customer['大件体积占比'] = df_customer['在库件数_XL%'] + df_customer['在库件数_L2%'] + df_customer['在库件数_L1%']

    df_customer['客户类型'] = np.NAN
    df['储位类型'] = np.NAN
    df_customer.loc[(df_customer['客户类型'].isna()) & (df_customer['大件体积占比'] >= 0.8 ), ['客户类型']] = '纯大货型'
    df_customer.loc[(df_customer['客户类型'].isna()) & (df_customer['大件体积占比'] >= 0.6 ), ['客户类型']] = '大货型'
    df_customer.loc[(df_customer['客户类型'].isna()) & (df_customer['大件体积占比'] >= 0.3), ['客户类型']] = '混货型'
    df_customer.loc[(df_customer['客户类型'].isna()), ['客户类型']] = '小货型'



    ### 重排列


    org_customer_columns = ['客户代码_', '在库体积(m³)_XL', '在库体积(m³)_L2', '在库体积(m³)_L1',  '在库体积(m³)_M', '在库体积(m³)_S', '在库体积(m³)_XS', '在库体积(m³)_总计',
                         '在库体积(m³)_XL%', '在库体积(m³)_L2%', '在库体积(m³)_L1%', '在库体积(m³)_M%', '在库体积(m³)_S%',  '在库体积(m³)_XS%',
                        '在库件数_XL', '在库件数_L2', '在库件数_L1', '在库件数_M', '在库件数_S',  '在库件数_XS', '在库件数_总计',
                        '在库件数_XL%', '在库件数_L2%', '在库件数_L1%',  '在库件数_M%', '在库件数_S%', '在库件数_XS%',
                        'sku数', '库存深度(m³/sku)', '库存深度(件/sku)', '大件体积占比', '客户类型']

    # new_customer_columns = ['客户代码', '在库体积(m³)_XL', '在库体积(m³)_L2', '在库体积(m³)_L1',  '在库体积(m³)_M', '在库体积(m³)_S', '在库体积(m³)_XS', '在库体积(m³)_总计',
    #                      '在库体积(m³)_XL%', '在库体积(m³)_L2%', '在库体积(m³)_L1%', '在库体积(m³)_M%', '在库体积(m³)_S%',  '在库体积(m³)_XS%',
    #                     '在库件数_XL', '在库件数_L2', '在库件数_L1', '在库件数_M', '在库件数_S',  '在库件数_XS', '在库件数_总计',
    #                     '在库件数_XL%', '在库件数_L2%', '在库件数_L1%',  '在库件数_M%', '在库件数_S%', '在库件数_XS%',
    #                     'sku数', '库存深度(m³/sku)', '库存深度(件/sku)', '大件体积占比', '客户类型']

    df_customer = df_customer[org_customer_columns]
    # df_customer.columns = new_customer_columns


    print('*' * 10, '客户分析结果', '*' * 10, '\n')
    print('字段名：')
    print(df_customer.columns)
    print('\n')


    '''
    库龄分析
    '''
    df_age = pd.pivot_table(df_sku, index=['库龄等级'],
                            values=['在库体积(m³)', '在库件数', '产品代码'],
                            aggfunc={'在库体积(m³)': np.sum, '在库件数':np.sum, '产品代码':len},
                            margins=True,
                            margins_name='合计',
                            fill_value=0).reset_index()

    ## 列的重命名 透视表中排序以拼音首字母顺序
    new_columns = ['库龄等级', '在库sku数', '在库件数', '在库体积(m³)']
    df_age.columns = new_columns

    ## 计算库存体积和件数的占比
    for col in new_columns[1:]:
        df_age[col + '%'] = df_age[col] / (df_age[col].sum() / 2)


    df_age['库存深度(m³/sku)'] = df_age['在库体积(m³)'] / df_age['在库sku数']
    df_age['库存深度(件/sku)'] = df_age['在库件数'] / df_age['在库sku数']


    print('*' * 10, '库龄分析结果', '*' * 10, '\n')
    print('字段名：')
    print(df_age.columns)
    print(df_age)
    print('\n')



    '''
    计算结果写入Excel表格
    '''
    ### write to file
    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}库存分析_{}.xlsx'.format(output_path, str_time))

    format_data(writer=writer, df=df_location, sheet_name='A01-库位推荐')

    format_data(writer=writer, df=df_customer, sheet_name='A02-客户货型分布')

    format_data(writer=writer, df=df_age, sheet_name='A03-库龄')


    format_data(writer=writer, df=df, sheet_name='01-数据源')
    format_data(writer=writer, df=df_sku, sheet_name='02-sku维度数据源')

    writer.save()



def format_data(writer, df, sheet_name, isTrans=True):
    '''
    将Dataframe 格式化写入Excel表格
    :param writer: Excel文件
    :param df: 写入的Dataframe
    :param sheet_name: 表格sheet名，需要根据sheet名修改格式
    :return: None
    '''

    workbook = writer.book

    '''设置格式'''
    ## 数据格式
    percent_fmt = workbook.add_format({'num_format': '0.00%'})
    pure_percent_fmt = workbook.add_format({'num_format': '0%'})
    amt_fmt = workbook.add_format({'num_format': '#,##0'})
    dec2_fmt = workbook.add_format({'num_format': '#,##0.00'})
    dec4_fmt = workbook.add_format({'num_format': '#,##0.0000'})
    date_fmt = workbook.add_format({'font_name': 'Microsoft YaHei', 'font_size': 9, 'num_format': 'yyyy/mm/dd'})

    ## 列格式
    fmt = workbook.add_format({'font_name': 'Microsoft YaHei', 'font_size': 9, 'align': 'center', 'valign': 'vcenter'})

    ## 边框格式
    border_format = workbook.add_format({'border': 1})

    ## 表头及字段格式
    head_note_fmt = workbook.add_format(
        {'bold': True, 'font_size': 11, 'font_name': 'Microsoft YaHei', 'bg_color':'2F75B5', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter'})
    # 'bg_color': '#9FC3D1','bold': True,
    note_fmt = workbook.add_format(
        {'bold': True, 'font_size': 9, 'font_name': 'Microsoft YaHei', 'bg_color': '07387D', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter'})
    bold_fmt = workbook.add_format({'bold': True, 'font_size': 9})
    left_fmt = workbook.add_format({'font_size': 9, 'font_name': 'Microsoft YaHei', 'align': 'left', 'valign': 'vcenter'})

    ### 修改编号，从1开始
    df.index = range(1, len(df) + 1)
    df.index.name = '序号'

    ### df写入表格， 从第2行开始写入
    if 'A0' in sheet_name or 'C0' in sheet_name:
        start_row = 2
    else:
        start_row = 0


    df.to_excel(excel_writer=writer, sheet_name=sheet_name, encoding='utf8',
                startrow=start_row, startcol=0, na_rep='-', inf_rep='')
    worksheet1 = writer.sheets[sheet_name]

    ### 数据源行数，和列数 +1表示最后一行 start_row 为前2行说明
    end_line = df.shape[0] + 1 + start_row

    ### 数据源列数, 增加序号列 需+1
    cols = df.shape[1] + 1

    ### excel中列名 A,B,C...
    cap_list = get_char_list(200)

    ### 添加边框
    worksheet1.conditional_format('A1:{}{}'.format(cap_list[cols], end_line),
                                  {'type': 'no_blanks', 'format': border_format})

    # 'type': 'cell','criteria': '>', 'value': 0, 'format': border_format

    ### 设置列宽
    worksheet1.set_column('A:{}'.format(cap_list[cols]), 12, fmt)

    ### 根据表名，设置页面表头
    if 'A01' in sheet_name:

        worksheet1.set_column('B:B', 15, left_fmt)
        ### 第一行为表格说明
        worksheet1.merge_range('A1:Z1', '库位需求测算表', head_note_fmt)
        worksheet1.merge_range('B2:H2', '库位参数', note_fmt)
        worksheet1.merge_range('I2:T2', '现状批次库存', note_fmt)
        worksheet1.merge_range('U2:Z2', '规划参数', note_fmt)

        ### 序号列格式化, 数据从第2行开始写入
        worksheet1.merge_range('A2:A3', '序号', note_fmt)

    elif 'A02' in sheet_name:

        worksheet1.merge_range('A1:AG1', '客户货型分布', head_note_fmt)
        ### 序号列格式化, 数据从第2行开始写入
        worksheet1.merge_range('A2:A3', '序号', note_fmt)
        worksheet1.merge_range('B2:B3', '客户代码', note_fmt)

        worksheet1.merge_range('C2:I2', '在库体积', note_fmt)
        worksheet1.merge_range('J2:O2', '在库体积占比', note_fmt)
        worksheet1.merge_range('P2:V2', '在库件数', note_fmt)
        worksheet1.merge_range('W2:AB2', '在库件数占比', note_fmt)

        worksheet1.merge_range('AC2:AC3', 'sku数', note_fmt)
        worksheet1.merge_range('AD2:AD3', '库存深度\n(m³/sku)', note_fmt)
        worksheet1.merge_range('AE2:AE3', '库存深度\n(件/sku)', note_fmt)
        worksheet1.merge_range('AF2:AF3', '大件体积占比', note_fmt)
        worksheet1.merge_range('AG2:AG3', '客户类型', note_fmt)

    elif 'A03' in sheet_name:

        ### 更新列宽
        worksheet1.set_column('A:{}'.format(cap_list[cols]), 15, fmt)
        worksheet1.set_column('B:B', 15, left_fmt)

        worksheet1.merge_range('A1:J2', '库龄分析', head_note_fmt)
        ### 序号列格式化, 数据从第2行开始写入
        # worksheet1.merge_range('A2:A3', '序号', note_fmt)
        # worksheet1.merge_range('B2:B3', '库龄等级', note_fmt)
        worksheet1.conditional_format('A3:J3', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': note_fmt})

    elif 'C01' in sheet_name:

        worksheet1.merge_range('A2:A3', '序号', note_fmt)
        worksheet1.merge_range('B2:B3', 'Month', note_fmt)
        worksheet1.merge_range('C2:C3', '海柜号或跟踪号', note_fmt)
        worksheet1.merge_range('D2:D3', '货运方式', note_fmt)

        worksheet1.merge_range('E2:K2', '来货体积', note_fmt)
        worksheet1.merge_range('L2:R2', '来货件数', note_fmt)
        worksheet1.merge_range('S2:X2', '来货体积占比', note_fmt)
        worksheet1.merge_range('Y2:AD2', '来货件数占比', note_fmt)

    elif 'C02' in sheet_name:
        worksheet1.merge_range('A2:A3', '序号', note_fmt)
        worksheet1.merge_range('B2:B3', '海柜号或跟踪号', note_fmt)
        worksheet1.merge_range('C2:C3', '货运方式', note_fmt)

        worksheet1.merge_range('D2:G2', '体积', note_fmt)
        worksheet1.merge_range('H2:K2', '箱数', note_fmt)
        worksheet1.merge_range('L2:O2', '件数', note_fmt)
        worksheet1.merge_range('P2:R2', '均箱体积', note_fmt)

        worksheet1.merge_range('S2:S3', '总体积', note_fmt)
        worksheet1.merge_range('T2:T3', '总箱数', note_fmt)
        worksheet1.merge_range('U2:U3', '总均箱体积', note_fmt)

    else:
        worksheet1.write(start_row, 0, '序号', note_fmt)



    ## 序号列格式设置
    for i, index in enumerate(df.index):
        worksheet1.write(i+start_row+1, 0, index, fmt)

    ### 按列名设置列的格式
    for k, col in enumerate(df.columns.values):
        i = k + 1

        # 将dataframe 列名写入sheet， （行，列，列名，格式）
        worksheet1.write(start_row, i, col, note_fmt)

        ### 根据列名，格式化一列的格式
        if '%' in col or '率' in col or '占比' in col:
            # print(col, '百分数')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': percent_fmt})
        elif 'm³' in col or '系数' in col or '体积' in col:
            # print(col, '2位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': dec2_fmt})
        elif 'EN' in col or 'EQ' in col or 'IK' in col or 'IQ' in col or '/' in col:
            # print(col, '2位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': dec2_fmt})
        elif '日期' in col or 'date' in col:
            # print(col, '4位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'no_blanks', 'format': date_fmt})
        elif '库容利用率' in col:
            # print(col, '4位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': pure_percent_fmt})
        elif '等级' in col:
            # print(col, '4位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': left_fmt})
        else:
            # print(sheet_name, col, '2位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_line),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': amt_fmt})


    ### 最后一行即合计行 加粗
    if 'A01' in sheet_name:
        worksheet1.conditional_format('B{}:{}{}'.format(end_line, cap_list[cols], end_line),
                                    {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': bold_fmt})
    ### 客户分布加粗总计行
    elif 'A02' in sheet_name:
        worksheet1.conditional_format('B{}:{}{}'.format(4, cap_list[cols], 4),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': bold_fmt})

    elif 'A03' in sheet_name:
        worksheet1.conditional_format('B{}:{}{}'.format(end_line, cap_list[cols], end_line),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': bold_fmt})

    ### 是否翻译列名
    if isTrans:
        cols_name = trans(df.columns)
        for i, col in enumerate(cols_name):
            # 添加了index列在Excel的第1列，df的columns像右移1行
            worksheet1.write(start_row, i + 1, col, note_fmt)


def get_char_list(n):
    char_list = [chr(i) for i in range(65, 91)]

    for i in range(65, 91):
        for j in range(65, 91):
            char_list.append(chr(i) + chr(j))
            if len(char_list) >= n:
                break
        if len(char_list) >= n:
            break
    # print(char_list)
    return char_list


def trans(columns):
    if len(columns) > 0:
        new_col = []
        for col in columns:
            ### 库存分析修改列名
            col = col.replace('在库体积(m³)_', '')
            col = col.replace('在库件数_', '')


            ### 入库分析字段翻译
            col = col.replace('receive_', '来货')
            col = col.replace('interval_', '间隔')
            col = col.replace('days', '天数')
            col = col.replace('date', '日期')

            col = col.replace('deliveryNO', '海柜号或跟踪号')
            col = col.replace('containerNO', '海柜号')
            col = col.replace('trackingNO', '跟踪号')


            col = col.replace('delivery_mode', '货运方式')

            col = col.replace('Vol(m³)_', '')
            col = col.replace('quantity_', '')
            col = col.replace('cartonNO_', '')
            col = col.replace('均箱体积_', '')

            col = col.replace('cartonNO', '箱数')
            col = col.replace('Vol', '体积')
            col = col.replace('quantity', '件数')

            ### 出库分析字段翻译
            col = col.replace('order_tag', '订单类型')
            col = col.replace('re_order_structure', '订单结构')
            col = col.replace('order_type', '订单组合')
            col = col.replace('customer', '客户代码')
            col = col.replace('combine_', '组合')
            col = col.replace('age_class', '库龄等级')
            col = col.replace('age', '库龄')
            col = col.replace('ob_', '出库')
            col = col.replace('cumu_', '累计')
            col = col.replace('qty', '件数')
            col = col.replace('freq_day', '天数频率')
            col = col.replace('max_', '最大')
            col = col.replace('ob_', '出库')
            col = col.replace('inv_', '在库')
            col = col.replace('orderID', '订单数')
            col = col.replace('order_', '订单')

            col = col.replace('channel', '渠道')
            col = col.replace('platform', '平台')

            new_col.append(col)
    else:
        new_col = columns

    return new_col


