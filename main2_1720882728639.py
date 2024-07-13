# -*- coding: utf-8 -*-
"""
该脚本用于从Abaqus odb文件中提取特定单元的最大主应变数据。
"""
# 导入Abaqus库和常量
# 打开Odb文件
odb = openOdb(path=r'E:/aa/cc/V6_Ball_6/V6_Ball_6.odb')

# 选择odb中的特定部件实例
# 获取Part实例
part_instance = odb.rootAssembly.instances['BOTTOMFOAM-1']

# 选择特定的元素集合
element_labels = (40666,)
# 获取元素和积分点
element = part_instance.ElementSetFromElementLabels(name='dfrgvgcd', elementLabels=element_labels)

# 获取所有属性，用于后续处理（这里仅用于展示，实际代码中可能不需要）
attributes = [attr for attr in dir(part_instance) if not attr.startswith('__')]
print(attributes)

# 明确指定要获取的积分点数据
integration_point = 1

# 从最后一步和最后一帧中获取场输出数据
# 获取应变场数据
field_output = odb.steps['Step-1'].frames[-1].fieldOutputs['LE']

# 从场输出数据中提取特定元素的应变数据
# 过滤出特定单元的场数据
element_data = field_output.getSubset(region=element)

# 初始化最大主应变变量
max_principal_strain = None

# 遍历所有值，找到最大主应变
for value in element_data.values:
    max_principal_strain = value.maxPrincipal

# 输出最大主应变
print(max_principal_strain)

# 注释掉的odb关闭操作
#odb.close()
