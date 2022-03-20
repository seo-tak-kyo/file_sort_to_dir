import os
import shutil
import dateutil.parser as dparser

def file_copy(in_path, out_path):
    shutil.copy(in_path, out_path)

def get_dir_list(path):
    return os.listdir(path)

"""
IMG_20190503_130506 이런 문자가 들어오면 
datetime.datetime 형의 인자를 반환한다.
"""
def str_to_datetime(str_date):
    try:
        str_split = str_date.split('_')
        for i in str_split: 
            try:
                ret_date = dparser.parse(i, fuzzy=True)
            except:
                ret_date = None

            if ret_date:
                return ret_date

        return None    
    except:
        return None

if __name__ == "__main__":
  in_str = "IMG_20190503_130506.mp4"
  out_date = str_to_datetime(in_str)
  print("input :", in_str)
  print("out : ", out_date)

