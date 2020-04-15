01 專題摘要解釋實作與說明需要解決的問題，限300~500字。
02 實作方法介紹介紹使用的程式碼、模組，並附上實作過程與結果的截圖，需圖文並茂。
03 成果展示介紹成果的特點為何，並撰寫心得。
04 結論總結本次專題的問題與結果。


## purpose : Ptt
1.  八卦版：https://www.ptt.cc/bbs/Gossiping/index.html
2.  政黑板：https://www.ptt.cc/bbs/HatePolitics/index.htmlPtt


## 期末專題實作提示 (基本目標)
TARGET 1 爬下文章，透過 jieba 等斷詞將文章拆解
link: 
```
https://medium.com/pyladies-taiwan/%E8%87%AA%E7%84%B6%E8%AA%9E%E8%A8%80%E8%99%95%E7%90%86%E5%85%A5%E9%96%80-word2vec%E5%B0%8F%E5%AF%A6%E4%BD%9C-f8832d9677c8
http://nccur.lib.nccu.edu.tw/bitstream/140.119/78817/1/101201.pdf
```
TARGET 2 可以簡單的計算同樣文字出現的頻率或是透過 TFIDF 的統計方式計算
```
https://taweihuang.hpd.io/2017/03/01/tfidf/
https://medium.com/@chih.sheng.huang821/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92%E6%87%89%E7%94%A8-%E5%9E%83%E5%9C%BE%E8%A8%8A%E6%81%AF%E5%81%B5%E6%B8%AC-%E8%88%87-tf-idf%E4%BB%8B%E7%B4%B9-%E5%90%AB%E7%AF%84%E4%BE%8B%E7%A8%8B%E5%BC%8F-2cddc7f7b2c5
```
TARGET 3 將經常出現的 stop words 過濾掉之後對頻率進行排名


TARGET 4 將結果透過 wordcloud 文字雲的方式呈現


## 期末專題實作提示  (進階目標)

TARGET 1 透過不同帳號，但是相同 IP 且政治用語的詞頻分佈類似的定位成網軍
TARGET 2 進一步分析帳號是否在特定期間 (e.g. 選舉) 有明顯的活動特性
TARGET 3 如果不同帳號但是政治用語的詞頻分佈類似，進一步判斷這些高頻率的單字是positive / negative 來歸納兩個帳號之間是否具有相同政治立場


https://www.cupoy.com/clubnews/ai_tw/0000016E62FB84E4000000026375706F795F72656C656173654B5741535354434C5542/0000017071B527300000009F6375706F795F72656C656173654B5741535354434C55424E455753