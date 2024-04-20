import json
import requests
import threading

def extract_all_uris(json_data):
    all_uris = []
    for item in json_data['items']:
        uris = item.get('login', {}).get('uris', [])
        for uri_info in uris:
            all_uris.append((item, uri_info))
    return all_uris

def test_uri(item, uri_info, not_accessible_uris):
    uri = uri_info.get('uri')
    user = item.get('login', {}).get('username')
    password = item.get('login', {}).get('password')
    try:
        response = requests.get(uri, timeout=5)  # 设置超时时间为 5 秒
        if response.status_code == 200:
            return True  # URI 可用
    except Exception as e:
        with lock:
            not_accessible_uris.append((uri, user, password))
        return False  # URI 不可用

# 读取 JSON 文件并解析
json_file_path = './file.json'
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# 提取所有 URI
all_uris = extract_all_uris(json_data)
not_accessible_uris = []
lock = threading.Lock()  # 创建锁对象

# 使用多线程测试所有的 URI 是否可用
threads = []
for item, uri_info in all_uris:
    thread = threading.Thread(target=test_uri, args=(item, uri_info, not_accessible_uris))
    threads.append(thread)
    thread.start()

# 等待所有线程执行完毕
for thread in threads:
    thread.join()

# 显示所有不可用的 URI，并询问用户是否要删除对应的 JSON 字段
for uri, user, password in not_accessible_uris:
    choice = input(f"URI {uri} {user}:{password} 不可用(回车删除，其他任意输入保留): ")
    if choice.lower() == '':
        # 删除不可用 URI 相关的项目
        json_data['items'] = [item for item in json_data['items'] if uri != item.get('login', {}).get('uris', [{}])[0].get('uri')]

# 保存更新后的 JSON 文件
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, indent=4)
