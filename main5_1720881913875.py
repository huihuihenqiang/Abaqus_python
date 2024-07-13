# -*- coding: utf-8 -*-
'''
    可以多次提取不同odb的不同部件的点的位移和应力
'''
# 导入必要的库
import json
import numpy as np
from abaqus import *
from abaqusConstants import *
from odbAccess import *
import xlwt
import time
import os
import sys

# 定义进度条打印函数
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='#'):
    """
    调用示例：
    print_progress_bar(0, 100, prefix='Progress:', suffix='Complete', length=50)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    if iteration == total:
        print()

# 定义Odb数据提取类
class OdbDataExtractor:
    def __init__(self, config):
        """
        初始化方法，从配置中读取odb文件路径、部件实例名、节点标签、元素标签等信息
        :param config: 配置字典，包含odb文件路径等信息
        """
        self.odb_files = config['odb_files']
        self.part_instance_name = config['part_instance']
        self.node_labels = config['node_labels']
        self.element_labels = config['element_labels']
        self.U2_name = config['U2_name']
        self.LE_name = config['LE_name']

    def extract_U2data(self, odb, o_name):
        """
        提取节点的U2位移数据，并保存到Excel文件
        :param odb: ABAQUS数据库对象
        :param o_name: 文件名前缀
        """
        for i in range(len(self.node_labels)):
            try:
                instance_name = self.part_instance_name[i]  # 实例名称
                node_labels = (self.node_labels[i],)  # 节点标签
                # 根据实例名称和节点标签获取节点集合
                instance = odb.rootAssembly.instances['{}'.format(instance_name)]
                nodes = instance.NodeSetFromNodeLabels(name='{}+{}'.format(o_name, self.U2_name[i]), nodeLabels=node_labels)
                # 保存数据到列表中，每行是一个时间点的所有节点位移数据
                results = []
                time = np.linspace(0, 0.01, 101)
                for frame_index, frame in enumerate(odb.steps['Step-1'].frames):
                    values = frame.fieldOutputs['U'].getSubset(region=nodes).values
                    sub_result = [value.data[1] for value in values]  # 提取U2位移数据
                    results.append([time[frame_index], sub_result])
                # 保存结果到Excel文件
                self.save_to_excel(results, '{}.xls'.format(self.U2_name[i]), o_name)
                print('{} has saved!'.format(self.U2_name[i]))
            except Exception as e:
                print("errorU2:", e)

    def extract_LEdata(self, odb, o_name):
        """
        提取元素的最大主应力（LE）数据，并保存到Excel文件
        :param odb: ABAQUS数据库对象
        :param o_name: 文件名前缀
        """
        for i in range(len(self.element_labels)):
            try:
                instance_name = self.part_instance_name[i]  # 实例名称
                element_labels = (self.element_labels[i],)  # 元素标签
                # 根据实例名称和元素标签获取元素集合
                instance = odb.rootAssembly.instances['{}'.format(instance_name)]
                elements = instance.ElementSetFromElementLabels(name='{}+{}'.format(o_name, self.LE_name[i]),
                                                                elementLabels=element_labels)
                # 保存数据到列表中，每行是一个时间点的所有元素最大主应力数据
                results = []
                time = np.linspace(0, 0.01, 101)
                for frame_index, frame in enumerate(odb.steps['Step-1'].frames):
                    values = frame.fieldOutputs['LE'].getSubset(region=elements).values
                    sub_result = [value.maxPrincipal for value in values]  # 提取最大主应力数据
                    results.append([time[frame_index], sub_result])
                # 保存结果到Excel文件
                self.save_to_excel(results, '{}.xls'.format(self.LE_name[i]), o_name)
                print('{} has saved!'.format(self.LE_name[i]))
            except Exception as e:
                print("errorU2:", e)

    def save_to_excel(self, results, output_file, o_name):
        """
        将数据保存到Excel文件
        :param results: 要保存的数据列表
        :param output_file: 输出文件名
        :param o_name: 文件名前缀
        """
        # 创建新的工作簿和工作表
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet1')
        data = results
        file_name = 'D:\shiyan\{}\{}'.format(o_name, output_file)
        directory = os.path.dirname(file_name)

        # 确保目录存在，如果不存在则创建
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 将数据写入工作表
        for row_index, row in enumerate(data):
            worksheet.write(row_index, 0, row[0])  # 写入时间数据
            for col_index, value in enumerate(row[1]):
                worksheet.write(row_index, col_index + 1, str(value))  # 写入位移或应力数据

        # 保存工作簿
        workbook.save(file_name)

# 主函数入口
def main():
    # 读取配置文件
    try:
        with open(r'D:\shiyan\cc.json', 'r') as f:
            config = json.load(f)

        extractor = OdbDataExtractor(config)
    except Exception as e:
        print("error:4444")
    # 循环处理每个odb文件
    for i in range(len(extractor.odb_files)):
        odb = openOdb(path='{}'.format(extractor.odb_files[i]))
        file_name_with_extension = extractor.odb_files[i].split('/')[-1]  # 提取文件名
        o_name = file_name_with_extension.split('.')[0]  # 提取文件名前缀
        # 分别提取并保存U2位移和LE应力数据
        extractor.extract_U2data(odb, o_name)
        extractor.extract_LEdata(odb, o_name)
        odb.close()
        print_progress_bar(i + 1, len(extractor.odb_files), prefix='Progress:', suffix='Complete', length=50)

if __name__ == "__main__":
    print("start!")
    start_time = time.time()
    main()
    end_time = time.time()
    print("alltime:{:.2f}s".format(end_time - start_time))
