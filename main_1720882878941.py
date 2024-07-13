# -*- coding: utf-8 -*-
'''
模块说明：该模块用于从Abaqus数据库中提取特定部件的应力和应变数据，并将这些数据保存到Excel文件中。
'''
import json

import numpy as np
from abaqus import *
from abaqusConstants import *
from odbAccess import *
import xlwt
import time

class OdbDataExtractor:
    """
    类说明：该类用于提取Abaqus数据库中的特定数据，并将其保存到Excel文件中。
    
    参数：
    - config: 包含数据库文件路径、部件实例名称、节点标签、元素标签等信息的配置字典。
    """
    
    def __init__(self, config):
        """
        初始化方法：打开数据库文件，获取所有帧数据。
        
        参数：
        - config: 配置字典，包含odb文件路径等信息。
        """
        self.odb_files = config['odb_files']
        self.part_instance_name = config['part_instance']
        self.node_labels = config['node_labels']
        self.element_labels = config['element_labels']
        self.U2_name = config['U2_name']
        self.LE_name = config['LE_name']
        print('{}'.format(self.odb_files))
        self.odb = openOdb(path='{}'.format(self.odb_files))
        self.all_frames = self.odb.steps['Step-1'].frames
    
    def extract_U2data(self):
        """
        提取节点的位移数据，并保存到Excel文件中。
        
        参数：
        - None
        """
        for i in range(len(self.node_labels)):
            try:
                instance_name = self.part_instance_name[i]
                node_labels = (self.node_labels[i],)
                instance = self.odb.rootAssembly.instances['{}'.format(instance_name)]
                nodes = instance.NodeSetFromNodeLabels(name='{}'.format(self.U2_name[i]), nodeLabels=node_labels)
                results = []
                time = np.linspace(0, 0.01, 101)
                for frame_index, frame in enumerate(self.all_frames):
                    values = frame.fieldOutputs['U'].getSubset(region=nodes).values
                    sub_result = []
                    for value in values:
                        txt_line = (value.data)[1]
                        sub_result.append(txt_line)
                    results.append([time[frame_index], sub_result])
                self.save_to_excel(results, '{}.xls'.format(self.U2_name[i]))
                print('{} has saved!'.format(self.U2_name[i]))
            except Exception as e:
                print("errorU2:", e)
    
    def extract_LEdata(self):
        """
        提取元素的最大主应力数据，并保存到Excel文件中。
        
        参数：
        - None
        """
        for i in range(len(self.element_labels)):
            try:
                instance_name = self.part_instance_name[i]
                element_labels = (self.element_labels[i],)
                instance = self.odb.rootAssembly.instances['{}'.format(instance_name)]
                elements = instance.ElementSetFromElementLabels(name='{}'.format(self.LE_name[i]), elementLabels=element_labels)
                results = []
                time = np.linspace(0, 0.01, 101)
                for frame_index, frame in enumerate(self.all_frames):
                    values = frame.fieldOutputs['LE'].getSubset(region=elements).values
                    sub_result = []
                    for value in values:
                        txt_line = value.maxPrincipal
                        sub_result.append(txt_line)
                    results.append([time[frame_index], sub_result])
                print(results)
                self.save_to_excel(results, '{}.xls'.format(self.LE_name[i]))
                print('{} has saved!'.format(self.LE_name[i]))
            except Exception as e:
                print("errorLE:", e)
    
    def save_to_excel(self, results, output_file):
        """
        将数据保存到Excel文件中。
        
        参数：
        - results: 要保存的数据列表。
        - output_file: 输出的Excel文件名。
        """
        # 创建一个新的工作簿和工作表
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet1')
        data = results
        file_name = 'D:\shiyan\{}'.format(output_file)
        
        # 将数据写入工作表
        for row_index, row in enumerate(data):
            worksheet.write(row_index, 0, row[0])  # 写入第一列的数据
            for col_index, value in enumerate(row[1]):
                worksheet.write(row_index, col_index + 1, str(value))
        
        # 保存为 Excel 文件
        workbook.save(file_name)


def main():
    # 读取配置文件
    with open(r'D:\shiyan\cc.json', 'r') as f:
        config = json.load(f)

    extractor = OdbDataExtractor(config)
    #extractor.extract_U2data()
    extractor.extract_LEdata()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print("alltime:{:.2f}s".format(end_time - start_time))
