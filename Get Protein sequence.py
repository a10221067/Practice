import tkinter as tk
import tkinter.messagebox
import pandas as pd
import requests
import os
import bs4
import re

def find():
    BA =[]
    if (B1.get() != ''):
        B2 = B1.get()
        BA.append(B2)

    for i in range(len(CU)+1):     #將所有 keyword 放入array
        if i == len(CU) and GE.get() != '':     
            BA.append(GE.get())
        elif (i == len(CU)):
            BA = BA
        else:
            if CK[i].get() == True:     #將可選擇勾選框內容作為 keyword，並放入array中
                BA.append(CU[i])

    if len(BA) > 0 and BA[0] != '':     #辨認有沒有 keyword，如果沒有就沒辦法搜尋 --> Check point
        for i in range(len(BA)):     
            if GE.get() != '':     #有基因 
                if len(BA) == 1:     #只有基因
                    name = BA[i]
                    url = 'https://www.uniprot.org/uniprot/?query=%s&offset=0&limit=250' % name
                else:     #有基因，有菌種
                    if i < len(BA)-1:
                        name = BA[i]+'+'+BA[len(BA)-1]
                        url = 'https://www.uniprot.org/uniprot/?query=%s&offset=0&limit=250' % name
                    if len(BA) == 2 and i == 1:     #如果只有各一個基因和菌種，避免再次迴圈
                        break

            else:     #沒基因，僅有菌種
                name = BA[i]
                url = 'https://www.uniprot.org/uniprot/?query=%s&offset=0&limit=250' % name

            try:
                requests.get(url).raise_for_status()
                print('成功載入 DATAbase...')
                print(url)     #url是 key word 輸入後進入的 database 網站
                
            except Exception as err:
                print("網頁下載失敗: %s" % err)         

            else:          
                df = pd.read_html(url)[0]     #將 data 以 DataFrame 讀取出來
                df = df[["Organism","Protein names","Entry"]]     #選擇需要的資料
                df.insert(df.shape[1],'Sequence',"")     #建立一個新的 column，給後面取到的 data 放

                for i in range(len(df.Entry)):     #利用抓到的 ID，在去抓其內容
                    url2 = 'https://www.uniprot.org/uniprot/%s' % df.Entry[i]
                    try:
                        requests.get(url2).raise_for_status()
                        print('成功載入目標資料庫...')
                        print(url2)
                    except Exception as err:
                        print("網頁下載失敗: %s" % err)         

                    else:    
                        htmlFile = requests.get(url2).content
                        way = bs4.BeautifulSoup(htmlFile, 'lxml')
                        tag = way.select('pre.sequence')     
                        SEQ = re.sub("[^A-Z]",'',str(tag))     #所需要的 data 都是大寫英文，把不是的去掉
                        df.Sequence[i] = SEQ

                writer = '%s/%s.xls' % (path,name)     #將取到的 data 輸出成 Excel format
                df.to_excel(writer)
                
                tk.messagebox.showinfo("通知","目標資料已取得完畢\n請看OUTPUT檔")
                
    else:     #辨認有沒有 key word，如果沒有就沒辦法搜尋 --> Check point
        tk.messagebox.showwarning("警告","沒有輸入內容無法查詢！")
    

def mkdir(path):     #為這個程式要輸出的資料做新的資料夾
    folder = os.path.exists(path)
    
    if not folder:
        os.makedirs(path)
    
window = Tk()

window.title("特定蛋白質搜尋")
window.geometry("400x400")
window.resizable(0,0)

frame1 = Frame(window)
frame2 = Frame(window)

B1 = StringVar()     #輸入菌種
GE = StringVar()     #輸入基因

label1 = Label(frame1,text="菌種：",bg='yellow',font="標楷體 16 bold").pack(side=LEFT)
entry1 = Entry(frame1,textvariable=B1,bd=3).pack(side=LEFT)

label2 = Label(frame2,text="基因：",bg='yellow',font="標楷體 16 bold").pack(side=LEFT)
entry2 = Entry(frame2,textvariable=GE,bd=3).pack(side=LEFT)

lbf1 = LabelFrame(window,text="使用常用的?",cursor='circle',font="標楷體 12")

CU = {0:"Escherichia+coli",1:"Salmonella"}
CK = {}

for i in range(len(CU)):
    CK[i] = BooleanVar()
    Checkbutton(lbf1,text=CU[i],variable=CK[i],font="Verdana 10").pack()
    
frame1.pack(side=TOP,pady=15)
lbf1.pack(side=TOP,pady=15)
frame2.pack(side=TOP,pady=15)

button = Button(window,text="查詢",width=15,height=15,command=find,bg='red',font="標楷體 16 bold",fg='white')
button.pack(side=TOP,pady=15)

window.mainloop()

global path
path = 'd:\\Python\\Find_gene_information'     #指定電腦硬碟位置，後面用於存放 output檔
mkdir(path)
