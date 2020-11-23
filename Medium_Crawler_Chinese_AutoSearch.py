import time
import gc
from bs4 import BeautifulSoup as bs
import requests
import jieba.analyse
from collections import Counter

# Input 3 varibles. The keyword for searching, how many result you want to show, and if any article id you want to ignore. 
# This funciton is specially designed for searching Chinese article while collect the keys word from each article for trend analysis.
# It will return a nest list with [[id, pub_time, title, author, likes, url, image_url, discussion, keywords, content]]
def Medium_Crawler(keyword, resultcount, ignore=None):
    url = f"https://medium.com/search/posts?q={keyword}&count={resultcount}&ignore={ignore}"
    passed_1 = 0
    
    while 1:
        session_requests = requests.session()
        session_requests.keep_alive = False
        try:
            link = session_requests.get(url, headers={
                "Cookie": "Your cookie",                 
                "Host": "medium.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
            })
        except:
            print("Cannot search, wait 5 second and try again.")
            time.sleep(5)
            passed_1 = passed_1 + 1
            if passed_1 == 10:
                print ("Search failed, move to next keyword")
                return (passed_1)
            continue
        break

    # BeautifulSoup 
    content = bs(link.text, "html.parser")
    all_articles = content.find_all("div", class_="postArticle")
    articles_list = []
    jieba.set_dictionary('./extra_dict/dict.txt.big')

    # Getting content 

    for n in all_articles:

        # getting medium id
        id = n.get("data-post-id")
  
        # getting publish time
        pub_time = n.select_one("time").get("datetime")

        # getting author
        author = n.find_all("a", class_="ds-link")
        try:
            author = author[0].text
        except:
            author = "Null"
        author = author.replace("'", " ")

        # getting title from different div
        h3 = n.find_all("h3", class_="graf")
        h4 = n.find_all("h4", class_="graf")
        p = n.find_all("p", class_="graf")
        li = n.find_all("li", class_="graf")

        if [] != h3:
            title = h3[0].text
            title = title.replace("'", " ")
        elif [] != h4:
            title = h4[0].text
            title = title.replace("'", " ")
        elif [] != p:
            title = p[0].text
            title = title.replace("'", " ")
        elif [] != li:
            title = li[0].text
            title = title.replace("'", " ")

        if len(title) > 50:
            title = title[:50] + "..."

        # getting likes
        likes = n.find_all("button", class_="button")
        likes = likes[1].text
        likes = likes.replace(".", "")
        likes = likes.replace("K", "00")
        if str.isdigit(likes) == False:
            likes = "0"
        likes = int(likes)

        # getting article url
        url = n.find_all("a", class_="link")

        try:
            url = url[2].get("data-action-value")
            url = url.split("?source", 1)
            url = url[0]
        except:
            url = url[1].get("data-action-value")
            url = url.split("?source", 1)
            url = url[0]

        # retrieve content
        while 1:
            session_requests_r1 = requests.session()
            session_requests_r1.keep_alive = False
            passed_2 = 0
            try:
                r1 = session_requests_r1.get(url, headers={
                    "Cookie": "Your cookie",
                    "Host": "medium.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
                })
            except:
                print("Cannot retrieve content, move to next article.")
            break

        # Getting content and title
        soup = bs(r1.text, "html.parser")
        post1 = soup.find_all(["p", "h1"])
        text_r = ""
        # Remove not needed part.
        for m in post1:
            if m.text != "Written by":
                text_r = text_r + "".join(m.text)


        # check Chinese 
        if "的" not in text_r:
            print (url)
            print (text_r)
            print("Content is not Chinese, skip.")
            continue

        if "の" in text_r:
            print("Content is Japanese, skip.")
            continue
            
        text_r = text_r.replace("'", " ")

        content = text_r

        # Loading jieba large
        try: 
            jieba.analyse.set_stop_words("extra_dict/stop_words.txt")
        except:
            pass
        # getting keyword from the article
        keywords = jieba.analyse.extract_tags(text_r, topK=5)


        # getting picture link
        image_url = n.find_all("img", class_="progressiveMedia-image")
        if image_url != []:
            image_url = image_url[0].get("data-src")
            if image_url[-5:-1] == ".jpe":
                image_url = image_url
            elif image_url[-4:-1] == ".pn":
                image_url = image_url
            elif image_url[-4:-1] == ".gi":
                image_url = image_url
            elif "https://cdn-images-1.medium.com/fit" in image_url:
                image_url = image_url
            else:
                image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/450px-No_image_available.svg.png"
        else:
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/450px-No_image_available.svg.png"

        # getting comments count
        aclass = n.find_all("a", class_="button")
        try:
            discussion = aclass[1].text
            discussion = discussion.replace(" response", "")
            discussion = int(discussion)
        except:
            discussion = -1

        article = [id, pub_time, title, author, likes, url, image_url, discussion, keywords, content]
        articles_list.append(article)
    return articles_list
    # print(table)



# main program
search_list = ['2020 11 的', ]
search_key = 0
search_count = 0

# define seearching cycle
while search_count != 1000:

    print ("Searching:", search_list[search_key])
    articles_list = Crawler(search_list[search_key], 100, "abd3060d4bbf")
    if articles_list == 10:
        search_key = search_key + 1
        continue

    # keyword list + 1 to search next key
    search_key = search_key + 1
    keywords_list = []

    # An example of inputting the search data into a DB
    # for n in range(len(articles_list)):
    #    id = articles_list[n][0]
    #    data = DB.IntputFindCmd(f"SELECT * FROM main WHERE medium_id = '{articles_list[n][0]}'")
    #    if data == []:
    #        TitleList = ["medium_id", "title", "author", "pub_date", "likes", "comment", "content_url", "image_url", "content"]
    #        ContentList = [articles_list[n][0], articles_list[n][2], articles_list[n][3], articles_list[n][1], str(articles_list[n][4]), str(articles_list[n][7]), articles_list[n][5], articles_list[n][6], articles_list[n][9]]
    #        DB.Insert("main", TitleList, ContentList)

    # Identify keyword for next search.
    most_keywords_num = Counter(keywords_list).most_common(10)
    most_keywords = []
    
    # Add "的" in the keyword to search Chinese content    
    for n in range(len(most_keywords_num)):
        if most_keywords_num[n][0] not in search_list:
           most_keywords.append(most_keywords_num[n][0] + " 的")
            
    search_list += most_keywords

    gc.collect()
    
    print("The keywords for searching:", search_list)
    search_count = search_count + 1