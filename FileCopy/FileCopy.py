import PySimpleGUI as sg
import threading
import shutil
import time
import os
import glob
import csv
import psutil
import datetime
from PIL import Image
import stat

class App():

    def __init__(self):
        self.tar_img = ""
        self.tar_dir = ""
        self.save_dir = "C:\\Users\\Y.Kojima\\Pictures"
        self.csv_name = "./memory_log.csv"
        self.copy_flag = False
        self.status = ""
        self.save_span1 = "10" #200M以下
        self.save_span2 = "30" #500M以下
        self.save_span3 = "60" #1GB以下
        self.save_span4 = "120" #1GB以上

        self.max_copy_num = "20000"
        self.delete_count = 10
        self.target_pid = "0"

        column = [
            [sg.Text('MODE1: 同一ファイルのコピーを繰り返す場合は以下を指定',font=('Helvetica', 13))],
            [sg.Input(key='tar_image', size=(30,1), font=('Helvetica', 15)),
            sg.FileBrowse('コピーファイル選択', size=(18,1), font=('Helvetica', 15))],

            [sg.Text('MODE2: フォルダを参照して違うファイルをコピーする場合は以下を指定',font=('Helvetica', 13))],
            [sg.Input(key='tar_dir', size=(30,1), font=('Helvetica', 15)),
            sg.FolderBrowse('コピーフォルダ選択', size=(18,1), font=('Helvetica', 15))],

            [sg.Text('*使わない方のモードはブランクにして下さい。\n(両方選択の場合はMODE1を使用します)',
                     font=('Helvetica', 13))],
            [sg.Text('',font=('Helvetica', 13))],

            [sg.Text('[共通設定]',font=('Helvetica', 15))],
            [sg.Input(self.save_dir, key='save_dir', size=(30,1), font=('Helvetica', 15)),
            sg.FolderBrowse('保存先選択', size=(15,1), font=('Helvetica', 15))],

            [sg.Text('[保存スパン設定]',font=('Helvetica', 15))],

            [sg.Text('ファイル容量200MB以下:',font=('Helvetica', 15)),
             sg.In(self.save_span1, size=(5,5), font=('Helvetica', 15), key='save_span1',justification='right')],

            [sg.Text('ファイル容量200MB-500MB間',font=('Helvetica', 15)),
             sg.In(self.save_span2, size=(5,5), font=('Helvetica', 15), key='save_span2',justification='right')],

            [sg.Text('ファイル容量500MB-1GB間',font=('Helvetica', 15)),
             sg.In(self.save_span3, size=(5,5), font=('Helvetica', 15), key='save_span3',justification='right')],

            [sg.Text('ファイル容量1GB以上',font=('Helvetica', 15)),
             sg.In(self.save_span4, size=(5,5), font=('Helvetica', 15), key='save_span4',justification='right')],

            [sg.Text('最大コピー枚数(枚)',font=('Helvetica', 15)),
             sg.In(self.max_copy_num, size=(5,5), font=('Helvetica', 15), key='max_copy_num',justification='right')],
 
            [sg.Text('ターゲットPID(0なら測定しません)',font=('Helvetica', 15)),
             sg.In(self.target_pid, size=(5,5), font=('Helvetica', 15), key='target_pid',justification='right')],

            [sg.Button('START', size=(15,2), font=('Helvetica', 25)),
             sg.Button('STOP', size=(15,2), font=('Helvetica', 25))],
            
            [sg.Text('ステータス',font=('Helvetica', 20))],
            [sg.In(size=(60,5), font=('Helvetica', 15), key='cur_status')]
            ]
     
        window = sg.Window(title = 'FileCopy v1.2', size=(700,750)).Layout(column)
               
        while True:
            event, values = window.Read(timeout = 200)

            if event == sg.TIMEOUT_KEY:
                window.FindElement('cur_status').Update(self.status)

            if event == 'START':
                self.tar_img = values['tar_image']
                self.tar_dir = values['tar_dir']

                self.save_dir = values["save_dir"]
                self.max_copy_num = values["max_copy_num"]
                self.save_span1 = int(values["save_span1"])
                self.save_span2 = int(values["save_span2"])
                self.save_span3 = int(values["save_span3"])
                self.save_span4 = int(values["save_span4"])

                self.target_pid = int(values["target_pid"])

                if not self.tar_img and not self.tar_dir:
                    self.status = 'コピーソースが見当たりません'

                else:
                    self.status = 'コピー中'
                    self.copy_flag = True
                    threading.Thread(target=self.copy_file, args=(self.tar_img,
                                                                  self.tar_dir)).start()
            
            if event == 'STOP':
                self.copy_flag = False
                self.status = '処理中断しました'

        window.Close()
    
    def copy_file(self, tar_img, tar_dir):
        delete_list = []

        format_list = [".vl"] ##, ".png", ".jpg", ".bmp", ".jpeg"]
        if not tar_dir =="":
            img_list = [p for p in glob.glob("{}\**\*".format(tar_dir), recursive=True) if os.path.splitext(p)[1] in format_list] 

        n = 0
        i = 0
        count_num = 0
        
        while self.copy_flag:

            if tar_img:
                copy_file = "{0}\\{1:04d}_{2:04d}.vl".format(self.save_dir,i, n)  

                if not os.access(tar_img, os.W_OK):
                    os.chmod(tar_img, stat.S_IWRITE)

                time_sta = time.perf_counter()

                shutil.copy(tar_img, copy_file)

                time_end = tie.perf_counter()

                copy_time = time_end - time_sta

                save_span, data_size = self.get_img_size(copy_file)

                self.status = "現在{}枚コピーしました".format(str(count_num))
                self.mem_info_get(os.path.basename(tar_img), data_size, copy_time)

                n += 1
                count_num = i*10000 + n

                time.sleep(int(save_span))

                if n > 1 and n % self.delete_count == 0:
                    threading.Thread(target=self.file_delete, args=[self.delete_count, delete_list]).start()
                    delete_list = []

                if count_num == int(self.max_copy_num):
                    self.status = '最大数に達しました'
                    break

                elif n == 9999:
                    n = -1
                    i += 1

                delete_list.append(copy_file)

            
            elif not tar_dir =="":
                file_name = "{0:05d}_{1}".format(count_num, os.path.basename(img_list[n])) 
                copy_file = os.path.join(self.save_dir, file_name)

                if not os.access(img_list[n], os.W_OK):
                    os.chmod(img_list[n], stat.S_IWRITE)

                time_sta = time.perf_counter()
                
                shutil.copy(img_list[n], copy_file)

                time_end = time.perf_counter()

                copy_time = time_end - time_sta

                save_span, data_size = self.get_img_size(copy_file)

                self.status = "現在{}枚コピーしました".format(str(count_num))
                self.mem_info_get(img_list[n], data_size, copy_time)

                n += 1
                count_num += 1
                
                time.sleep(int(save_span))

                if n > 1 and count_num % self.delete_count == 0:
                    threading.Thread(target=self.file_delete, args=[self.delete_count, delete_list]).start()
                    delete_list = []

                if count_num == int(self.max_copy_num):
                    self.status = '最大数に達しました'
                    break

                delete_list.append(file_name)

                if n == len(img_list):
                    n = 0

    def file_delete(self, delete_count, delete_list):
 
        if len(delete_list) > 0:
            for i in range(len(delete_list)):
                os.remove(os.path.join(self.save_dir, delete_list[i]))


        else:
            for i in range(delete_count):
                os.remove(os.path.join(self.save_dir, files[i]))

    def get_img_size(self, img_dir):
        thre_data1 = 200000000 #200MB
        thre_data2 = 500000000 #500MB
        thre_data3 = 1000000000 #1GB

        data_size = os.path.getsize(img_dir)

        if thre_data2 > data_size >= thre_data1:
            time_span = self.save_span2

        elif thre_data3 > data_size >= thre_data2:
            time_span = self.save_span3

        elif data_size >= thre_data3:
            time_span = self.save_span4

        else:
            time_span = self.save_span1
            
        return time_span, data_size


    def mem_info_get(self, copied_img_name, data_size, copy_time):
        data = []
            
        ##記録時刻取得
        dt = datetime.datetime.now()
        save_time = ['{0:%Y%m%d-%H%M%S}'.format(dt)]
        data.append(save_time)
        data.append([copy_time])

        ##コピーしたファイル名
        data.append([copied_img_name])

        ##コピーしたファイルのデータ容量
        data.append([data_size])

        ##固定PIDメモリ取得(USS)
        current_process = psutil.Process(int(self.target_pid))
        if not self.target_pid == 0:
            data.append([self.target_pid])
            data.append([current_process.memory_full_info().uss])

        ##全メモリ取得
        mem = str(psutil.virtual_memory())[6:-1].split(",")
        data.extend([mem[i]] for i in range(len(mem)))

        ##CSVファイル生成＆データ書き込み
        with open(self.csv_name, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(data)
            #print(data)

#        time.sleep(int(self.save_span))


App()
