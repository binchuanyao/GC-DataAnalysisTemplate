# -*- coding: utf-8 -*-
# @File   : inventory
# @Time   : 2022/02/14 10:44 
# @Author : BCY


from config import *
from datetime import datetime

# 实例化配置参数, 全局变量
config = Config()
config.run()

pd.set_option('display.max_columns', None)

def load_inventory_data(file_path, inventory_file_name, date=None):
    """
    :param file_path: 文件路径
    :param inventory_file_name: 文件名
    :param date: 批次库存日期
    :return:
    """
    # import inBound and outBound source data
    if ".xlsx" in inventory_file_name:
        data = pd.read_excel('{}{}'.format(file_path, inventory_file_name))
    else:
        try:
            print('*' * 10, 'utf-8', '*' * 10)
            data = pd.read_csv('{}{}'.format(file_path, inventory_file_name), encoding='utf-8')
        except:
            print('*' * 10, 'gbk-8', '*' * 10)
            data = pd.read_csv('{}{}'.format(file_path, inventory_file_name), encoding='gbk')

    cols = data.columns
    if '在库体积(M³)' in cols:
        col = ['Month Key', '批次库存日期', '系统来源', '区域仓名称', '区域仓编码', '物理仓名称', '物理仓名称en', '物理仓编码', '客户代码',
               '上架日期', '产品代码', '货物属性', '一级品类', '二级品类', '三级品类', '产品货型',
               '储位类型', '层', '层级属性', '库位类型代码', '库位数量',
               '产品实际长(Cm)', '产品实际宽(Cm)', '产品实际高(Cm)', '产品实际重量(Kg)', '在库件数', '在库体积(M³)', '在库重量(Kg)']
    else:

        col = ['Month Key', '批次库存日期', '系统来源', '区域仓名称', '区域仓编码', '物理仓名称', '物理仓名称en', '物理仓编码', '客户代码',
               '上架日期', '产品代码', '货物属性', '一级品类', '二级品类', '三级品类', '产品货型',
               '储位类型', '层', '层级属性', '库位类型代码', '库位数量',
               '产品实际长(Cm)', '产品实际宽(Cm)', '产品实际高(Cm)', '产品实际重量(Kg)', '在库件数', '在库体积(M3)', '在库重量(Kg)']



    new_col = ['Month Key', '批次库存日期', '系统来源', '区域仓名称', '区域仓编码', '物理仓名称', '物理仓名称en', '物理仓编码', '客户代码',
           '上架日期', '产品代码', '货物属性', '一级品类', '二级品类', '三级品类', '产品货型',
           '储位类型', '层', '层级属性', '库位类型代码', '库位数量',
           '长(cm)',  '宽(cm)', '高(cm)', '重量(kg)', '在库件数', '在库体积(m³)', '在库重量(kg)']


    # print('\n', data.dtypes)
    df = data[col]
    df.columns = new_col

    print('*'*10, '数据导入', '*'*10, '\n')
    print('字段类型：')
    print(df.dtypes)

    # 计算库龄
    df['批次库存日期'] = pd.to_datetime(df['批次库存日期'])
    df['上架日期'] = pd.to_datetime(df['上架日期'])
    df['库龄'] = pd.to_timedelta(df['批次库存日期'] - df['上架日期']).dt.days

    ## 计算库位维度库龄类别   AGE_CLASS 数据结构为[['D1(0,30]', 0, 30], ['D2(30,60]', 30, 60]] 二维列表，其中的元素为【等级，左区间，右区间】
    df['库龄等级'] = ''
    rank_num = len(config.AGE_CLASS)
    for i in range(rank_num):
        df.loc[(df['库龄'] > config.AGE_CLASS[i][1]) & (df['库龄'] <= config.AGE_CLASS[i][2]), ['库龄等级']] = config.AGE_CLASS[i][0]

    # 返回指定日期的批次库存数据,否则返回所有数据
    if date is None:
        return df
    else:
        return df.where(data['批次库存日期'] == date)



def load_sku_data(file_path, inventory_file_name):
    '''
    从本地路径导入原始数据
    :param inventory_file_name: 完整的路径+文件名
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



def inventory_analysis(df, output_path):


    # 简单库位匹配，一个sku只匹配一种库位类型
    design_location_pt, current_location_pt, df = calculate_single_location(df)


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
    col = []
    for (s1, s2) in df_customer.columns:
        if len(s2) > 0:
            col.append(s1 + '_' + str(s2))
        else:
            col.append(s1)
    # delivery_df.columns = [ s1 + '_' + str(s2) for (s1, s2) in delivery_df.columns]
    df_customer.columns = col

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
    customer_sku.columns = ['客户代码', 'sku数']
    total_sku = sum(customer_sku['sku数'])

    ### 合并库存货型分布及sku数
    df_customer = pd.merge(df_customer, customer_sku, how='left', sort=False)

    ## 修改sku的总计值
    df_customer.loc[(df_customer['客户代码'] == '总计'), ['sku数']] = total_sku

    ### 计算库存深度
    df_customer['库存深度(m³/sku)'] = df_customer['在库体积(m³)_总计'] / df_customer['sku数']
    df_customer['库存深度(件/sku)'] = df_customer['在库件数_总计'] / df_customer['sku数']

    df_customer['大件体积占比'] = df_customer['在库件数_XL%'] + df_customer['在库件数_L2%'] + df_customer['在库件数_L1%']

    df_customer['客户类型'] = np.NAN
    df['储位类型'] = np.NAN
    df_customer.loc[(df_customer['客户类型'].isna()) & (df_customer['大件体积占比'] >= 0.8), ['客户类型']] = '纯大货型'
    df_customer.loc[(df_customer['客户类型'].isna()) & (df_customer['大件体积占比'] >= 0.6), ['客户类型']] = '大货型'
    df_customer.loc[(df_customer['客户类型'].isna()) & (df_customer['大件体积占比'] >= 0.3), ['客户类型']] = '混货型'
    df_customer.loc[(df_customer['客户类型'].isna()), ['客户类型']] = '小货型'

    ### 重排列
    org_customer_columns = ['客户代码', '在库体积(m³)_XL', '在库体积(m³)_L2', '在库体积(m³)_L1', '在库体积(m³)_M', '在库体积(m³)_S', '在库体积(m³)_XS', '在库体积(m³)_总计',
                            '在库体积(m³)_XL%', '在库体积(m³)_L2%', '在库体积(m³)_L1%', '在库体积(m³)_M%', '在库体积(m³)_S%', '在库体积(m³)_XS%',
                            '在库件数_XL', '在库件数_L2', '在库件数_L1', '在库件数_M', '在库件数_S', '在库件数_XS', '在库件数_总计',
                            '在库件数_XL%', '在库件数_L2%', '在库件数_L1%', '在库件数_M%', '在库件数_S%', '在库件数_XS%',
                            'sku数', '库存深度(m³/sku)', '库存深度(件/sku)', '大件体积占比', '客户类型']

    df_customer = df_customer[org_customer_columns]

    '''
    库龄分析
    '''
    df_sku = get_sku_pivot(df)
    sku_col = ['产品代码', '在库件数', '在库体积(m³)', '库龄', '库龄等级']  # 重命名列
    df_sku.columns = sku_col

    df_age = pd.pivot_table(df_sku, index=['库龄等级'],
                            values=['在库体积(m³)', '在库件数', '产品代码'],
                            aggfunc={'在库体积(m³)': np.sum, '在库件数': np.sum, '产品代码': len},
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

    wh = df.at[1, '物理仓名称']
    date = df.at[1, '批次库存日期']
    rows = df.shape[0]
    cols = df.shape[1]
    data_info = '''数据源\n 物理仓： {},  批次库存日期：{},  数据量：行数 {}, 列数{}'''.format(wh, date, rows, cols)
    # print('inventory data info: ', data_info)

    format_data(writer=writer, df=design_location_pt, sheet_name='A1.1-库位推荐', source_data_info=data_info)

    format_data(writer=writer, df=current_location_pt, sheet_name='A1.2-现状库位', source_data_info=data_info)

    format_data(writer=writer, df=df_customer, sheet_name='A2-客户货型分布', source_data_info=data_info)

    format_data(writer=writer, df=df_age, sheet_name='A3-库龄', source_data_info=data_info)

    format_data(writer=writer, df=df, sheet_name='01-数据源')
    format_data(writer=writer, df=df_sku, sheet_name='02-sku维度数据源')

    writer.save()



def calculate_multi_location(df, output_path):
    # 实例化配置参数
    config = Config()
    config.run()

    # print('data column: ', df.columns)



def calculate_single_location(df):
    """
    :param df: 透视表原始数据
    :return:
    """

    '''库存数据基础字段计算'''

    df['在库托数'] = df['在库体积(m³)'] / config.PALLET['valid_vol']

    df['是否超长'] = 'N'
    df.loc[(df['长(cm)'] >= config.SUPER_LONG_PARAM), ['是否超长']] = 'Y'

    df['是否批量'] = 'N'
    df.loc[(df['在库托数'] >= config.BATCH_PARAM), ['是否批量']] = 'Y'

    df['储位类型'] = np.NAN
    df.loc[(df['储位类型'].isna()) & (df['是否批量'] == 'Y'), ['储位类型']] = '批量平铺区'
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
        df.loc[(df['储位类型'] == '卡板区') &
               (df['在库托数'] > config.PALLET_CLASS[i][1]) &
               (df['在库托数'] <= config.PALLET_CLASS[i][2]),
               ['储区类型']] = config.PALLET_CLASS[i][0]

    # 按标准库位类型匹配的设计库位 , A1.1
    design_location_pt = design_location(df)


    '''新增现有批次库存货位类型分布'''
    current_index = ['批次库存日期', '库位类型代码']
    current_location_pt = current_location(df, index=current_index)


    return design_location_pt, current_location_pt, df



def design_location(df, index=None, pt_col=None):
    if index is None:
        index = ['批次库存日期', '储位类型']

    if pt_col is None:
        pt_col = ['产品代码', '在库件数', '在库体积(m³)', '在库重量(kg)']

        # datetime64[ns]不能作为key,将日期列的格式转换为string
    df['批次库存日期'] = df['批次库存日期'].astype(str)
    df['上架日期'] = df['上架日期'].astype(str)
    df['Month Key'] = df['Month Key'].astype(str)

    df_location = pd.pivot_table(df, index=index,
                               values=pt_col,
                               aggfunc={'产品代码': pd.Series.nunique, '在库件数': np.sum, '在库体积(m³)': np.sum, '在库重量(kg)': np.sum},
                               fill_value=0).reset_index()

    # 重排列
    re_pt_col = ['在库体积(m³)', '在库件数', '产品代码', '在库重量(kg)']
    df_location = df_location[index + re_pt_col]

    # 重命名列
    df_location.columns = index + ['在库体积(m³)', '在库件数', 'sku数', '在库重量(kg)']

    # 透视字段， 需计算总和及百分比的字段
    sum_col = ['在库体积(m³)', '在库件数', 'sku数', '在库重量(kg)']

    # 计算库存深度
    df_location['库存深度(m³/sku)'] = df_location['在库体积(m³)'] / df_location['sku数']
    df_location['库存深度(件/sku)'] = df_location['在库件数'] / df_location['sku数']


    '''
    合并库位类型与透视结果
    '''
    print('库位类型： \n')
    print(config.LOCATION_DF)
    print('\n')

    df_location = pd.merge(config.LOCATION_DF, df_location, on='储位类型', how='right', sort=False).fillna(0)
    print(df_location)

    # 设计参数
    df_location['单sku需求库位数'] = df_location['库存深度(m³/sku)'] / df_location['有效库容(m³)']
    df_location['库位需求1-库容最大化'] = np.ceil(df_location['在库体积(m³)'] / df_location['有效库容(m³)'])
    df_location['库位需求2-sku数最大化'] = np.ceil(df_location['sku数'] * df_location['单sku需求库位数'] / df_location['sku限制'])
    df_location['库位需求-现有库存'] = df_location[['库位需求1-库容最大化', '库位需求2-sku数最大化']].max(axis=1)
    df_location['库容饱和系数'] = 0.7
    df_location['规划库位需求数量'] = df_location['库位需求-现有库存'] / df_location['库容饱和系数']
    df_location['面积需求'] = df_location['在库体积(m³)'] / df_location['库容坪效系数']

    row_n = df_location.shape[0]
    # 更新合计值
    df_location.at[row_n, index[-1:]] = '合计'
    df_location.at[row_n, sum_col] = df_location[sum_col].apply(lambda x: x.sum())

    # 计算比例
    for i in range(len(sum_col)):
        df_location[sum_col[i] + '%'] = df_location[sum_col[i]] / (df_location[sum_col[i]].sum() / 2)

    df_location['库存深度(m³/sku)'] = df_location['在库体积(m³)'] / df_location['sku数']
    df_location['库存深度(件/sku)'] = df_location['在库件数'] / df_location['sku数']

    sum_design_col = ['库位需求1-库容最大化', '库位需求2-sku数最大化', '库位需求-现有库存', '规划库位需求数量', '面积需求']
    df_location.at[row_n, sum_design_col] = df_location[sum_design_col].apply(lambda x: x.sum())

    # row_n = df_location.shape[0]
    # sum_design_col = ['库位需求1-库容最大化', '库位需求2-sku数最大化', '库位需求-现有库存', '规划库位需求数量', '面积需求']
    # df_location.loc[(df_location['储位类型'] == '合计'), sum_design_col] = 0   # 把合计行置0
    # df_location.loc[(df_location['储位类型'] == '合计'), sum_design_col] = df_location[sum_design_col].apply(lambda x: x.sum())


    print(df_location[sum_design_col].apply(lambda x: x.sum()))

    '''
    库位需求结果 列重排
    '''

    re_columns = ['储位类型', '长(cm)', '宽(cm)', '高(cm)', '库容利用率', '有效库容(m³)', 'sku限制', '库容坪效系数',
                  '批次库存日期', '在库体积(m³)', '在库件数', 'sku数', '在库重量(kg)', '在库体积(m³)%', '在库件数%', 'sku数%', '在库重量(kg)%',
                  '库存深度(m³/sku)', '库存深度(件/sku)', '单sku需求库位数',
                  '库位需求1-库容最大化', '库位需求2-sku数最大化', '库位需求-现有库存', '库容饱和系数', '规划库位需求数量', '面积需求']

    df_location = df_location[re_columns]
    print(df_location)

    return df_location


def current_location(df, index=None, pt_col=None):
    if index is None:
        index = ['批次库存日期', '库位类型代码']

    if pt_col is None:
        pt_col = ['产品代码',  '库位数量', '在库件数', '在库体积(m³)']

        # datetime64[ns]不能作为key,将日期列的格式转换为string
    df['批次库存日期'] = df['批次库存日期'].astype(str)
    df['上架日期'] = df['上架日期'].astype(str)
    df['Month Key'] = df['Month Key'].astype(str)

    df_location = pd.pivot_table(df, index=index,
                               values=pt_col,
                               aggfunc={'产品代码': pd.Series.nunique, '库位数量': np.sum, '在库件数': np.sum, '在库体积(m³)': np.sum},
                               fill_value=0).reset_index()

    # 重排列
    re_pt_col = ['在库体积(m³)', '在库件数', '产品代码', '库位数量']
    df_location = df_location[index + re_pt_col]

    # 重命名列
    df_location.columns = index + ['在库体积(m³)', '在库件数', 'sku数', '库位数量']

    # 透视字段， 需计算总和及百分比的字段
    sum_col = ['在库体积(m³)', '在库件数', 'sku数', '库位数量']


    row_n = df_location.shape[0]
    df_location.at[row_n, index[-1:]] = '合计'
    df_location.at[row_n, sum_col] = df_location[sum_col].apply(lambda x: x.sum())

    # 计算比例
    for i in range(len(sum_col)):
        df_location[sum_col[i] + '%'] = df_location[sum_col[i]] / (df_location[sum_col[i]].sum() / 2)


    # 计算库存深度
    df_location['库存深度(m³/sku)'] = df_location['在库体积(m³)'] / df_location['sku数']
    df_location['库存深度(件/sku)'] = df_location['在库件数'] / df_location['sku数']

    return df_location


def format_data(writer, df, sheet_name, source_data_info=None, isTrans=True):
    '''
    将Dataframe 格式化写入Excel表格
    :param writer: Excel文件
    :param df: 写入的Dataframe
    :param sheet_name: 表格sheet名，需要根据sheet名修改格式
    :param source_data_info: 原始数据信息
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
    ## 表头逻辑说明格式
    remark_fmt = workbook.add_format(
        {'bold': False, 'font_size': 9, 'font_name': 'Microsoft YaHei',  'bg_color': '#BFBFBF', 'align': 'left', 'valign': 'vcenter'})
    # 'bg_color': '#BFBFBF','bold': True,
    note_fmt = workbook.add_format(
        {'bold': True, 'font_size': 9, 'font_name': 'Microsoft YaHei', 'bg_color': '07387D', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter'})
    bold_fmt = workbook.add_format({'bold': True, 'font_size': 9})
    left_fmt = workbook.add_format({'font_size': 9, 'font_name': 'Microsoft YaHei', 'align': 'left', 'valign': 'vcenter'})

    ### 修改编号，从1开始
    df.index = range(1, len(df) + 1)
    df.index.name = '序号'


    ### df写入表格， 从第3行开始写入, 第1行为逻辑说明；第2行为数据来源
    start_row = 3

    df.to_excel(excel_writer=writer, sheet_name=sheet_name, encoding='utf8',
                startrow=start_row, startcol=0, na_rep='-', inf_rep='-')
    worksheet1 = writer.sheets[sheet_name]

    ### 数据源行数，和列数 +1表示最后一行 start_row 为前2行说明
    end_row = df.shape[0] + 1 + start_row
    cols = df.shape[1]
    ### excel中列名 A,B,C...
    cap_list = get_char_list(200)
    end_col = cap_list[cols]

    ### 添加边框
    worksheet1.conditional_format('A{}:{}{}'.format(start_row+1, end_col, end_row),
                                  {'type': 'cell','criteria': '>=', 'value': 0, 'format': border_format})

    # 'type': 'cell','criteria': '>', 'value': 0, 'format': border_format

    ### 设置列宽
    worksheet1.set_column('A:{}'.format(end_col), 12, fmt)
    # worksheet1.set_row(0, 100)  # 设置测试逻辑行高
    # worksheet1.set_row(1, 50)   # 设置数据来源行高


    ### 序号列格式设置
    worksheet1.write(start_row, 0, '序号', note_fmt)
    for i, index in enumerate(df.index):
        worksheet1.write(i+start_row+1, 0, index, fmt)


    ### 根据表名，设置页面表头及说明
    if 'A1.1' in sheet_name:
        # 规划库位推荐
        worksheet1.set_column('B:B', 15, left_fmt)
        worksheet1.set_row(0, 100)
        worksheet1.set_row(1, 50)
        ### 第一行为表格说明
        remark = '''测算逻辑 \n 1. 一个sku只匹配一种库位类型；\n 2. 按库容及sku数计算需求库位，取两者较大值；\n 3. 根据库容饱和系数计算规划库位需求；\n 4. 根据不同库位类型的库容坪效系数估算面积需求。'''

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        worksheet1.merge_range('B{}:I{}'.format(start_row, start_row), '库位参数', note_fmt)
        worksheet1.merge_range('J{}:U{}'.format(start_row, start_row), '现状批次库存', note_fmt)
        worksheet1.merge_range('V{}:AA{}'.format(start_row, start_row), '规划参数', note_fmt)

        ### 序号列格式化, 数据从第3行开始写入
        worksheet1.merge_range('A{}:A{}'.format(start_row, start_row+1), '序号', note_fmt)

        ### 有合并行的地方，添加边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, end_row),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'A1.2' in sheet_name:
        # 现状库位统计
        worksheet1.set_row(0, 100)
        worksheet1.set_row(1, 50)
        ### 第一行为表格说明
        remark = '''测算逻辑 \n 1. 当前批次库存的库位分布；\n 2. 计算不同库位类型的体积、件数、sku数、库位数量及其占比。'''
        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})


    elif 'A2' in sheet_name:
        # 客户维度体积及件数分布
        remark = '''测算逻辑 \n 1. 客户维度，产品货型的体积和件数分布,并计算客户维度的库存深度；\n 2. 根据产品货型的比例对客户定性：
        \t ①大件体积>=80%, 纯大货型；②大件体积>=60%, 大货型；③ 大件体积>=30%, 混货型；④其他， 小货型'''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)   # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 序号列格式化, 数据从第3行开始写入
        worksheet1.merge_range('A{}:A{}'.format(start_row, start_row+1), '序号', note_fmt)
        worksheet1.merge_range('B{}:B{}'.format(start_row, start_row+1), '客户代码', note_fmt)

        worksheet1.merge_range('C{}:I{}'.format(start_row, start_row), '在库体积', note_fmt)
        worksheet1.merge_range('J{}:O{}'.format(start_row, start_row), '在库体积占比', note_fmt)
        worksheet1.merge_range('P{}:V{}'.format(start_row, start_row), '在库件数', note_fmt)
        worksheet1.merge_range('W{}:AB{}'.format(start_row, start_row), '在库件数占比', note_fmt)

        worksheet1.merge_range('AC{}:AC{}'.format(start_row, start_row+1), 'sku数', note_fmt)
        worksheet1.merge_range('AD{}:AD{}'.format(start_row, start_row+1), '库存深度\n(m³/sku)', note_fmt)
        worksheet1.merge_range('AE{}:AE{}'.format(start_row, start_row+1), '库存深度\n(件/sku)', note_fmt)
        worksheet1.merge_range('AF{}:AF{}'.format(start_row, start_row+1), '大件体积占比', note_fmt)
        worksheet1.merge_range('AG{}:AG{}'.format(start_row, start_row+1), '客户类型', note_fmt)

        ### 有合并行的地方，添加边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, end_row),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'A3' in sheet_name:
        # sku库龄等级的分布
        remark = '''测算逻辑 \n 1. sku库龄等级的分布；\n 2. sku库龄取不同库位库龄的加权平均值，权重为件数比例'''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)   # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 更新列宽
        worksheet1.set_column('A:{}'.format(end_col), 15, fmt)
        worksheet1.set_column('B:B', 15, left_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'C1' in sheet_name:
        # 海柜及快递来货体积及件数分布
        remark = '''测算逻辑 \n 1. 日维度不同货运方式到货件型分布'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 100)   # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        worksheet1.merge_range('A{}:A{}'.format(start_row, start_row+1), '序号', note_fmt)
        worksheet1.merge_range('B{}:B{}'.format(start_row, start_row+1), 'Month', note_fmt)
        worksheet1.merge_range('C{}:C{}'.format(start_row, start_row+1), '日期', note_fmt)
        worksheet1.merge_range('D{}:D{}'.format(start_row, start_row+1), '海柜号或跟踪号', note_fmt)
        worksheet1.merge_range('E{}:E{}'.format(start_row, start_row + 1), '货运方式', note_fmt)

        worksheet1.merge_range('F{}:L{}'.format(start_row, start_row), '来货体积', note_fmt)
        worksheet1.merge_range('M{}:S{}'.format(start_row, start_row), '来货件数', note_fmt)
        worksheet1.merge_range('T{}:Y{}'.format(start_row, start_row), '来货体积占比', note_fmt)
        worksheet1.merge_range('Z{}:AE{}'.format(start_row, start_row), '来货件数占比', note_fmt)

        ### 有合并行的地方，添加边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, end_row),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'C2' in sheet_name:
        # 海柜及快递来货体积及件数分布
        remark = '''测算逻辑 \n 1. 日维度不同货运方式到货箱型类别分布; \n 2. 箱型划分：
        \t ①单箱单件：箱内sku数=1，件数=1；\t ②单箱单件：箱内sku数=1，件数>1；\t ③单箱多品：箱内sku数>1，件数>1；\t ④异常：件数=0'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 100)   # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        worksheet1.merge_range('A{}:A{}'.format(start_row, start_row+1), '序号', note_fmt)
        worksheet1.merge_range('B{}:B{}'.format(start_row, start_row + 1), 'Month', note_fmt)
        worksheet1.merge_range('C{}:C{}'.format(start_row, start_row + 1), 'weekday', note_fmt)
        worksheet1.merge_range('D{}:D{}'.format(start_row, start_row + 1), 'date', note_fmt)
        worksheet1.merge_range('E{}:E{}'.format(start_row, start_row+1), '海柜号或跟踪号', note_fmt)
        worksheet1.merge_range('F{}:F{}'.format(start_row, start_row+1), '货运方式', note_fmt)

        worksheet1.merge_range('G{}:J{}'.format(start_row, start_row), '体积', note_fmt)
        worksheet1.merge_range('K{}:N{}'.format(start_row, start_row), '箱数', note_fmt)
        worksheet1.merge_range('O{}:R{}'.format(start_row, start_row), '件数', note_fmt)
        worksheet1.merge_range('S{}:U{}'.format(start_row, start_row), '均箱体积', note_fmt)

        worksheet1.merge_range('V{}:V{}'.format(start_row, start_row+1), '总体积', note_fmt)
        worksheet1.merge_range('W{}:W{}'.format(start_row, start_row+1), '总箱数', note_fmt)
        worksheet1.merge_range('X{}:X{}'.format(start_row, start_row+1), '总均箱体积', note_fmt)

        ### 有合并行的地方，添加边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, end_row),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'C3' in sheet_name:
        # 海柜及快递来货体积及件数分布
        remark = '''测算逻辑 \n 1. 日维度不同货运方式到货箱内SKU数分布；\n 2. 箱内含1sku~9sku的箱数单独统计作为列，大于10sku的箱合并统计，只展示数据中存在的列。'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 100)   # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})


    elif 'C4' in sheet_name:
        # 海柜及快递来货体积及件数分布
        remark = '''测算逻辑 \n 1. 日维度海柜及快递方式到货数量，以及来货频次'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 100)   # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    # 出库表格说明
    elif 'B1.1' in sheet_name:
        remark = '''测算逻辑 \n 1. 日维度的标准订单EIQ'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B1.2' in sheet_name:
        remark = '''测算逻辑 \n 1. 日维度的FBA订单EIQ'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B1.3' in sheet_name:
        # 订单结构EIQ
        remark = '''测算逻辑 \n 1. 日维度的订单结构EIQ; \n 2. 不同订单结构订单数,sku数,行数及件数占比'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B1.4' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 根据截单时间点划分为2个波次，开始作业时间（如7点）到截单时间前为第二波，其他为第一波; \n 2. 不同波次不同订单结构中订单数,sku数,行数及件数分布'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B1.5' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 统计历史数据中每日拣货单数量，汇总拣货单中库位数及sku数; \n 2. 历史数据中订单维度的EIQ及拣货维度EIQ'''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'B1.6' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 统计多品多件订单货型组合分布; \n 2. 将sku根据货型尺寸定性分为4类,即小-中-大-XL, 划分依据为：①小：XS, S; ②中：M; ③大：L1, L2; ④XL
        \n 3. 订单的货型组合定义：①小: 订单中sku货型全部为小; ②中: 订单中sku货型全部为中; ③大: 订单中sku货型全部为大; 
        \n ④中配小: 订单中同时存在中、小货型，且不含大货型; ⑤大配小：订单中同时存在大、小货型，且不含中货型; ⑥大配中：订单中同时存在大、中货型，且不含小货型
        \n ⑦大中小: 订单中同时存在sku为大、中、小货型; ⑧XL: 只要订单含有XL货型sku '''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B2' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 客户维度库存、出库特性; \n 2. 若出库总天数≤30,则月动销sku选取所有数据计算，否则选取数据中天数最长的自然月份; \n 3. 由于库存数据选取的静态日期，月动销sku数有可能大于库存sku数
       '''

        worksheet1.set_row(0, 50)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 序号列格式化, 数据从第3行开始写入
        worksheet1.merge_range('A{}:A{}'.format(start_row, start_row + 1), '序号', note_fmt)
        worksheet1.merge_range('B{}:B{}'.format(start_row, start_row + 1), '客户代码', note_fmt)

        worksheet1.merge_range('B{}:G{}'.format(start_row, start_row), '库存结构', note_fmt)
        worksheet1.merge_range('H{}:N{}'.format(start_row, start_row), '出库结构', note_fmt)
        worksheet1.merge_range('O{}:S{}'.format(start_row, start_row), '出库特征', note_fmt)

        ### 有合并行的地方，添加边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, end_row),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B3' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 周维度sku动销率; \n 2. 关键字段计算逻辑：① 重合sku=current和next的交集; \t ② 流入sku=next-current的差集 \t ③ 流出sku=current-next的差集 \t 
        ④ current重合sku件数：重合sku在current中的件数; \t ⑤ next重合sku件数：重合sku在next中的件数; ⑥ sku池变化率=流入sku/current
       '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'B4' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 操作日期维度24小时订单流入统计; \n 2. 统计每个时点流入的订单数、行数、sku数、件数; \n 3. 统计截止到当前时刻的累计订单数、行数、sku数、件数及其比例
       '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}2'.format(end_col),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'B5.1' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. sku多重ABC分类的库存、出库分布
       '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B5.2' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. sku多重ABC分类结果明细; \n 2. skuABC分类逻辑：\n ①出库件数ABC：A、B、C类累计出库件数分别为70%，20%，10%; \n ②出库频次ABC：出库频率=出库天数/总出库天数 A≥50%, C≤20%，B其他
        ③动碰最大间隔天数ABC： A≤3, C≥10, B其他 \n 3. 组合ABC逻辑: ① A: A的数量≥1,且c的数量=0 ② C: A的数量=0,且c的数量≥2 ③ B: 其他
          '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B6.1' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. sku出库库龄等级分布,以订单行的最小维度统计; \n 2. sku出库库龄为出库明细行中出库日期与上架日期的间隔天数
          '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    elif 'B6.2' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 订单出库库龄等级分布,以订单的最小维度统计; \n 2. 订单出库库龄记为订单内sku的最长库龄
          '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B7.1' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 出库渠道维度的订单分布
          '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})
    elif 'B7.2' in sheet_name:
        # 波次EIQ
        remark = '''测算逻辑 \n 1. 订单下单平台维度的订单分布
          '''

        worksheet1.set_row(0, 100)  # 设置测试逻辑行高
        worksheet1.set_row(1, 50)  # 设置数据来源行高

        worksheet1.merge_range('A1:{}1'.format(end_col), remark, remark_fmt)
        worksheet1.merge_range('A2:{}2'.format(end_col), source_data_info, remark_fmt)

        ### 没有有合并行的地方，添加说明行边框
        worksheet1.conditional_format('A1:{}{}'.format(end_col, 2),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': border_format})

    else:
        worksheet1.write(start_row, 0, '序号', note_fmt)




    ### 按列名设置列的格式
    for k, col in enumerate(df.columns.values):
        i = k + 1
        # 将dataframe 列名写入sheet， （行，列，列名，格式）
        worksheet1.write(start_row, i, col, note_fmt)

        ### 根据列名，格式化一列的格式
        if '%' in col or 'freq' in col or '率' in col or '占比' in col:
            # print(col, '百分数')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': percent_fmt})
        elif 'm³' in col or '系数' in col or '体积' in col:
            # print(col, '2位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': dec2_fmt})
        elif 'EN' in col or 'EQ' in col or 'IK' in col or 'IQ' in col or '/' in col:
            # print(col, '2位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': dec2_fmt})
        elif '日期' in col or 'date' in col:
            # print(col, '4位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': date_fmt})
        elif '库容利用率' in col:
            # print(col, '4位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': pure_percent_fmt})
        elif '等级' in col:
            # print(col, '4位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': left_fmt})
        else:
            # print(sheet_name, col, '2位小数，千分位')
            worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], end_row),
                                          {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': amt_fmt})


    ### 最后一行即合计行 加粗
    if 'A1' in sheet_name:
        worksheet1.conditional_format('B{}:{}{}'.format(end_row, end_col, end_row),
                                    {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': bold_fmt})
    ### 客户分布加粗总计行
    elif 'A2' in sheet_name:
        worksheet1.conditional_format('B{}:{}{}'.format(4, end_col, 4),
                                      {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': bold_fmt})

    elif 'A3' in sheet_name:
        worksheet1.conditional_format('B{}:{}{}'.format(end_row, end_col, end_row),
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
            # col = col.replace('qty', '件数')
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


