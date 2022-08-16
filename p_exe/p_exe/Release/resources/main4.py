'''

添加句长相似度
三个因素

'''
from lib.preprocess import *
from lib.Similarity import *
from lib.Keyword import *
import numpy as np
import math


def Review(s1,s2,total):#打分算法
    '''
    计算句长
    句长相似度
    '''
    lens1=len(s1)
    lens2=len(s2)
    if lens1<lens2:
        Sa4=1
    else:
        Sa4=1-abs((lens1-lens2)/(lens1+lens2))

    #print("lens1",lens1)
    #print("lens2", lens2)
    #print("Sa4", Sa4)



    #分类ture:A,false:B
    '''
   
    先根据这几个词分类：”包括、内容、优点、缺点、优缺点、特点、特征、分为“
    句子包含上述词为A类，不包含为B类。
    然后若句子中只有“、”或者只有“；” 定义为A类
    目的是：分点答的句子，语义相似度同样重要，并且权重稍高于关键词
    '''
    #s1=货架可以分为固定货架和移动货架。
    CLASS = classification(s1)
    #print("CLASS", s1)
    # s1=货架可以分为固定货架和移动货架。
    #predone处理 (答案预处理)
    [s1,flag1] = predone1(predone(s1))
    #print("predone1", s1)
    # s1=固定货架和移动货架。
    if onlyAorB(s1):
        CLASS = "A"
    s2 = predone(s2)

    #预处理 level表示层次set表示层级
    #预处理后的词对数组,否定词个数,分层层级

    #关键词提取
    # key_words = KEYWORD(problem,s1)
    # flag1为是否有缩短原句，true为缩短过。即对含破折号、分号、以及标记的句子进行处理过
    key_words = KEYWORD2(s1,flag1)
    #print("关键词：",key_words)
    count_key = len(key_words)

    #print("KEYWORD2", s1)
    #s1=固定货架和移动货架。

    #关系词对预处理
    #print("Preprocessing3",s1)
    [set1,count1] = Preprocessing3(s1)
    #print("set1",set1)
    #print("count1",count1)

    #若该标准答案的句法关系只有并列关系，重置之前的题目分类，并新定义为C类题目。
    flag2 = True
    for item in set1:
        if item["DEPREL"]!="并列关系":
            flag2 = False
    if flag2:
        CLASS = "C"

    [set2, count2] = Preprocessing3(s2)
    # print("否定词个数：",count1,count2)

    #相似矩阵
    omega1 = 0.5 #依存词的权重
    omega2 = 0.5 #核心词的权重  omega1+omega2 = 1

    '''
    s1:健康相关行为：是指有助于个体在生理、心理和社会上保持良好状态、预防疾病的行为。它与健康信念密切相关，是个体为维持、实现、重建健康和预防疾病的活动。
    s2:健康相关行为：是指有助于个体对于生理、心理和社会上保持良好状态，预防疾病的行为。
    '''
    #print("set1",set1)
    #print("set2",set2)

    #for i in set1:
    #    print(i)
    #print()
    #for i in set2:
    #    print(i)


    m = len(set1)#标准答案的长度
    k = len(set2)#学生答案的长度
    #print("m",m)
    #print("k",k)
    N = np.zeros((m,k))#相似矩阵
    #print("N",N)
    for i in range(m):
        for j in range(k):
            A = similar(set1[i]['LEMMA'],set2[j]['LEMMA'])#依存词相似度
            B = similar(set1[i]['HEAD.LEMMA'],set2[j]['HEAD.LEMMA'])#核心词相似度
            if set1[i]['DEPREL'] == "并列关系" and set2[j]['DEPREL'] == "并列关系":
                temp_A = similar(set1[i]['LEMMA'],set2[j]['HEAD.LEMMA'])
                temp_B = similar(set1[i]['HEAD.LEMMA'],set2[j]['LEMMA'])
                # 相加
                N1 = isConsistent(set1[i]['DEPREL'],set2[j]['DEPREL'])*(omega1*A+omega2*B) # isConsistent判断关系是否相同
                N2 = isConsistent(set1[i]['DEPREL'],set2[j]['DEPREL'])*(omega1*temp_A+omega2*temp_B)
                N[i,j] = max(N1,N2)
            else:
                # 相乘
                if set1[i]['LEMMA'] not in key_words:
                    A = A/2+0.5
                if set1[i]['HEAD.LEMMA'] not in key_words:
                    B = B/2+0.5
                N[i,j] = isConsistent(set1[i]['DEPREL'],set2[j]['DEPREL'])*(A*B)

    # print(N)
    #评分算法----获得单词对的最大相似度组合
    # theta = 0.5 #相似矩阵中大于theta的值才算有效(相加)0.6
    theta = 0.4 #相似矩阵中大于theta的值才算有效(相乘)0.0001,0.05,0.1
    # print(N)
    Nmax = []
    Nmax_set1 = []
    Nmax_set2 = []
    '''
    N的大小是m*k
    m是set1的行数
    k是set2的行数
    '''
    while True:
        if N.shape[0]==0 or N.shape[1]==0 or N.max()<theta:
            break
        else:
            # Nmax.append(N.max())
            row = np.where(N==N.max())[0][0]# 最大值的行
            col = np.where(N==N.max())[1][0]# 最大值的列

            Nmax.append(N[row][col]) # 取矩阵𝑁(𝑆1,𝑆2)中最大的元素作为有效语义相似元素
            Nmax_set1.append(set1[row]) # 取出标准答案  与学生相似度最大的行
            Nmax_set2.append(set2[col]) #取出学生答案 与标准的相似度最大的行
            #print("关系词对相似度:",N[row][col])
            #print("标准",set1[row])
            #print("学生",set2[col])
            '''
            由于以后会继续取最大的相似度
            所以将已经取出的最大的相似度所在的set1,set2对应的行删掉，将N对应的行，列删掉。
            '''
            set1.pop(row)
            set2.pop(col)
            #删除𝑁(𝑆1,𝑆2)中它的行和列
            N = np.delete(N,row,axis = 0)
            N = np.delete(N,col,axis = 1)

    # 语义相似度
    p = 0.2  # [0,1]
    t = 1  # [1,+inf]
    i = len(Nmax)
    # print(m,k,i,p)
    #计算beta
    beta = 0
    if 2 * i / (m + k) >= p:
        beta = math.exp((2 * i / (m + k) - 1) / t)
    else:
        beta = (math.exp((p - 1) * t) / p) * (2 * i / (m + k))

    if i == 0:
        Sa2 = 0
    else:
        Sa2 = beta * sum(Nmax) / i

    # print(beta)
    # print(sum(Nmax))
    ##########################
    ##########################
    ##########################

    #关键词相似度
    Sa1 = 0
    # for sim in key_words_sim:
    #     if sim>=0.3:###############################大于某个值才有效
    #         Sa1=Sa1+sim
    # 学生答案分词：
    [set3, count3, level3] = Preprocessing2(s2)  # 学生答案（对学生答案去标点符号，对词赋权）
    student_words = Participle(set3)  # 单纯分词（将句法分析分词的容器进行转变）
    # print(key_words)
    # 补充关键词相似度
    # if len(key_words)!=0:
    for word in key_words:
        max_word = ""
        max_sim = 0
        for s_word in student_words:
            sim = similar(word, s_word)
            # print(sim,word,s_word)
            if sim > max_sim:
                max_sim = sim
        if max_sim > 0.7:  #######################################大于某个值才有效
            Sa1 = Sa1 + max_sim

    if count_key != 0:
        Sa1 = Sa1 / count_key  # count_key = len(key_words)
    else:
        Sa1 = 0

    '''
    # print(key_words)
    ##########################
    ##########################
    Sa3_sim = []# 核心语义
    ##########################
    ##########################
    ##########################


    # 关键词相似度计算
    # key_words_sim = []
    student_key_words = []
    for i in range(0,len(Nmax))[::-1]:
        flag = False
        if Nmax_set1[i]['LEMMA'] in key_words:  #标准答案里与学生答案相似度高的词，如果在关键词内
            flag = True
            student_key_words.append(Nmax_set1[i]['LEMMA'])
            # key_words.remove(Nmax_set1[i]['LEMMA'])
            # key_words_sim.append(similar(Nmax_set1[i]['LEMMA'],Nmax_set2[i]['LEMMA']))
        if Nmax_set1[i]['HEAD.LEMMA'] in key_words: ##标准答案里与学生答案相似度高的词的核心词，如果在关键词内
            flag = True
            student_key_words.append(Nmax_set1[i]['HEAD.LEMMA'])
            # key_words.remove(Nmax_set1[i]['HEAD.LEMMA'])
            # key_words_sim.append(similar(Nmax_set1[i]['HEAD.LEMMA'],Nmax_set2[i]['HEAD.LEMMA']))
        if flag:
            # print(i,Nmax[i])
            Sa3_sim.append(Nmax[i])   # 与标准答案关键词（在Nmax_set1[i]中）相似度高的词的（矩阵𝑁(𝑆1,𝑆2)中最大的元素作为）有效语义相似元素作为关键词相似度
    student_key_words  = list(set(student_key_words)) # set是一个不允许内容重复的组合，而且set里的内容位置是随意的，所以不能用索引列出。


    ##########################
    ##########################
    ##########################

    # 核心语义相似度
    Sa3 = 0
    for s in Sa3_sim:
        Sa3 = Sa3+s
    if Sa3!=0:
        Sa3 = Sa3/len(Sa3_sim)

    if len(key_words)==0:
        Sa3 = 0
        CLASS = "D"
    else:
        Sa3 = Sa3*len(student_key_words)/len(key_words)
    
    # print(i,m,k,beta,Sa)
    
    '''


    if CLASS == "A":#0.33 0.47
        if Sa4<0.75:
            pa1 = 0.33*0.5
            pa2 = 0.47*0.5
            #pa3 = 0
            pa4 = 0.5/2 #目的让Sa4*pa4*10变成Sa4*pa4*10*0.5
        else:
            pa1 = 0.33
            pa2	= 0.47
            #pa3 = 0
            pa4 = 0.2
    elif CLASS == "B":#0.8 0.2
        if Sa4<0.75:
            pa1 = 0.8 * 0.5
            pa2 = 0.2 *0.5
            #pa3 = 0
            pa4 = 0.25
        else:
            pa1 = 0.8
            pa2	= 0.2
            #pa3 = 0
            pa4 = 0
    elif CLASS == "C":
        if Sa4<0.75:
            pa1 = 0.5
            pa2 = 0
            #pa3 = 0
            pa4 = 0.25
        else:
            pa1 = 1
            pa2	= 0
            #pa3 = 0
            pa4 = 0
    elif CLASS == "D":
        if Sa4 < 0.75:
            pa1 = 0
            pa2 = 0.5
            #pa3 = 0
            pa4 = 0.25
        else:
            pa1 = 0
            pa2	= 1
            #pa3 = 0
            pa4 = 0
    S = int(Sa1*pa1*total+Sa2*pa2*total+Sa4*pa4*total+0.5)

    '''

    （1）再来一个test，用于生成另一种表2（心理学分数的其他sheet）
    三个分数分别是相似度*10,四舍五入。
    
    搞一搞这么写入表中    
    
    （2）生成表3（2.22）---表三的人工评分都不完全，先不生成
    （3）生成表4（4.12）
    
    
    
    '''

    result = {}
    result["S"] = S
    result["Sa1"] = Sa1
    result["Sa2"] = Sa2
    #result["Sa3"] = Sa3
    result["Sa4"] = Sa4
    result['count1'] = count1
    result['count2'] = count2
    result['CLASS'] = CLASS

    print("类别：",CLASS)
    print("关键词相似度：",Sa1)
    print("语义相似度：",Sa2)
    #print("核心语义相似度：",Sa3)
    print("句长相似度：", Sa4)
    print("最终得分：",S)

    return result

def extract600Keywords():
    # with open('600答案.txt','r', encoding='utf-8') as f1:
    with open('标准答案.txt','r') as f1:
        content = f1.read().splitlines()
        with open('100关键字.txt','w+', encoding='utf-8') as f:
            for s in content:
                [s,flag] = predone1(predone(s))
                key_words = KEYWORD2(s,flag)
                print(key_words)
                f.write(" ".join(key_words)+"\n")

if __name__ == "__main__":



    S1=["健康相关行为：是指有助于个体在生理、心理和社会上保持良好状态、预防疾病的行为。它与健康信念密切相关，是个体为维持、实现、重建健康和预防疾病的活动。",
        "自我效能理论：是个体对自己成功执行某行为并导致预期结果的信念，属于自信范畴。自我效能在制定健康生活目标的意向阶段、具体行为改变阶段、防止复发过程中都具有重要的调节作用。自我效能来源于成功的经验、替代性经验、言语劝导和生理状态等四方面。",
        "药物成瘾：是指强迫性、失去控制的用药行为，是药物的精神依赖性和生理依赖性共同造成的结果。能成瘾的药物具有引起精神愉悦或缓解烦恼的作用，这是触发条件。",
        "酗酒：也称为酒精滥用或问题饮酒，它是造成躯体或精神损害或不良社会后果的过度饮酒。其特点是对饮酒不能自控，思想关注于酒，饮酒不顾后果；思维障碍；每一症状可以是持续或周期性的。",
        "网络成瘾：是指慢性或周期性的对网络的着迷状态，不可抗拒的再度使用的渴望与冲动，上网后欣快，下网后出现戒断反应，出现生理或心理的依赖现象。",
        "肥胖：是指体内过量脂肪堆积而使体重超过某一范围，当肥胖影响健康或正常生活及工作时才称为肥胖症。"]
    '''
    S2=["",
        "",
        "",
        "",
        "",
        "",
        ]
    '''

    
    
    S2 =["健康相关行为:指人们为了增强健康体质和维持身心健康而进行的各项活动，如充足的睡眠、均衡的营养、适当的运动等。",
        "自我效能理论：指个人对自己完成某方面工作能力的主观评估。",
        "药物成瘾：指某人因身体或心理上的需求长期或过量服用某种药物，并对该药物产生很强的依赖性。",
        "酗酒：一次喝5瓶或5瓶以上啤酒，或者血液中酒精含量达到或超过8*10^-2g/L。",
        "网络成瘾：主要指长时间沉迷于网络，对之外的事情都没有过度的兴趣，从而影响身心健康的一种病症。",
        "肥胖：人体内脂肪过度、沉积的状态。主要见于皮下组织，按年龄和身高算，超过标准体重20%~25%即为肥胖。",
        ]

    for i in range(6):
        print(i+1)
        Result = Review(S1[i], S2[i])


    '''
    s1 = input("标准答案：")
    s2 = input("学生答案：")
    s1="网络成瘾：是指慢性或周期性的对网络的着迷状态，不可抗拒的再度使用的渴望与冲动，上网后欣快，下网后出现戒断反应，出现生理或心理的依赖现象。"
    s2="网络成瘾：是上网者由于长时间地和习惯地沉浸在网络时空当中，对互联网产生强烈地依赖，以至于达到了痴迷的程度而难以自我解脱的行为状态和心理状态。"
    Result = Review(s1,s2)
    # print("类别：",Result["CLASS"])
    #print("标准答案否定词个数：",Result["count2"])
    #print("学生答案否定词个数：",Result["count1"])
    print("关键词相似度：",Result["Sa1"])
    print("语义相似度：",Result["Sa2"])
    print("句长语义相似度：",Result["Sa4"])
    print("最终得分：",Result["S"])
    '''






