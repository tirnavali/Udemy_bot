from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import requests, threading,glob,sys
import bs4 as bs


def is_rate_valid(element):
    '''
    Finds if the current course meets the conditions
    :param element: the element of the relevant course
    :return: if the current course meets the conditions
    '''

    rate = element.find("div", {"class": "coupon-details-extra-3"}).find_all('p')[2].text
    rate = rate.split('Rate: ')[1]
    stars = float(rate.split('/')[0])
    people = int(rate.split('/')[1])
    return stars >= 4.2 and people >= 200


def is_valid_coupon(element):
    '''
    Checks if the coupon is not expired
    :param element: relevant element
    :return: if the coupon is not expired
    '''

    button = element.find("a", {"class": "button-icon"}).text
    return "Expired" not in button


def get_udemy_link(element):
    '''
    Gets the relevent link to the udemy course
    :param element: relevant element
    :return: the relevent link to the udemy course
    '''

    link1 = element.find("a", {"class": "button-icon"})['href']
    source = requests.get(link1)
    soup = bs.BeautifulSoup(source.content, 'lxml')
    return soup.find("a", {"class": "button-icon"})['href']


def add_links(soup):
    '''
    Cheack if the course meets the conditions
    :param soup:  relevent BeautifulSoup object
    :return:
    '''
    for i in soup.find_all("div", {"class": "col-md-4 col-sm-6"}):
        if is_valid_coupon(i):
            if is_valid_coupon(i) and is_rate_valid(i):
                potential_urls.append(get_udemy_link(i))


def find_potential_urls():
    '''
    Finds all relevent courses
    '''
    print("Looking for potential links")
    for l in range(1, 217):  # might needed pages update
        url = "https://www.udemyfreebies.com/course-category/it-and-software/" + str(l)
        source = requests.get(url)
        soup = bs.BeautifulSoup(source.content, 'lxml')
        while (threading.activeCount() >= 100):
            sleep(1)
        threading.Thread(target=add_links, args=(soup,)).start()

    # you can add more categories
    for l in range(1, 305):  # might needed pages update
        url = "https://www.udemyfreebies.com/course-category/development/" + str(l)
        source = requests.get(url)
        soup = bs.BeautifulSoup(source.content, 'lxml')
        while (threading.activeCount() >= 100):
            sleep(1)
        threading.Thread(target=add_links, args=(soup,)).start()

    while (threading.activeCount() != 1):
        sleep(1)


def click():
    '''
    clicks on enroll button
    '''

    try:
        browser.find_element_by_xpath(
            "//div[contains(@class,'ud-component--course-landing-page-udlite--buy-button-cacheable')]").click()
        sleep(1)
    except:
        pass
    try:
        browser.find_element_by_class_name("slider-menu__buy-button").find_element_by_tag_name("button").click()
        sleep(2)
        browser.find_element_by_class_name("styles--complete-payment-container--3Jazs").find_element_by_tag_name(
            "button").click()
        sleep(1)
    except:
        pass


def is_account_exist(email, password):
    '''
    Checks if the credentials are correct
    :param email: users email
    :param password: users password
    :return: if the credentials are correct
    '''

    print("Checking the email and the password are correct")
    options = Options()
    # options.add_argument("--incognito")
    # options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    #browser.set_window_position(5000, 5000) make checking window invisible
    browser.get("https://www.udemy.com/join/login-popup/")
    sleep(1)
    browser.find_element_by_id("email--1").send_keys(email)
    sleep(1)
    browser.find_element_by_id("id_password").send_keys(password)
    sleep(1)
    temp_url = browser.current_url
    browser.find_element_by_id("submit-id-submit").click()
    sleep(4)
    is_exist = temp_url == browser.current_url
    browser.close()
    return is_exist


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Wrong input make sure you type you Email and Password")
        exit()
    elif is_account_exist(sys.argv[1], sys.argv[2]):
        print("There was a problem logging in.Check your email and password or create an account.")
        exit()

    email = sys.argv[1]
    password = sys.argv[2]

    potential_urls = []
    if glob.glob("urls.txt"):
        with open("urls.txt") as f:
            potential_urls = f.read().split("\n")
    else:
        find_potential_urls()
        ###################
        # save urls
        f = open("urls.txt", "a")
        for u in potential_urls:
            f.write(u + "\n")
        f.close()
        ###################

    print("found ", len(potential_urls), " urls")
    options = Options()

    # options.add_argument("user-data-dir=/tmp/tarun")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    browser.get("https://www.udemy.com/join/login-popup/")
    sleep(1)
    browser.find_element_by_id("email--1").send_keys(email)
    sleep(1)
    browser.find_element_by_id("id_password").send_keys(password)
    sleep(1)
    browser.find_element_by_id("submit-id-submit").click()
    
    print("saving the courses to your udemy account")
    course_count = 0
    for url in potential_urls:
        try:
            browser.get(url)
            sleep(2)
            if "Free" in browser.find_element_by_xpath \
                        (
                        "//div[contains(@class, 'price-text--price-part--Tu6MH udlite-clp-discount-price udlite-heading-lg')]") \
                    .find_elements_by_xpath(".//span")[1].text:
                click()
                course_count += 1
        except:
            pass
    print("Done added " + str(course_count) + " courses")
    browser.close()
