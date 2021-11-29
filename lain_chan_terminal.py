from lxml import html
import requests
import os
import random


# This python script allows you to view posts from lainchan.org inside of your terminal
# This script honestly isn't that practical, since you can't see images. This would probably be more suited for a text board
# TODO add support for browsing catalog


# ansi 256 color escape code. Most modern terminals should support 256 colors
# highlight color
bg = "\u001b[48;5;"
# text color
fg = "\u001b[38;5;"

# default background color
default = bg + "16m"

# reset text color
rs = "\u001b[0m" + bg + default

# You can edit these for custom colors!
colors = [
    fg + "76m" + default,   # post body
    fg + "63m" + default,   # title
    fg + "140m" + default,  # name
    fg + "88m" + default,   # dark red text
    fg + "124m" + default,  # board title
    fg + "124m" + default,  # red
    fg + "242m" + default,  # dark gray
]

banner = """
  _       _            _                                  
 | |     (_)          | |                                 
 | | __ _ _ _ __   ___| |__   __ _ _ __    ___  _ __ __ _ 
 | |/ _` | | '_ \ / __| '_ \ / _` | '_ \  / _ \| '__/ _` |
 | | (_| | | | | | (__| | | | (_| | | | || (_) | | | (_| |
 |_|\__,_|_|_| |_|\___|_| |_|\__,_|_| |_(_)___/|_|  \__, |
                                                     __/ |
                                                    |___/ 
"""


link = 'https://www.lainchan.org/'
current_page = 1

# these are all the non-board pages
non_working_pages = (0, 1, 2, 3, 21, 22, 23, 24, 25, 26)


def homepage():
    clear_screen()
    print(f'{rs}{random_color()}', end='')
    print(banner, end='')
    
    # get homepage html
    home = requests.get(link)
    tree = html.fromstring(home.content)
    
    # get the navigation elements and print them out
    nav_a = tree.xpath('/html/body/div[1]/div/span/a/@href')
    nav = tree.xpath('/html/body/div[1]/div/span/a/text()')
    print_selection(nav)

    usr_input = input('\n> ')
    
    try:

        if usr_input.isnumeric():

            if int(usr_input) in non_working_pages:
                homepage()
            else:
                # get board page html
                new_page = requests.get(link + nav_a[int(usr_input)])
                new_tree = html.fromstring(new_page.content)
                add_newlines(new_tree)
                print_posts(new_tree, nav[int(usr_input)])
        else:
            homepage()

    except IndexError:
        homepage()


def format_post(title, name, post_id, post_time, post):
    # This function loops through every element in the title, name, post id, date, and the body text
    # and prints it nicely to the terminal

    post_header = ""
    # used for making a line seperator the same length as the post header
    header_length = 0

    for element in title:
        post_header += f"{colors[1]}{element} "
        header_length += len(element) + 1

    for element in name:
        post_header += f"{colors[2]} {element}"
        header_length += len(element) + 1

    for element in post_time:
        post_header += f'  {colors[6]}{element}'
        header_length += len(element) + 2

    for element in post_id:
        post_header += f"  {colors[3]}No.{element}"
        header_length += len(element) + 5

    print(post_header)
    print(seperator(header_length))

    for i in range(len(post)):
        print(f"{colors[0]}{post[i].text_content()}", end=rs)


def print_posts(tree, board):
    global current_page
    current_post = 0
    
    # loop through each post on the page
    for i in range(1, 11):

        clear_screen()
        print(f'{colors[4]}/{board}/{rs}', "\n")
        
        # post xpath info
        title = tree.xpath(f'/html/body/div[2]/form[2]/div[{i}]/div[2]/p/label/span[1]/text()')
        name = tree.xpath(f'/html/body/div[2]/form[2]/div[{i}]/div[2]/p/label/span[2]/text()')
        post_id = tree.xpath(f'/html/body/div[2]/form[2]/div[{i}]/div[2]/p/a[2]/text()')
        post_time = tree.xpath(f'/html/body/div[2]/form[2]/div[{i}]/div[2]/p/label/time/text()')
        post = tree.xpath(f'/html/body/div[2]/form[2]/div[{i}]/div[2]/div')

        current_post = i
        
        # print post
        format_post(title, name, post_id, post_time, post)
        
        usr_input = input("\n\n0 - Enter nothing to view next post\n1 - Enter 1 to view replies\n> ")

        if usr_input.isnumeric():
            
            # show replies
            if int(usr_input) == 1:
                
                print("\nloading replies...")
                
                # get the reply link
                post_link = tree.xpath(f'/html/body/div[2]/form[2]/div[{current_post}]/div[2]/p/a[3]/@href')
                # get the reply page html
                reply_page = requests.get(link + post_link[0])
                reply_tree = html.fromstring(reply_page.content)

                add_newlines(reply_tree)
                clear_screen()
                
                # get full OP post xpath info
                op_title = reply_tree.xpath('/html/body/div[2]/form[2]/div[1]/div[2]/p/label/span[1]/text()')
                op_name = reply_tree.xpath('/html/body/div[2]/form[2]/div[1]/div[2]/p/label/span[2]/text()')
                op_id = reply_tree.xpath('/html/body/div[2]/form[2]/div[1]/div[2]/p/a[2]/text()')
                op_time = reply_tree.xpath('/html/body/div[2]/form[2]/div[1]/div[2]/p/label/time/text()')
                op_post = reply_tree.xpath('/html/body/div[2]/form[2]/div[1]/div[2]/div')
                
                # print full OP post
                format_post(op_title, op_name, op_id, op_time, op_post)

                print("\n\n0 - Enter nothing to view next reply\n1 - Enter 1 to view next post\n")

                num_replies = len(reply_tree.xpath('/html/body/div[2]/form[2]/div[1]/div/div[2]'))

                for i in range(0, num_replies):
                    
                    # get reply xpath info
                    reply = reply_tree.xpath(f'/html/body/div[2]/form[2]/div[1]/div[{i+3}]/div[2]/div[2]')
                    reply_name = reply_tree.xpath(f'/html/body/div[2]/form[2]/div[1]/div[{i+3}]/div[2]/p/label/span/text()')
                    reply_name_special = reply_tree.xpath(f'/html/body/div[2]/form[2]/div[1]/div[{i+3}]/div[2]/p/label/a/span/text()')
                    reply_time = reply_tree.xpath(f'/html/body/div[2]/form[2]/div[1]/div[{i+3}]/div[2]/p/label/time/text()')
                    reply_id = reply_tree.xpath(f'/html/body/div[2]/form[2]/div[1]/div[{i+3}]/div[2]/p/a[3]/text()')
                    
                    # print name of reply
                    for element in reply_name:
                        print(f'{colors[2]}{element}', end=f'{rs}  ')
                    
                    # print red names
                    for element in reply_name_special:
                        print(f'{colors[5]}{element}', end=f'{rs}  ')
                    
                    # print date and post id
                    print(f'{colors[6]}{reply_time[0]}', end=f'{rs}  ')
                    print(f'{colors[3]}No.{reply_id[0]}', end=f'{rs}\n')
                    
                    # print body text
                    for element in reply:
                        print(f"{colors[0]}{element.text_content()}", end=rs)

                    print('\n\n')

                    usr_input = input()

                    if usr_input.isnumeric(): 
                        if int(usr_input) == 1:
                            break
        
    clear_screen()
    print("Go to next page or return home?\n0 - Enter nothing to go to next page\n1 - Enter 1 to go to home page")
    
    usr_input = input("> ")
    
    if usr_input.isnumeric():
        if int(usr_input) == 1:
            homepage()
    
    # get the html content of the next page
    current_page += 1
    next_page = requests.get(link + board + "/" + str(current_page))
    next_page_tree = html.fromstring(next_page.content)
    print_posts(next_page_tree, board)


# print elements in xpath in a list in random colors
# used for board navigation
def print_selection(xpath):
    for i in range(len(xpath)):
        if i % 8 == 0:
            print("")
        print(f'{random_color()}({i}){xpath[i]}{rs}', end=" ")
    print("")


# replace all <br> tags with newline escape characters so they show correctly in terminal
def add_newlines(tree):
    for br in tree.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"


# clear the screen on windows and unix
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# returns a line seperator with a given length
def seperator(length):
    seperator = rs
    seperator += (length * "-")
    return seperator


def random_color():
    color = random.randint(21, 231)
    return fg + str(color) + "m";



if __name__ == "__main__":
    homepage()
