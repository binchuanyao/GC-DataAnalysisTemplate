# -*- coding: utf-8 -*-
# @File   : outbound
# @Time   : 2022/02/15 13:58 
# @Author : BCY


from inventory import *


def input_column_index():
    print('请按以下字段顺序输入对应的列号：（列号从0开始，以空格隔开enter结束）')
    print('\n')
    print('日期 订单号 SKU代码 件数 订单类型标识(是否FBA)')

    column_index = [int(x) for x in input().split()]


def load_outbound_data(file_path, order_file_name, time_file_name, sku_df=None):
    '''
    从本地路径导入原始数据
    :param inventory_fileName: 完整的路径+文件名
    :return: 原始数据的dataframe形式
    '''
    # import inBound and outBound order detail source data
    if '.xlsx' in order_file_name:
        data = pd.read_excel('{}{}'.format(file_path, order_file_name))
    else:
        try:
            # print('='*10, 'utf-8', '='*10)
            data = pd.read_csv('{}{}'.format(file_path, order_file_name), encoding='utf-8')
        except:
            # print('=' * 10, 'gbk', '=' * 10)
            data = pd.read_csv('{}{}'.format(file_path, order_file_name), encoding='gbk')

    ### 交互界面，输入EIQ分析的有效字段编号
    print('\n')
    print('请按以下字段顺序输入 订单明细 对应的列号：（列号从0开始，以空格隔开enter结束）')
    print('日期 订单号 产品代码 产品货型 件数 订单类型标识(是否FBA) 上架时间')

    # column_index = [int(x) for x in input().split()]
    detail_index = [0, 5, 9, 10, 12, 4, 2]
    column_name = data.columns.tolist()

    # print('column_index: ', detail_index)

    detail_columns = []
    for i in detail_index:
        detail_columns.append(column_name[i])

    # print('detail_columns: ', detail_columns)

    detail_data = data[detail_columns]
    valid_columns_name = ['date', 'orderID', 'sku', 'sku_size', 'quantity', 'order_tag', 'putaway_date']
    detail_data.columns = valid_columns_name

    date_col = []
    for x in valid_columns_name:
        if 'date' in x:
            date_col.append(x)
            ### 填充上架日期的缺失值
            detail_data[x] = detail_data[x].fillna(datetime.now().strftime('%Y年%m月%d日'))
            detail_data.loc[(detail_data[x] == '*'), [x]] = datetime.now().strftime('%Y年%m月%d日')

    for col in date_col:
        try:
            detail_data[col] = pd.to_datetime(detail_data[col], format='%Y/%m/%d')
        except ValueError:
            detail_data[col] = pd.to_datetime(detail_data[col], format='%Y年%m月%d日')
        else:
            pass

    ## 新增 客户代码列
    detail_data['customer'] = detail_data['orderID'].map(lambda x: x[0: x.index('-')])

    print(detail_data.dtypes)
    print(detail_data.head(10))

    print('\n')
    print('*' * 10, '原始数据', '*' * 10)
    print('行数： ', detail_data.shape[0], '\t列数： ', detail_data.shape[1])

    ''' 数据清洗 '''
    '''
    如果sku基础信息为空，删除货型尺寸不明的SKU对应的订单
    如果sku基础信息不为空，匹配sku基础信息后，再删除货型尺寸不明的SKU对应的订单
    '''

    if sku_df is None:
        detail_data['sku_size'] = detail_data['sku_size'].fillna('Null')
        order_df = detail_data.loc[(detail_data['sku_size'] == 'Null') | (detail_data['sku_size'] == '*')]
        orders = order_df['orderID'].unique()
        detail_data = detail_data[~detail_data['orderID'].isin(orders)]

    else:
        ### 合并订单及库存数据中产品货型
        temp = pd.merge(detail_data, sku_df, on='sku', how='left')

        if 'sku_size_x' in temp.columns:
            temp['sku_size'] = temp['sku_size_x']
            temp.loc[(temp['sku_size_x'] == 'Null') | (temp['sku_size_x'] == '*'), ['sku_size']] = temp['sku_size_y']

        temp['sku_size'] = temp['sku_size'].fillna('Null')
        order_df = temp.loc[(temp['sku_size'] == 'Null') | (temp['sku_size'] == '*')]
        orders = order_df['orderID'].unique()

        detail_data = temp[valid_columns_name]
        detail_data = detail_data[~detail_data['orderID'].isin(orders)]

    print('\n')
    print('*' * 10, '数据清洗后', '*' * 10)
    print('行数： ', detail_data.shape[0], '\t列数： ', detail_data.shape[1])

    ''' import outBound order synchronize time source data '''

    if '.xlsx' in time_file_name:
        time_df = pd.read_excel('{}{}'.format(file_path, time_file_name))
    else:
        try:
            time_df = pd.read_csv('{}{}'.format(file_path, time_file_name), encoding='utf-8')
        except:
            time_df = pd.read_csv('{}{}'.format(file_path, time_file_name), encoding='gbk')

    ### 交互界面，输入EIQ分析的有效字段编号
    print('\n')
    print('请按以下字段顺序输入 订单时间 的列号：（列号从0开始，以空格隔开enter结束）')
    print('流入时间 订单号 订单结构 平台 服务渠道')

    # time_index = [int(x) for x in input().split()]
    time_index = [2, 9, 10, 3, 4]
    time_column_name = time_df.columns.tolist()

    # print('time_index: ', time_index)

    time_columns = []
    for i in time_index:
        time_columns.append(time_column_name[i])

    # print('time_columns: ', time_columns)

    time_data = time_df[time_columns]
    time_data_columns_name = ['time_in', 'orderID', 'order_structure', 'platform', 'channel']
    time_data.columns = time_data_columns_name
    time_data['time_in'] = pd.to_datetime(time_data['time_in'])

    re = pd.merge(detail_data, time_data, on='orderID', how='left')

    ### 增加出库库龄
    re['sku_age'] = pd.to_timedelta(re['date'] - re['putaway_date']).dt.days
    re.loc[(re['sku_age'] < 0), ['sku_age']] = 30  ### 库龄异常的行，赋值为30天

    print('\n', '*' * 10, '出库数据有效列名', '*' * 10)
    print('result columns: ', re.columns)
    print('\n', '*' * 10, '出库数据预览', '*' * 10)
    print(re.dtypes)
    print(re.head(10))

    return re


def outbound_analyse(df, output_path, inv_customer_df, inv_sku_df):
    ## GC数据 更新订单类型
    df.loc[(df['order_tag'] == '是'), ['order_tag']] = 'FBA订单'
    df.loc[(df['order_tag'] == '否'), ['order_tag']] = '普通订单'

    ##
    print('*' * 30)
    # print(df.head(10))

    df_order = pd.pivot_table(df, index=['orderID'], values=['sku', 'quantity'], aggfunc={'sku': len, 'quantity': np.sum}).reset_index()
    ## 根据订单的行数和件数更新订单结构
    df_order['re_order_structure'] = np.NAN
    df_order.loc[(df_order['sku'] == 1) & (df_order['quantity'] == 1), ['re_order_structure']] = '单品单件'
    df_order.loc[(df_order['sku'] == 1) & (df_order['quantity'] > 1), ['re_order_structure']] = '单品多件'
    df_order.loc[(df_order['sku'] >= 10) | (df_order['quantity'] >= 20), ['re_order_structure']] = '批量订单'
    df_order.loc[(df_order['sku'] > 1), ['re_order_structure']] = '多品多件'

    ### 增加新定义的订单类型
    df = pd.merge(df, df_order[['orderID', 're_order_structure']], on=['orderID'], how='left')

    ''' 计算订单的货型组合 '''
    temp_df_order_size = df[['orderID', 'sku_size']]

    dict = {'XS': '小', 'S': '小', 'M': '中', 'L1': '大', 'L2': '大', 'XL': 'XL'}

    temp_df_order_size['size_type'] = temp_df_order_size['sku_size'].map(dict)

    df_order_size = temp_df_order_size[['orderID', 'size_type']].groupby('orderID')['size_type'].agg('-'.join).reset_index()

    # df_order_size = df[['orderID', 'sku_size']].groupby('orderID')['sku_size'].agg(lambda x: set(x)).reset_index()

    ### 增加订单货型字段
    df_order_size['order_type'] = df_order_size['size_type']

    ###组合类型
    df_order_size.loc[(df_order_size['size_type'].str.contains('大')) & (df_order_size['size_type'].str.contains('小')), 'order_type'] = '大配小'
    df_order_size.loc[(df_order_size['size_type'].str.contains('大')) & (df_order_size['size_type'].str.contains('中')), 'order_type'] = '大配中'
    df_order_size.loc[(df_order_size['size_type'].str.contains('中')) & (df_order_size['size_type'].str.contains('小')), 'order_type'] = '中配小'
    df_order_size.loc[(df_order_size['size_type'].str.contains('大')) & (df_order_size['size_type'].str.contains('中'))
                      & (df_order_size['size_type'].str.contains('小')), 'order_type'] = '大中小'

    ### 单类型
    df_order_size.loc[
        (df_order_size['size_type'].str.contains('大')) & ~(df_order_size['size_type'].str.contains('中')) & ~(df_order_size['size_type'].str.contains('小')), 'order_type'] = '大'
    df_order_size.loc[
        (df_order_size['size_type'].str.contains('中')) & ~(df_order_size['size_type'].str.contains('大')) & ~(df_order_size['size_type'].str.contains('小')), 'order_type'] = '中'
    df_order_size.loc[
        (df_order_size['size_type'].str.contains('小')) & ~(df_order_size['size_type'].str.contains('中')) & ~(df_order_size['size_type'].str.contains('大')), 'order_type'] = '小'

    df_order_size.loc[(df_order_size['size_type'].str.contains('XL')), 'order_type'] = 'XL订单'
    # print(df_order_size.head(10))

    '''合并 订单明细数据 和 订单货型数据'''
    df = pd.merge(df, df_order_size, on=['orderID'], how='left')

    df['month'] = df.date.dt.month
    df['week'] = df.date.dt.week
    df['hour'] = df.time_in.dt.hour

    df['wave'] = 'Wave1'
    df.loc[(df['hour'] >= 7) & (df['hour'] <= 12), ['wave']] = 'Wave2'

    '''
    订单EIQ分析，输入参数
    '''
    normal_order = '普通订单'
    fba_order = 'FBA订单'
    wave_date = '2022-01-01'

    '''
    B1 订单结构
    '''

    print('*' * 10, '出库分析数据源预览', '*' * 10)
    print(df.dtypes)
    print(df.head(10))

    ### 周维度  FBA与普通订单分开
    week_index = ['week']
    df_normal = df.query('order_tag == "{}"'.format(normal_order))
    normal_order_week_EIQ = get_EIQ(df=df_normal, index=week_index)

    df_fba = df.query('order_tag == "{}"'.format(fba_order))
    fba_order_week_EIQ = get_EIQ(df=df_fba, index=week_index)

    ### 订单结构EIQ
    order_index = ['order_tag', 're_order_structure']
    order_type_EIQ = get_EIQ(df=df_normal, index=order_index)

    # print('\n')
    # print('*'*10, '订单结构维度的EIQ', '*'*10)
    # print(order_type_EIQ)

    ### 波次EIQ
    wave_index = ['date', 'wave', 're_order_structure']
    df_wave = df.query('date == "{}"'.format(wave_date))
    df_wave['date'] = df_wave['date'].astype(np.str)  # datetime64[ns] can't be the merge index

    wave_order_type_EIQ = get_EIQ(df=df_wave, index=wave_index)
    # print('\n')
    # print('*' * 10, 'wave_order_type_EIQ', '*' * 10)
    # print(wave_order_type_EIQ)

    ### 多品多件订单货型组合
    df_multi_order = df.query('re_order_structure == "{}"'.format('多品多件'))
    multi_index = ['order_tag', 're_order_structure', 'order_type']
    multi_order_EIQ = order_distribution(df=df_multi_order, index=multi_index)

    '''
    B2 客户维度
    '''
    customer_df = customer_dimension(df, customer_df=inv_customer_df)

    '''
    B3 sku动销率
    '''
    active_col = ['week', 'sku', 'quantity']
    active_sku_df = sku_active_rate(df[active_col])

    '''
    B4 小时累积流入订单
    '''
    hour_in_col = ['time_in', 'orderID', 'sku', 'hour', 'quantity']
    hour_in_sku_df = hour_accumulate_sku(df[hour_in_col], ['2022-01-05'])

    '''
    B5 ABC分类
    '''
    abc_col = ['date', 'sku', 'quantity', 'sku_age']
    abc_df, sku_source_df = get_ABC_class(df[abc_col], inv_sku_df)
    # print(abc_df.dtypes)
    # print(abc_df.head(10))

    '''
    B6 sku&订单出库库龄
    '''
    outbound_age_col = ['orderID', 'sku', 'quantity', 'customer', 're_order_structure', 'sku_age']
    sku_age_df, order_age_df = outbound_age(df[outbound_age_col])

    # print(sku_age_df.dtypes)
    # print(sku_age_df)
    #
    # print(order_age_df.dtypes)
    # print(order_age_df)

    '''
    B7 渠道&平台订单分布
    '''
    sample_cols = ['date', 'orderID', 'sku', 'sku_size', 'quantity', 'customer', 'channel', 'platform']
    channel_index = ['channel']
    channel_order_distribution = order_distribution(df[sample_cols], index=channel_index)

    platform_index = ['platform']
    platform_order_distribution = order_distribution(df[sample_cols], index=platform_index)

    print(channel_order_distribution)
    print(platform_order_distribution)

    '''
    计算结果写入Excel表格
    '''
    ### write to file
    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}出库分析_{}.xlsx'.format(output_path, str_time))

    format_data(writer=writer, df=normal_order_week_EIQ, sheet_name='B1.1-周EIQ')
    format_data(writer=writer, df=fba_order_week_EIQ, sheet_name='B1.2-FBA EIQ')
    format_data(writer=writer, df=order_type_EIQ, sheet_name='B1.3-订单结构EIQ')
    format_data(writer=writer, df=wave_order_type_EIQ, sheet_name='B1.4-波次EIQ')
    format_data(writer=writer, df=multi_order_EIQ, sheet_name='B1.5-多品订单组合')

    format_data(writer=writer, df=customer_df, sheet_name='B2-客户动销')

    format_data(writer=writer, df=active_sku_df, sheet_name='B3-SKU动销')

    format_data(writer=writer, df=hour_in_sku_df, sheet_name='B4-SKU小时流入')

    format_data(writer=writer, df=abc_df, sheet_name='B5.1-ABC分类')
    format_data(writer=writer, df=sku_source_df, sheet_name='B5.2-SKU ABC分类明细')

    format_data(writer=writer, df=sku_age_df, sheet_name='B6.1-SKU出库库龄')
    format_data(writer=writer, df=order_age_df, sheet_name='B6.2-订单出库库龄')

    format_data(writer=writer, df=channel_order_distribution, sheet_name='B7.1-渠道分布')
    format_data(writer=writer, df=platform_order_distribution, sheet_name='B7.2-平台分布')

    writer.save()


def get_EIQ(df, index):
    EIQ_re = pd.pivot_table(df, index=index,
                            values=['orderID', 'sku', 'sku_size', 'quantity'],
                            aggfunc={'orderID': pd.Series.nunique, 'sku': pd.Series.nunique, 'sku_size': len, 'quantity': sum},
                            margins=True,
                            margins_name='总计',
                            fill_value=0).reset_index()

    EIQ_re.columns = index + ['order', 'qty', 'sku', 'line']

    order_columns = ['order', 'sku', 'line', 'qty']

    EIQ_re = EIQ_re[index + order_columns]

    # 按index的维度，增加均值和峰值
    order_columns = ['order', 'sku', 'line', 'qty']
    EIQ_re.columns = index + order_columns

    new_line = EIQ_re[:0].copy()  # 复制dataframe数据结构
    avg_value = [EIQ_re[col].mean() for col in order_columns]
    max_value = [EIQ_re[col].max() for col in order_columns]

    # 日均值行
    end_row = 0
    new_line.loc[end_row, index[0:1]] = 'Average'
    new_line.loc[end_row, order_columns] = avg_value

    # 日峰值行
    end_row += 1
    new_line.loc[end_row, index[0:1]] = 'Max'
    new_line.loc[end_row, order_columns] = max_value

    # 峰均比行
    end_row += 1
    new_line.loc[end_row, index[0:1]] = 'Max/Avg'
    new_line.loc[end_row, order_columns] = [1.00 * EIQ_re[col].max() / EIQ_re[col].mean() for col in order_columns]

    ### 增加均值、峰值、峰均比到末尾
    EIQ_re = pd.concat([EIQ_re, new_line], ignore_index=True)

    ### 计算EIQ
    EIQ_re['EN'] = EIQ_re['line'] / EIQ_re['order']
    EIQ_re['EQ'] = EIQ_re['qty'] / EIQ_re['order']
    EIQ_re['IK'] = EIQ_re['line'] / EIQ_re['sku']
    EIQ_re['IQ'] = EIQ_re['line'] / EIQ_re['sku']

    EIQ_re['qty/line'] = EIQ_re['qty'] / EIQ_re['line']

    return EIQ_re


def order_distribution(df, index):
    re = pd.pivot_table(df, index=index,
                        values=['orderID', 'quantity', 'sku', 'sku_size'],  # 行数计数任选一列，此处选择的是sku_size
                        aggfunc={'orderID': pd.Series.nunique, 'sku': pd.Series.nunique, 'sku_size': len, 'quantity': sum},
                        margins=True,
                        margins_name='总计',
                        fill_value=0).reset_index()

    re.columns = index + ['order', 'qty', 'sku', 'line']

    order_columns = ['order', 'sku', 'line', 'qty']

    re = re[index + order_columns]

    # 计算比例
    for i in range(len(order_columns)):
        re[order_columns[i] + '%'] = re[order_columns[i]] / (re[order_columns[i]].sum() / 2)

    re = re.sort_values(by='order%', ascending=False, ignore_index=True)

    return re


def customer_dimension(df, customer_df):
    '''
    :param df: 源数据
    :param customer_df: 客户库存数据
    :return:
    '''
    customer_index = ['customer']
    customer_qty = pd.pivot_table(df, index=customer_index,
                                  values=['quantity', 'date'],
                                  columns=['re_order_structure'],
                                  aggfunc={'quantity': np.sum, 'date': pd.Series.nunique},
                                  margins=True,
                                  margins_name='总计',
                                  fill_value=0).reset_index()

    ### 多级索引转成单层索引
    customer_qty.columns = [s1 + '_' + str(s2) for (s1, s2) in customer_qty.columns.tolist()]
    print(customer_qty.head(10))

    order_type = ['单品单件', '单品多件', '多品多件', '批量订单', '总计']
    # 计算日均出库件数
    for i in range(len(order_type)):
        customer_qty['日均件_' + order_type[i]] = 0
        customer_qty.loc[(customer_qty['date_' + order_type[i]]) > 0, ['日均件_' + order_type[i]]] = customer_qty['quantity_' + order_type[i]] / customer_qty[
            'date_' + order_type[i]]

    # print('\n')
    # print(customer_qty.head(10))

    col = ['customer_', 'quantity_总计', 'date_总计', '日均件_总计', '日均件_单品单件', '日均件_单品多件', '日均件_多品多件', '日均件_批量订单']
    re_col = ['customer', '出库总件数', '出库天数', '日均出库件数', '日均件_单品单件', '日均件_单品多件', '日均件_多品多件', '日均件_批量订单']

    customer_qty = customer_qty[col]
    customer_qty.columns = re_col

    '''月&日均动销SKU'''
    month_cnt = pd.pivot_table(df, index=['month'],
                               values=['date'],
                               aggfunc=pd.Series.nunique).reset_index()

    # 查询月份时期最大的月份
    select_month = 0
    days = 0
    # 选取天数最大的月份
    for index, row in month_cnt.iterrows():
        if row['date'] > days:
            days = row['date']
            select_month = row['month']
    # 数据源中总天数小于等于30天，月动销sku不做筛选
    if month_cnt['date'].sum() <= 30:
        select_month = 0

    if select_month > 0:
        active_df = df.query('month == {}'.format(select_month))
    else:
        active_df = df

    customer_month_sku = pd.pivot_table(active_df, index=customer_index,
                                        values=['sku'],
                                        aggfunc=pd.Series.nunique,
                                        margins=True,
                                        margins_name='总计').reset_index()
    customer_month_sku.columns = customer_index + ['月动销sku']

    # print('active_df: ', active_df.columns)
    # print('active_df shape: ', active_df.shape)

    sku_index = ['customer', 'date']
    customer_daily_sku2 = active_df[sku_index + ['sku']].groupby(sku_index).nunique().reset_index()

    customer_daily_sku = pd.pivot_table(customer_daily_sku2, index=customer_index,
                                        values=['sku'],
                                        margins_name='总计',
                                        fill_value=0).reset_index()

    customer_daily_sku.columns = customer_index + ['日均动销sku']
    # customer_daily_sku['日均动销sku'] = customer_daily_sku[customer_daily_sku>0].mean(axis=1)

    customer_sku = pd.merge(customer_month_sku, customer_daily_sku, on='customer', how='left')

    customer_temp = pd.merge(customer_df, customer_qty, on='customer', how='left')

    customer_re = pd.merge(customer_temp, customer_sku, on='customer', how='left').fillna(0)

    # print('customer_re detail: \n')
    # print(customer_re.head(10))

    '''增加整体计算值'''

    customer_re['sku日动销率'] = customer_re['日均动销sku'] / customer_re['sku数']
    customer_re['sku月动销率'] = customer_re['月动销sku'] / customer_re['sku数']

    customer_re.loc[(customer_re['sku月动销率'] >= 1), ['sku月动销率']] = 1

    customer_re['库存周期'] = customer_re['在库件数'] / customer_re['日均出库件数']

    customer_re = customer_re.sort_values(by='日均出库件数', ascending=False, ignore_index=True)

    return customer_re


def sku_active_rate(df, index=None):
    '''
    计算不同时间周期内SKU的动销率
    :param df: 包含分组标签列，如week列， 必须包含sku、件数列的dataframe
    :return:
    '''
    if index is None:
        index = ['week']
    df.sort_values(by=index).reset_index()  # 按周排序

    groups_df = df.groupby(index)

    group_dict = {}
    sku_dict = {}
    for item, group in groups_df:
        sku_dict[item] = set(group['sku'])
        group_dict[item] = group

    sku_cnt = []
    for k, v in sku_dict.items():
        curr = k
        if k + 1 > 52:
            next = 1
        else:
            next = k + 1

        curr_cnt = len(v)

        ### sku交集
        comm_sku_set = v.intersection(sku_dict.get(next, {}))
        curr_df = group_dict[curr]
        curr_qty = curr_df['quantity'].sum()
        curr_comm_qty = curr_df[curr_df['sku'].isin(list(comm_sku_set))]['quantity'].sum()

        next_df = group_dict.get(next, None)
        if next_df is None:
            next_qty = 0
            next_comm_qty = 0
        else:
            next_qty = next_df['quantity'].sum()
            next_comm_qty = next_df[next_df['sku'].isin(list(comm_sku_set))]['quantity'].sum()

        comm_cnt = len(v.intersection(sku_dict.get(next, {})))
        in_cnt = len(set(sku_dict.get(next, {})).difference(v))
        out_cnt = len(v.difference(sku_dict.get(next, {})))

        sku_cnt.append([curr, next, curr_cnt, comm_cnt, in_cnt, out_cnt, curr_qty, next_qty, curr_comm_qty, next_comm_qty])

    sku_col = ['curr_{}'.format(index[-1]), 'next_{}'.format(index[-1]), '当前sku', '重合sku', '流入sku', '流出sku',
               'current件数', 'next件数', 'current重合sku件数', 'next重合sku件数']

    sku_df = pd.DataFrame(sku_cnt, columns=sku_col)

    sku_df['sku池变化率'] = sku_df['流入sku'] / sku_df['当前sku']
    sku_df['current重合sku件数%'] = sku_df['current重合sku件数'] / sku_df['current件数']
    sku_df['next重合sku件数%'] = sku_df['next重合sku件数'] / sku_df['next件数']

    sku_df = sku_df.sort_values(by=['next_{}'.format(index[-1])]).fillna(0)

    print('\n')
    print(sku_df)
    return sku_df


def hour_accumulate_sku(df, date, cutoff_hour=12):
    '''
    计算给定日期的订单累计流入
    :param df: 必须包含time_in（或date，hour）列，订单号，sku,件数字段 ['time_in', 'orderID', 'sku', 'hour', 'quantity']
    :param date: 日期筛选参数，兼容string和list类型
    :return:
    '''

    # 从流入时间字段中截取日期
    df['date'] = pd.to_datetime(df['time_in'].dt.date)

    # print(df.head(10))

    df['process_date'] = df['date']
    print(df.dtypes)
    print(df.head(10))

    df['day_delta'] = pd.Timedelta(days=0)
    df.loc[(df['hour'] >= cutoff_hour), ['day_delta']] = pd.Timedelta(days=1)

    ### 将日期列转化为float，进行加减
    df['process_date'] = df['process_date'].values.astype(float)
    df['day_delta'] = df['day_delta'].values.astype(float)

    # 更新截单点后的操作日期
    df.loc[(df['hour'] >= cutoff_hour), ['process_date']] = pd.to_datetime(df['process_date'] + df['day_delta'])
    df['process_date'] = pd.to_datetime(df['process_date'])
    df = df.drop(columns='day_delta')  # 删除计算操作日期的辅助列

    ### 计算累计订单是的index
    df['index_hour'] = df['hour'].apply(lambda x: x - cutoff_hour if x >= cutoff_hour else x + (24 - cutoff_hour))

    if type(date) is np.str:
        df = df.query('process_date == "{}"'.format(date))
    elif type(date) is list:
        df = df.loc[df['process_date'].isin(date)]
    else:
        print("请输入正确的日期参数！")
        print("形如 "'"2022-01-01"'" 或 ["'"2022-01-01"'", "'"2022-01-10"'", "'"2022-01-15"'"]")

    print('订单累计流入数据源')
    print(df.dtypes)
    print(df.head(10))

    '''
    初始化结果dataframe
    '''
    re_col = ['date', 'curr_hour', 'next_hour', 'local_hour', 'order_cnt', 'line_cnt', 'sku_cnt', 'qty', 'in_sku', 'out_sku',
              'cumu_order_cnt', 'cumu_line_cnt', 'cumu_sku_cnt', 'cumu_qty',
              'cumu_order_cnt%', 'cumu_line_cnt%', 'cumu_sku_cnt%', 'cumu_qty%']
    re_df = pd.DataFrame(columns=re_col)

    ## 按操作日期分组
    df['process_date'] = df['process_date'].astype(np.str)  # process_date作为groupby的index，转化为string更简洁
    date_groups = df.groupby(['process_date'])

    for day, date_df in date_groups:
        hour_groups = date_df.groupby(['index_hour'])

        hour_dict = {}
        hour_list = []
        for h, hour_df in hour_groups:
            hour_dict[h] = hour_df

        for i in range(24):
            curr_hour = i
            next_hour = i + 1

            if curr_hour >= cutoff_hour:
                local_hour = curr_hour - cutoff_hour
            else:
                local_hour = curr_hour + cutoff_hour

            ### current hour order discrible

            # 若当前小时没有订单数据，给curr_df赋值0，订单描述性参数都为0
            curr_df = hour_dict.get(curr_hour, None)
            next_df = hour_dict.get(next_hour, None)
            if curr_df is not None:
                order_cnt = curr_df['orderID'].nunique()
                line_cnt = curr_df.shape[0]
                sku_cnt = curr_df['sku'].nunique()
                qty = curr_df['quantity'].sum()
            else:
                order_cnt = 0
                line_cnt = 0
                sku_cnt = 0
                qty = 0

            ### 统计当前小时的sku流入流出
            if curr_df is not None and next_df is not None:
                in_cnt = len(set(next_df['sku'].unique()).difference(set(curr_df['sku'].unique())))
                out_cnt = len(set(curr_df['sku'].unique()).difference(set(next_df['sku'].unique())))
            elif curr_df is not None:
                in_cnt = 0
                out_cnt = sku_cnt
            elif next_df is not None:
                in_cnt = next_df['sku'].nunique()
                out_cnt = 0
            else:
                in_cnt = 0
                out_cnt = 0

            ### accumulate order discrible
            # 若累计到当前小时没有订单数据，给cumu_df赋值0，订单描述性参数都为0
            cumu_df = date_df[date_df['index_hour'] <= curr_hour]
            if cumu_df.shape[0] != 0:
                cumu_order_cnt = cumu_df['orderID'].nunique()
                cumu_line_cnt = cumu_df.shape[0]
                cumu_sku_cnt = cumu_df['sku'].nunique()
                cumu_qty = cumu_df['quantity'].sum()
            else:
                cumu_order_cnt = 0
                cumu_line_cnt = 0
                cumu_sku_cnt = 0
                cumu_qty = 0

            hour_list.append([day, curr_hour, next_hour, local_hour, order_cnt, line_cnt, sku_cnt, qty, in_cnt, out_cnt,
                              cumu_order_cnt, cumu_line_cnt, cumu_sku_cnt, cumu_qty])

        hour_accu_col = ['date', 'curr_hour', 'next_hour', 'local_hour', 'order_cnt', 'line_cnt', 'sku_cnt', 'qty', 'in_sku', 'out_sku',
                         'cumu_order_cnt', 'cumu_line_cnt', 'cumu_sku_cnt', 'cumu_qty']
        hour_accu_df = pd.DataFrame(hour_list, columns=hour_accu_col)

        ### 增加累计比例列
        accu_percentage_col = ['order_cnt', 'line_cnt', 'sku_cnt', 'qty']
        for i in accu_percentage_col:
            if i == 'sku_cnt':
                total_sku = hour_accu_df.tail(1)['cumu_' + i].to_list()
                hour_accu_df['cumu_' + i + '%'] = hour_accu_df['cumu_' + i] / total_sku
            else:
                hour_accu_df['cumu_' + i + '%'] = hour_accu_df['cumu_' + i] / hour_accu_df[i].sum()

        re_df = re_df.append(hour_accu_df)

    # print('='*10, '订单累计流入结果')
    # print(re_df.dtypes)
    # print(re_df)

    return re_df


def get_ABC_class(df, inv_sku_df, period=None, ratio=None, freq=None, interval=None, multi_para=None, multiple=True):
    '''
    :param df: ABC分类原始数据，必须包含sku, 件数，出库日期，库龄字段 ['date', 'sku', 'quantity', 'sku_age']
    :param inv_sku_df: 库存sku数据，包含字段 [产品代码	在库件数	在库体积(m³)	库龄	库龄等级]
    :param period: 计算周期，若为空则计算所有数据，若非空，对日期列 date 进行筛选;
                    period为列表形式，第一个元素为开始日期，第二个元素为结束日期
    :param ratio: 出库件数ABC分类参数
    :param freq: 出库天数频次ABC分类参数
    :param interval: 出库最大间隔天数ABC分类参数
    :param multi_para: 组合ABC的定义参数
    :param multiple: True时返回组合ABC, 否则返回件数ABC
    :return: sku_ABC_df. ABC分类汇总后的结果，sku_df:ABC原始数据
    '''

    if ratio is None:
        ratio = [0.7, 0.2, 0.1]  # A类累计占比70%， B类累计占比70%~90%， C类累计占比90%~100%
    if freq is None:
        freq = [0.5, 0.2]  # A类出库频次大于50%， B类出库频次为20%~50%， C类出库批次小于20%
    if interval is None:
        interval = [3, 10]

    ### ABC计算周期
    if period is not None:
        if type(period) is list:
            start = period[0]
            end = period[1]
            df = df.query('date >= "{}" & date <= "{}"'.format(start, end))

    if multi_para is None:
        multi_para = {'A': [1, 0],
                      'C': [0, 2]}
    ### 出库件数ABC 和 出库频次ABC

    sku_df = pd.pivot_table(df,
                            index=['sku'],
                            values=['date', 'quantity'],
                            aggfunc={'date': pd.Series.nunique, 'quantity': np.sum},
                            fill_value=0).reset_index()

    ### 根据同一sku不同出库时间的库龄计算sku的加权库龄
    sku_age = pd.pivot_table(df, index=['sku'],
                             values=['sku_age'],
                             aggfunc=lambda rows: np.average(rows, weights=df.loc[rows.index, 'quantity']),
                             margins=False,
                             fill_value=0).reset_index()

    sku_df = pd.merge(sku_df, sku_age, on=['sku'], how='left')

    sku_df = sku_df.sort_values(by='quantity', ascending=False)
    sku_df.columns = ['sku', 'ob_days', 'ob_quantity', 'sku_age']

    ''' 计算sku出库库龄等级'''
    sku_df['sku_age_class'] = ''
    rank_num = len(config.AGE_CLASS)
    for i in range(rank_num):
        sku_df.loc[(sku_df['sku_age'] > config.AGE_CLASS[i][1]) & (sku_df['sku_age'] <= config.AGE_CLASS[i][2]), ['sku_age_class']] = config.AGE_CLASS[i][0]

    '''计算出库件数ABC'''
    sku_df['cumu_qty'] = sku_df['ob_quantity'].cumsum()
    sku_df['cumu_qty%'] = sku_df['ob_quantity'] / sku_df['ob_quantity'].sum()

    # 计算ABC
    sku_df['qty_ABC'] = 'C'
    sku_df.loc[(sku_df['cumu_qty%'] <= sum(ratio[0:2])), ['qty_ABC']] = 'B'
    sku_df.loc[(sku_df['cumu_qty%'] <= sum(ratio[0:1])), ['qty_ABC']] = 'A'

    index_ABC = ''
    ### 判断是否计算组合ABC
    if multiple == False:
        single_col = ['sku', 'ob_quantity', 'cumu_qty%', 'qty_ABC']
        sku_df = sku_df[single_col]
        index_ABC = 'qty_ABC'

    else:

        ''' 计算出库频次ABC '''
        total_day = df['date'].nunique()
        sku_df['freq_day'] = sku_df['ob_days'] / total_day

        # 计算ABC
        sku_df['freq_ABC'] = 'B'
        sku_df.loc[(sku_df['freq_day'] >= freq[0]), ['freq_ABC']] = 'A'
        sku_df.loc[(sku_df['freq_day'] < freq[1]), ['freq_ABC']] = 'C'

        '''计算动销间隔天数ABC'''
        temp_df = df[['sku', 'date']]
        temp_df = temp_df.sort_values(by=['sku', 'date'])
        sku_groups = temp_df.groupby(['sku'])

        sku_interval_day_list = []
        for sku, group in sku_groups:
            group['interval_days'] = pd.to_timedelta(group['date'].shift(-1) - group['date']).dt.days
            max_interval_days = group['interval_days'].max()
            sku_interval_day_list.append([sku, max_interval_days])

        sku_interval_day_df = pd.DataFrame(sku_interval_day_list, columns=['sku', 'max_interval_days'])

        ### 计算间隔天数ABC
        sku_interval_day_df['interval_ABC'] = 'B'

        sku_interval_day_df.loc[(sku_interval_day_df['max_interval_days'] < interval[0]), ['interval_ABC']] = 'A'
        sku_interval_day_df.loc[(sku_interval_day_df['max_interval_days'] > interval[1]), ['interval_ABC']] = 'C'

        sku_df = pd.merge(sku_df, sku_interval_day_df, on='sku', how='left')

        '''
        计算3个维度的组合ABC
        '''
        ABC_col = ['qty_ABC', 'freq_ABC', 'interval_ABC']
        abc = ['A', 'B', 'C']
        # 统计3个维度ABC的个数
        for item in abc:
            sku_df[item + '_cnt'] = sum([sku_df[col].map(lambda x: x.count(item)) for col in ABC_col])

        # 根据ABC的个数计算组合ABC

        sku_df['combine_ABC'] = 'B'
        sku_df.loc[(sku_df['A_cnt'] >= multi_para['A'][0]) & (sku_df['C_cnt'] == multi_para['A'][1]), ['combine_ABC']] = 'A'
        sku_df.loc[(sku_df['A_cnt'] == multi_para['C'][0]) & (sku_df['C_cnt'] >= multi_para['C'][1]), ['combine_ABC']] = 'C'

        multi_col = ['sku', 'ob_quantity', 'cumu_qty%', 'qty_ABC', 'ob_days', 'freq_day', 'freq_ABC', 'max_interval_days', 'interval_ABC', 'combine_ABC']
        sku_df = sku_df[multi_col]

        index_ABC = 'combine_ABC'

    print('inventory sku pivot!!!!!!!!!!!!!!')
    print(inv_sku_df.columns)
    print(inv_sku_df.shape)
    print(inv_sku_df.head(10))

    print('outbound sku pivot!!!!!!!!!!!!!!')
    print(sku_df.columns)
    print(sku_df['combine_ABC'].value_counts())

    sku_df = pd.merge(sku_df, inv_sku_df, on=['sku'], how='left')
    print('test！！！！！！！！！！！')
    print(sku_df.columns)
    print(sku_df.shape)

    index = [index_ABC] + ['age_class']
    print('index: ', index)
    sku_ABC_df = pd.pivot_table(sku_df,
                                index=index,
                                values=['ob_quantity', 'inv_quantity', 'sku'],
                                aggfunc={'ob_quantity': np.sum, 'inv_quantity': np.sum, 'sku': pd.Series.nunique},
                                margins=True,
                                fill_value=0).reset_index()

    print(sku_ABC_df.dtypes)
    print(sku_ABC_df)

    return sku_ABC_df, sku_df


def outbound_age(df):
    '''

    :param df: 出库库龄源数据，必须包含字段  ['orderID', 'sku', 're_order_structure', 'sku_age']
    :return:
    '''

    # 实例化配置参数
    config = Config()
    config.run()

    ''' 计算sku出库库龄等级'''
    df['sku_age_class'] = ''
    rank_num = len(config.AGE_CLASS)
    for i in range(rank_num):
        df.loc[(df['sku_age'] > config.AGE_CLASS[i][1]) & (df['sku_age'] <= config.AGE_CLASS[i][2]), ['sku_age_class']] = config.AGE_CLASS[i][0]

    '''计算订单出库库龄'''
    order_df = df.groupby(['orderID'])['sku_age'].max().reset_index()
    order_df['order_age_class'] = ''
    for i in range(rank_num):
        order_df.loc[(order_df['sku_age'] > config.AGE_CLASS[i][1]) & (order_df['sku_age'] <= config.AGE_CLASS[i][2]), ['order_age_class']] = config.AGE_CLASS[i][0]

    order_df = order_df[['orderID', 'order_age_class']]
    df = pd.merge(df, order_df, on='orderID', how='left')

    sku_age_df = general_pivot(df, index=['sku_age_class'], pt_col=['quantity', 'sku'], distinct_count=['sku'], isCumu=True)

    order_age_df = general_pivot(df, index=['order_age_class', 're_order_structure'], pt_col=['orderID', 'quantity'], distinct_count=['orderID'], isCumu=True)

    return sku_age_df, order_age_df


def general_pivot(df, index, pt_col, distinct_count=None, isCumu=False):
    """
    :param df: 透视表原始数据
    :param index: 透视的行
    :param distinct_count: 是否添加 SKU_ID 字段
    :param pt_col: 透视的 values，即透视字段
    :param isCumu: 默认为False, 是否计算累计比例
    :return:
    """

    col_function = {}

    for col in pt_col:
        f = np.sum
        if distinct_count is not None and col in distinct_count:
            f = pd.Series.nunique

        col_function[col] = f

    result_pt = pd.pivot_table(df, index=index,
                               values=pt_col,
                               aggfunc=col_function,
                               fill_value=0).reset_index()

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(cols)):
        result_pt.loc[result_pt[index[0]] == 'All', [cols[i]]] = df[cols[i]].sum()

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i]] / (result_pt[cols[i]].sum())

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt['cumu_' + cols[i] + '%'] = result_pt[cols[i] + '%'].cumsum()

    return result_pt
