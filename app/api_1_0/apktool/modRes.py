#!/usr/bin/python
# -*- coding=utf-8 -*-
# author : wklken@yeah.net
# date: 2012-05-25
# version: 0.1
 
from xml.etree.ElementTree import ElementTree,Element
 
def read_xml(in_path):
  '''读取并解析xml文件
    in_path: xml路径
    return: ElementTree'''
  tree = ElementTree()
  tree.parse(in_path)
  return tree
 
def write_xml(tree, out_path):
  '''将xml文件写出
    tree: xml树
    out_path: 写出路径'''
  tree.write(out_path, encoding="utf-8",xml_declaration=True)
 
def if_match(node, kv_map):
  '''判断某个节点是否包含所有传入参数属性
    node: 节点
    kv_map: 属性及属性值组成的map'''
  for key in kv_map:
    if node.get(key) != kv_map.get(key):
      return False
  return True
 
#---------------search -----
def find_nodes(tree, path):
  '''查找某个路径匹配的所有节点
    tree: xml树
    path: 节点路径'''
  return tree.findall(path)
 
def get_node_by_keyvalue(nodelist, kv_map):
  '''根据属性及属性值定位符合的节点，返回节点
    nodelist: 节点列表
    kv_map: 匹配属性及属性值map'''
  result_nodes = []
  for node in nodelist:
    if if_match(node, kv_map):
      result_nodes.append(node)
  return result_nodes
 

 
def change_node_text(nodelist, text, is_add=False, is_delete=False):
  '''改变/增加/删除一个节点的文本
    nodelist:节点列表
    text : 更新后的文本'''
  for node in nodelist:
    if is_add:
      node.text += text
    elif is_delete:
      node.text = ""
    else:
      node.text = text
 

 

 

 
def modifyRes(Name,xmlPath):
  #1. 读取xml文件
  xmlPath = xmlPath + "/res/values/strings.xml"
  tree = read_xml(xmlPath)
 
  #5. 修改节点文本
    #定位节点
  text_nodes = get_node_by_keyvalue(find_nodes(tree, "string"), {"name":"app_name"})
  change_node_text(text_nodes, Name)
  text_nodes = get_node_by_keyvalue(find_nodes(tree, "string"), {"name":"owner_name"})
  change_node_text(text_nodes, Name)
  #6. 输出到结果文件
  write_xml(tree, xmlPath)