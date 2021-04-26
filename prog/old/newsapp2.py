from tkinter import *
from tkinter import ttk
import tkinter
from jbayes import BayesianFilter
from bs4 import BeautifulSoup
import requests
import urllib.request as req
import csv
import wikipedia
import webbrowser
import re
import MeCab

#ニュース取得
def itGet_News():
	url = "https://www.itmedia.co.jp/news/subtop/ranking/"
	res = requests.get(url)
	content = res.content
	soup = BeautifulSoup(content, "html.parser")
	articletitles = soup.find_all('div', class_='colBoxIndexRight')
	urllist = []
	newslist = []
	
	for articletitle in articletitles:
		url = articletitle.a["href"]
		news = articletitle.h3.string
		urllist.append(url)
		newslist.append(news)

	return urllist, newslist

#ニュース取得
def sceGet_News():
	url = "https://bio.nikkeibp.co.jp/"
	res = requests.get(url)
	content = res.content
	soup = BeautifulSoup(content, "html.parser")
	articletitles = soup.find_all("p", class_ = "title")
	urllist = []
	newslist = []
	 
	for articletitle in articletitles:
		if articletitle.string is not None:
			url = "https://bio.nikkeibp.co.jp/" + articletitle.a["href"]
			news = articletitle.string
			urllist.append(url)
			newslist.append(news)

	return urllist, newslist

#タグ付け
def itTagging(newslist):
	stucsvfile = "../data/itnews.csv"
	f1 = open(stucsvfile, "r")
	reader = csv.reader(f1)
	bf = BayesianFilter()
	taglist = []
	#教師データで学習
	for row in reader:
		bf.fit(row[0],row[1])
	#ニュースに対してタグ付け
	for news in newslist:
		#AIが入っていたら確定でAIのニュース
		regex = r".+AI"
		pattern = re.compile(regex)
		matchObj = pattern.match(news)
		pre, scorelist = bf.predict(news);
		if matchObj is not None:
			taglist.append("AI")
		else:
			taglist.append(pre)

	return taglist

#タグ付け
def sceTagging(newslist):
	stucsvfile = "../data/scenews.csv"
	f1 = open(stucsvfile, "r")
	reader = csv.reader(f1)
	bf = BayesianFilter()
	taglist = []
	#教師データで学習
	for row in reader:
		bf.fit(row[0],row[1])
	#ニュースに対してタグ付け
	for news in newslist:
		pre, scorelist = bf.predict(news);
		taglist.append(pre)
	return taglist

def getpat():
	with open("../data/studata.txt") as f:
		infile = f.read()
	mecab = MeCab.Tagger("")
	node = mecab.parseToNode(infile)
	#品詞のリスト
	stcashlst = []
	#品詞の詳細のリスト
	stprecashlst  = []
	#言葉のリスト
	stwordlst = [] 
	stchecklst = []

	while node:
		stcashlst.append(node.feature.split(",")[0])
		stprecashlst.append(node.feature.split(",")[1])
		stwordlst.append(node.surface)
		node = node.next

	for i,cash in enumerate(stcashlst):
		if cash == "助詞":
			#助詞なら助詞＋品詞の詳細をリストに保存
			stchecklst.append(stwordlst[i] + stprecashlst[i+1])

	return stchecklst

def testpat(stchecklst):
	EditValue = EditBox2.get()
	#品詞のリスト
	incashlst = []
	#品詞の詳細のリスト
	inprecashlst  = []
	#言葉のリスト
	inwordlst = [] 
	inchecklst = []
	wordlst = []
	checklst = []

	mecab = MeCab.Tagger("")
	node = mecab.parseToNode(EditValue)
	while node:
		incashlst.append(node.feature.split(",")[0])
		inprecashlst.append(node.feature.split(",")[1])
		inwordlst.append(node.surface)
		node = node.next
	
	for i,cash in enumerate(incashlst):
		if cash == "助詞" and inprecashlst[i+1] != "*":
			inchecklst.append(inwordlst[i] + inprecashlst[i+1])
			wordlst.append(inwordlst[i-1] + inwordlst[i] + inwordlst[i+1])

	for i,incheck in enumerate(inchecklst):
		if incheck not in stchecklst:
			checklst.append(wordlst[i])

	if len(checklst) == 0:
		checklst.append('ミスはありませんでした。') 

	return checklst

# ボタンクリックイベント
def Btn1_Click():
	#新しい画面をsub_winという名前で生成する
	sub_win1 = Toplevel()
	sub_win1.geometry('800x500')
	sub_win1.title('マッチしたニュース')
	num = tagrdo_var.get()
	if num % 2 == 0:
		#urlとニュース取得
		urllist, newslist = itGet_News()
		#タグ付与
		taglist = itTagging(newslist)
	if num % 2 == 1:
		#urlとニュース取得
		urllist, newslist = sceGet_News()
		#タグ付与
		taglist = sceTagging(newslist)

	anslist = []
	murllist = []

	for i,tag in enumerate(taglist):
		if tag == tagrdo_txt[num]:
			anslist.append(newslist[i] + '\n')
			murllist.append(urllist[i] + '\n')

	if len(anslist) == 0:
		res_word = 'マッチするニュースがありませんでした。'
		sublabel1 = tkinter.Label(sub_win1,text = res_word, font = ('メイリオ',15))
		sublabel1.place(x = 230, y = 250)
	else:
		sublabel2 = tkinter.Label(sub_win1,text = str(len(anslist)) + '件のニュースがマッチしました。\n', font = ('メイリオ',13))
		sublabel2.place(x = 0, y = 0)
		ans_var = tkinter.IntVar()
		ans_var.set(0)
		for i in range(len(anslist)):
			ans = tkinter.Radiobutton(sub_win1, value = i, variable = ans_var, text = anslist[i], font = ('メイリオ',10))
			ans.place(x = 20, y = 30 + (i * 27))

	subbutton1 = ttk.Button(
		sub_win1,
		text = 'ニュースを見る',
		width = str('ニュースを見る'),
		command = lambda: Btn3_Click(ans_var.get(),murllist)
		)
	subbutton1.place(x = 350, y = 500)

def Btn2_Click():
	sub_win2 = Toplevel()
	sub_win2.geometry('500x200')
	sub_win2.title('単語検索結果')
	wikipedia.set_lang('ja')
	EditValue = EditBox1.get()
	#検索した結果をいれる
	try:
		search_response = wikipedia.search(EditValue)
		if not search_response:
			res_word = ["その単語はwikipedia内に存在しませんでした"]
		else:
			res_word = wikipedia.summary(EditValue)
	except:
		res_word = ["その単語はwikipedia内に存在しませんでした"]

	txtbox = tkinter.Text(sub_win2, width=200, height=50)
	res_word = res_word.split("。")

def Btn3_Click(num,murllist):
	webbrowser.open(murllist[num])	 

def Btn4_Click():
	stchecklst = getpat()
	checklst = testpat(stchecklst)
	#新しい画面をsub_winという名前で生成する
	sub_win3 = Toplevel()
	sub_win3.geometry('400x200')
	sub_win3.title('文法ミス?')
	txtbox = tkinter.Text(sub_win3, width=200, height=50)
	for check in checklst:
		txtbox.insert('1.0',check)
		txtbox.pack()

# Tkクラス生成
root = Tk()
# 画面サイズ
root.geometry('800x500')
# 画面タイトル
root.title('ニュース紹介')

#ラベル作成
label1 = ttk.Label(text = 'ニュース紹介をするアプリです このアプリで知識を蓄えて面接の対策をしましょう', font = ('メイリオ', 15))
label1.place(x = 20, y = 0)
label2 = ttk.Label(text = 'ニュースを調べて面接時の質問に答えられるようにしましょう', font = ('メイリオ', 15))
label2.place(x = 120, y = 30)
label3 = ttk.Label(text = 'IT関係', font = ('メイリオ', 13))
label3.place(x = 100, y = 60)
label4 = ttk.Label(text = '化学関係', font = ('メイリオ', 13))
label4.place(x = 500, y = 60)
seplabel1 = ttk.Label(text = '-' * 95, font=("メイリオ", 13))
seplabel1.place(x = 70, y = 220)
label5 = ttk.Label(text = 'ニュースで分からなかった単語について調べて深く話せるようにしましょう', font = ('メイリオ', 15))
label5.place(x = 70, y = 250)
seplabel1 = ttk.Label(text = '-' * 80, font=("メイリオ", 13))
seplabel1.place(x = 120, y = 360)
label6 = ttk.Label(text = 'ニュースに対しての意見をアウトプットしてみましょう。', font = ('メイリオ', 15))
label6.place(x = 150, y = 380)

# ラジオボタンのラベルをリスト化する
tagrdo_txt = ['AI','医療','ネットワーク・セキュリティ','食品・農業','ソフトウェア・ハードウェア']

# ラジオボタンの状態
tagrdo_var = tkinter.IntVar()

#itのジャンルラジオボタンを動的に作成して配置
for i in range(len(tagrdo_txt)):
    tagrdo = tkinter.Radiobutton(root, value = i, variable = tagrdo_var, text = tagrdo_txt[i], font = ('メイリオ', 10))
    if i % 2 == 0:
    	tagrdo.place(x = 100, y = 90 + (i * 12))
    else:
    	tagrdo.place(x = 500, y = 90 + (i * 12) - 12)

# ボタン作成 
btn1 = tkinter.Button(root, text = 'ニュース記事取得', command = Btn1_Click, font = ('メイリオ',10))
btn1.place(x = 330, y = 180)
btn2 = tkinter.Button(root, text = '単語検索', command = Btn2_Click, font = ('メイリオ', 10))
btn2.place(x = 360,  y = 330) 
btn4 = tkinter.Button(root, text = '文法チェック', command = Btn4_Click, font = ('メイリオ', 10))
btn4.place(x = 350,  y = 450) 

#Entryの作成
EditBox1 = ttk.Entry()
EditBox1.place(x = 330, y = 300)
EditBox2 = ttk.Entry()
EditBox2.place(x = 180, y = 420, width = 450)

#プログラムの実行
root.mainloop()