import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils import read_urls, url2id

options = Options()
#options.add_argument("--headless")  # 不打开浏览器界面，以节省时间
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", "enable-logging"]
)
browser = webdriver.Chrome(options=options)

comments = ["来了来了[脱单doge]", 
            "就想简简单单中个奖QAQ",
            "啊啊啊啊啊, 让我中一次吧 T_T",
            "天选之子[doge]",
            "好耶，感谢[星星眼][星星眼][星星眼]"]
link_list=[]
num=0


def now_time():
    return "\033[32m[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]\033[0m"


def random_comment():
    global comments
    li = comments[:-1]
    pick = random.choice(li)
    idx = comments.index(pick)
    comments[idx], comments[4] = comments[4], comments[idx]
    return pick


def gethtml():
    """
    免登录访问B站
    """
    url = "https://www.bilibili.com"
    browser.get(url)
    browser.maximize_window()
    # 删除这次登录时，浏览器自动储存到本地的cookie
    browser.delete_all_cookies()

    # 读取之前已经储存到本地的cookie
    cookies_filename = "./cookies.json"
    cookies_file = open(cookies_filename, "r", encoding="utf-8")
    cookies_list = json.loads(cookies_file.read())
    for cookie in cookies_list:  # 把cookie添加到本次连接
        browser.add_cookie(
            {
                "domain": ".bilibili.com",  # 此处xxx.com前，需要带点
                "name": cookie["name"],
                "value": cookie["value"],
                "path": "/",
                "expires": None,
            }
        )
    # 再次访问网站，由于cookie的作用，从而实现免登陆访问
    browser.get(url)
    time.sleep(3)

def is_reference():
    """
    是否存在动态引用
    """
    try:
        browser.find_element(By.CLASS_NAME, "reference")
        return True
    except:
        return False

def is_official():
    try:
        official_icon = browser.find_element(By.CSS_SELECTOR, ".bili-rich-text-module.lottery")
        return official_icon
    except:
        return None

def is_reserve():
    try:
        reserve_icon = browser.find_element(By.CLASS_NAME, "uncheck")
        return reserve_icon
    except:
        return None


def do_reference():
    """转发加码动态
    """
    try:
        do_follow()
        forward_icon = browser.find_element(By.CSS_SELECTOR, ".side-toolbar__action.forward")
        forward_icon.click()
        time.sleep(1)
        textarea = browser.find_element(By.CLASS_NAME, "bili-rich-textarea__inner")
        # 使用js修改文本内容
        comment = random_comment()
        script = "arguments[0].childNodes[0].textContent = '\u200b' + '{}' + arguments[0].childNodes[0].textContent".format(comment)
        browser.execute_script(script, textarea)
        # 发布
        browser.find_element(By.CLASS_NAME, "bili-dyn-share-publishing__action").click()
        do_comment(False)
        global num
        num = num + 1
        print("{} {}：已成功转发动态{}".format(now_time(), num, url2id(url)))
        time.sleep(7 * random.random())
    except:
        print("{} {}：转发动态{}失败".format(now_time(), num, url2id(url)))


def do_official(official_icon):
    if official_icon is None:
        return
    try:
        official_icon.click()
        iframe = browser.find_element(By.CLASS_NAME, 'bili-popup__content__browser')
        browser.switch_to.frame(iframe)
        button = browser.find_element(By.CLASS_NAME, "join-button")
        time.sleep(2)
        button.click()
        browser.switch_to.default_content()
        global num
        num = num + 1
        print("{} {}：已成功转发official动态{}".format(now_time(), num, url2id(url)))
        time.sleep(7 * random.random())
    except:
        print("{} {}：转发official动态{}失败".format(now_time(), num, url2id(url)))


def do_reserve(reserve_icon):
    try:
        reserve_icon.click()
        global num
        num = num + 1
        print("{} {}：已成功预约直播预约动态{}".format(now_time(), num, url2id(url)))
        time.sleep(7 * random.random())
    except:
        print("{} {}：预约直播预约动态{}失败".format(now_time(), num, url2id(url)))

def do_comment(sync_to_dyn: bool = False):
    # 鼠标移向别处
    other_place = browser.find_element(By.XPATH, '//*[@id="nav-searchform"]/div[1]/input')
    ActionChains(browser).move_to_element(other_place).perform()
    time.sleep(3+random.random())

    for i in range(10): # 慢慢向下滑动窗口，让所有信息加载完成
        browser.execute_script('window.scrollTo(0, {});'.format(i*100))
        time.sleep(0.1)
    time.sleep(1)
    target = browser.find_element(By.CLASS_NAME, "bili-tabs__nav__items")
    browser.execute_script("arguments[0].scrollIntoView();", target) # 拖动到可见的元素去
    time.sleep(3 * random.random())

    # 输入评论
    browser.find_element(By.CLASS_NAME, "reply-box-textarea").click()
    time.sleep(1)
    browser.switch_to.active_element.send_keys(random_comment())
    if sync_to_dyn:
        # 勾选 同时转发到我动态
        browser.find_element(By.ID, "forwardToDynamic").click()
    
    time.sleep(1)
    # 发表评论
    browser.find_element(By.CLASS_NAME, "send-text").click()

def do_follow():
    # 关注
    profile = browser.find_element(By.CLASS_NAME, "bili-dyn-avatar")
    ActionChains(browser).move_to_element(profile).perform()
    time.sleep(1)
    follow = browser.find_element(By.CSS_SELECTOR, ".bili-user-profile-view__info__button.follow")
    if "checked" not in follow.get_attribute("class"):
        follow.click()

def dynamic(url):
    browser.get(url)
    time.sleep(1+random.random())
    has_ref = is_reference()
    official_icon = is_official()
    reserve_icon = is_reserve()
    if is_reserve():
        do_reserve(reserve_icon)
        return
    if has_ref:
        do_reference()
        return
    elif official_icon:
        do_official(official_icon)
        return
    do_follow()
    do_comment(True)
    global num
    num = num + 1
    print("{} {}：已成功转发动态{}".format(now_time(), num, url2id(url)))
    time.sleep(7 * random.random())


if __name__ == "__main__":
    link_list = read_urls()
    gethtml()
    
    note = open('./link_history.txt', 'a+', encoding="utf-8")
    note.seek(0)
    history= note.read().split('\n')
    for url in link_list:
        id=url[23:41]
        if id not in history:
            try:
                dynamic(url)
            except Exception as e:
                continue
            note.write(id+'\n')
    note.close()
    
    browser.close()
