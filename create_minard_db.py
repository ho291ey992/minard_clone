import re
import pandas as pd
import sqlite3

class CreateMinardDB:
    def __init__(self):
        with open("練習專案二：拿破崙征俄戰爭/data/minard.txt") as f:
            lines = f.readlines()
        self.lines = lines
        self.column_names = lines[2].split()
        # 使用 map() 清理所有元素，使用pd原因在於未來如果有大量數據時效能比較好。
        # cleaned_columns = [re.sub(r'\W+', '', col) for col in column_names] 這也是可以的。
        self.column_names_cleaned = pd.DataFrame({"name":self.column_names}).map(lambda x: re.sub(r'\W+', '', x))

    def creata_city_df(self):
        # city
        column_names_city = list(self.column_names_cleaned.name[:3])  # 載入"資料列名稱"
        longitudes, latitudes, cities = [], [], []  # 建立暫時儲存資料list
        for df in self.lines[6:26]: # 經過觀察"資料外觀後"，得知道city資料在[列:0~3,行:6~26]
            long, lat, city = df.split()[:3] # 暫存資料：由於資料屬於 txt 檔切割字串，提取前3個欄位（經度、緯度、城市名稱）。
            longitudes.append(float(long)) # 加入資料：原始資料為文字檔，經度轉換為浮點數並存入。
            latitudes.append(float(lat)) # 加入資料：原始資料為文字檔，緯度轉換為浮點數並存入。
            cities.append(city) # 加入資料

        city_data = (longitudes, latitudes, cities) # 將 3 個 list 合併為 tuple
        # 一開始我是好奇為什麼不是用list，查後發現好處還不少。
            # 1.資料安全性：Tuple 是不可變（Immutable）的，防止後續誤修改
            # 2.效能更好：在 zip() 時，Tuple 能提供更快的索引存取，在不需要修改內容的情況下，效能優於 List。
            # 3.內存管理：Tuple 佔用的內存通常比 List 少，當需要處理大量數據時，這能節省資源。
        # 總結：Tuple 適用於固定內容且不需要修改的情境，而 List 更適合可變數據。這裡的 city_data 是一組固定的數據組合，因此用 Tuple 會更好！
        
        # 建立空的 DataFrame，準備填入整理後的數據
        city_df = pd.DataFrame()
        # 將 city_data 的內容對應到相應的欄位名稱
        for column_name, data in zip(column_names_city, city_data):
            city_df[column_name] = data # 設定 DataFrame 的對應欄位數據
        return city_df # 返回處理完畢的 DataFrame
    
    def creata_temperature_df(self):
        # temp
        column_names_temp = list(self.column_names_cleaned.name[3:7])
        lontvalues, tempvalues, days, dates = [], [], [], []
        for df in self.lines[6:15]:
            lont, temp, day  = df.split()[3:6]
            lontvalues.append(float(lont))
            tempvalues.append(int(temp))
            days.append(int(day))
            if day == "10":
                dates.append("Nov 24")
            else:
                dates.append(df.split()[6] +" "+df.split()[7])

        temp_data = (lontvalues, tempvalues, days, dates)
        temperature_df = pd.DataFrame()
        for column_name, data in zip(column_names_temp, temp_data):
            temperature_df[column_name] = data
        return temperature_df
    
    def create_troop_df(self):
        # troop
        column_names_troop = list(self.column_names_cleaned.name)[-5:]
        lonp_values, latp_values, surviv_values, direc_values, division_values = [], [], [], [], []
        for df in self.lines[6:-3]:
            lonp, latp, surviv, direc, division = df.split()[-5:]
            lonp_values.append(float(lonp))
            latp_values.append(float(latp))
            surviv_values.append(int(surviv))
            direc_values.append(direc)
            division_values.append(int(division))

        troop_data = (lonp_values, latp_values, surviv_values, direc_values, division_values)
        troop_df = pd.DataFrame()
        for column_name, data in zip(column_names_troop, troop_data):
            troop_df[column_name] = data
        return troop_df
    
    def create_database(self):
        # 載入資料
        city_df = self.creata_city_df()
        temperature_df = self.creata_temperature_df()
        troop_df = self.create_troop_df()

        # 建立 SQLite
        connection = sqlite3.connect("練習專案二：拿破崙征俄戰爭/minard_clone/data/minard.db")
        df_dict = {
            "cities": city_df,
            "temperatures": temperature_df,
            "troops": troop_df
        }
        for k, v in df_dict.items():
            v.to_sql(name=k, con=connection, index=False, if_exists="replace") 
            # v.to_sql(name=資料表名稱, con=檔案位置, index=是否載入 pd 排序, if_exists="replace" 若同名檔案存在覆蓋) 
        connection.close()

create_minard_db = CreateMinardDB()
create_minard_db.create_database()
