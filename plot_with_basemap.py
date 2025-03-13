from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

class plot_minard_map():
    def __init__(self):
        connection = sqlite3.connect("練習專案二：拿破崙征俄戰爭/minard_clone/data/minard.db")
        self.city_df = pd.read_sql("""select * from cities;""", con=connection)
        self.temperature_df = pd.read_sql("""SELECT * FROM temperatures;""", con=connection)
        self.troop_df = pd.read_sql("""SELECT * FROM troops;""", con=connection)
        connection.close()
    
    # 繪製axes[0]圖層0:繪製城市地圖
    def city(self):
        lons = self.city_df['lonc'].values
        lats = self.city_df['latc'].values
        city_names = self.city_df['city'].values
        
        # 創造畫布和軸物件
            # nrows=2：表示有兩個圖層（兩個子圖）。
            # figsize=(25,12)：設定整個圖的大小，確保顯示效果清晰。
            # gridspec_kw={"height_ratios": [4, 1]}：代表第一個圖層的高度是第二個的 4 倍，因此第一個圖層比較大，第二個比較小
        self.fig, self.axes = plt.subplots(nrows=2, figsize=(25,12), gridspec_kw={"height_ratios": [4, 1]})

        # 插入標題
        self.axes[0].set_title("Napoleon's disastrous Russian campaign of 1812", loc="left", fontsize=30)

        # 建立地圖：
            # projection="lcc": Lambert Conformal.
            # resolution="i": 解析度為中階（intermediate）
            # width=1000000: 地圖寬度為 100 萬公尺（1000 公里）
            # height=400000: 地圖高度為 40 萬公尺（400 公里）
            # lon_0=31, lat_0=55: 地圖的中心經緯度為 (31, 55)
            # ax=axes[0]：指定在圖層0
        self.m = Basemap(projection="lcc", resolution="i", width=1000000, height=400000, lon_0=31, lat_0=55, ax=self.axes[0])

        # 繪製國家邊界
        self.m.drawcountries() 

        # 繪製河流
        self.m.drawrivers() 

        # 標記經緯度線 (labels使用的是"布林"，設置順序[左、右、上、下])
        self.m.drawparallels(range(54,58), labels=[1,0,0,0]) # 左邊顯示緯度標籤
        self.m.drawmeridians(range(23, 56, 2), labels=[0,0,0,1]) # 下方顯示經度標籤

        # 映射轉換： 將經緯度轉換為 Basemap 的相對座標
        x_c, y_c = self.m(lons, lats) 

        # 添加城市名稱標籤
        for xi, yi, city_name in zip(x_c, y_c, city_names): 
            self.axes[0].annotate(text=city_name, xy=(xi, yi), fontsize=10, ha="right", zorder=2)  
            # ha="right" 讓標籤靠右對齊，避免重疊
            # zorder=2 圖層：確保文字位於上層，不會被其他圖層覆蓋。
    
    # 繪製axes[0]圖層0:繪製軍隊圖
    def troop(self):
        # 取得軍隊行進路線的資料筆數
        rows = self.troop_df.shape[0]

        # 讀取經度、緯度、存活人數、行進方向
        lons = self.troop_df["lonp"].values # 軍隊的經度
        lats = self.troop_df["latp"].values # 軍隊的緯度
        survivals = self.troop_df["surviv"].values # 軍隊存活人數
        directions = self.troop_df["direc"].values # 軍隊行進方向

        # Basemap 座標轉換：lons, lats 是原始的 GPS 經緯度座標，透過 self.m(lons, lats) 轉換成 Basemap 的平面地圖座標 (x_t, y_t)
        x_t, y_t = self.m(lons, lats)

        for i in range(rows - 1):
            # 設定行進方向的顏色
            if directions[i] == "A":
                line_color = "tan"
            else:
                line_color = "black"
            
            # 設定起點與終點的 x, y 座標
            start_stop_lons = (x_t[i], x_t[i + 1])
            start_stop_lats = (y_t[i], y_t[i + 1])

            # 設定線條寬度：存活人數越多，線條越粗，以視覺化表達軍隊人數變化。
            line_width = survivals[i]  # 取得存活人數

            # 繪製路線-折線圖
            self.m.plot(start_stop_lons, start_stop_lats, linewidth=line_width/10000, color=line_color, zorder=1)
            # 設定線條粗細
                # line_width = survivals[i] 代表當下軍隊的存活數量。
                # linewidth=line_width/10000，將數值縮小，使線條寬度對應軍隊數量。
            # `zorder=1` 圖層：將軍隊行進路線放在較低圖層，確保不會覆蓋城市標籤或溫度標記。

    # 繪製axes[1] 圖層1:繪製氣溫圖
    def temperature(self):
        # 原始資料採用「列氏」溫度，跟攝氏溫度的轉換公式如下
        temp_celsius = (self.temperature_df["temp"] * 5/4).astype(int)

        # 經度
        lons = self.temperature_df["lont"].values

        # temp_celsius（轉換後的攝氏溫度）轉為 "溫度°C 月 日"字串
        annotations = temp_celsius.astype(str).str.cat(self.temperature_df["date"], sep="°C ")
        # Series.str.cat(others=None, sep='', na_rep=None)
            # others：要合併的資料（可為 DataFrame、Series、list）
            # sep：字串間的分隔符號（預設為 ''，即無分隔符）
            # na_rep：缺失值（NaN）的填充值（預設為 None，即跳過 NaN）

        # 折線圖
        self.axes[1].plot(lons, temp_celsius, linestyle="dashed", color="black")
            # linestyle：設定線外觀 dashed 為虛線
            # color：設定顏色

        # 插入文字
        for lont, temp_c, annotation in zip(lons, temp_celsius, annotations):
            self.axes[1].annotate(annotation, xy=(lont - 0.3, temp_c - 7), fontsize=16)
                 # 調整文字位置，使標籤稍微往左 (lont -0.3)，往下 (temp_c -7) 避免重疊
                 
        # 設定 Y 軸範圍（從 -50°C 到 10°C）
        self.axes[1].set_ylim(-50, 10)

        # ax.spines 移除邊框
        self.axes[1].spines["top"].set_visible(False)
        self.axes[1].spines["right"].set_visible(False)
        self.axes[1].spines["bottom"].set_visible(False)
        self.axes[1].spines["left"].set_visible(False)

        # 啟用主要格線，使氣溫變化更清晰
            # which：magor顯示主要格線
            # axis：xy都顯示
        self.axes[1].grid(True, which="major", axis="both")
            
        # set_xticklabels([]) 讓刻度標籤變空，若是直接 set_xticks([]) 刪除標籤，會倒置 "主要格線" 無法繪製。
        self.axes[1].set_xticklabels([])
        self.axes[1].set_yticklabels([])

        # 自動調整子圖之間的間距，避免標題或標籤重疊
        plt.tight_layout()
    
    # 輸出
    def minard_map(self):
        self.city()
        self.troop()
        self.temperature()

        # 儲存圖片
        self.fig.savefig("練習專案二：拿破崙征俄戰爭/minard_clone/minard_clone.png" )

plot_minard = plot_minard_map()
plot_minard.minard_map()
