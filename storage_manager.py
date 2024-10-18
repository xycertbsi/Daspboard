import os
import psutil
import shutil

def get_disks():
    partitions = psutil.disk_partitions()
    disks = []
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        disk = {
            'device': partition.device,
            'mountpoint': partition.mountpoint,
            'fstype': partition.fstype,
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent
        }
        disks.append(disk)
    return disks

def get_directory_contents(path):
    contents = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            size = os.path.getsize(item_path) if not is_dir else get_dir_size(item_path)
            contents.append({
                'name': item,
                'path': item_path,
                'is_dir': is_dir,
                'size': size,
                'modified': os.path.getmtime(item_path)
            })
    except PermissionError:
        return None
    return sorted(contents, key=lambda x: (not x['is_dir'], x['name'].lower()))

def get_dir_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_file_content(path, max_size=1024*1024):  # Max size: 1MB
    try:
        if os.path.getsize(path) > max_size:
            return "A fájl túl nagy a megjelenítéshez"
        with open(path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Hiba a fájl olvasása közben: {str(e)}"