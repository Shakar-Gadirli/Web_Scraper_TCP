import re
import constants
import socket, argparse
import requests, threading
from bs4 import BeautifulSoup
from colorama import Fore, Style



class Server:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def process(self,sc,sockname):
        link = sc.recv(constants.MAX_BYTES).decode()
        page = requests.get(link)
        
        print(f"[+] Scraping {link}")
        soup = BeautifulSoup(page.content,"html.parser")

        image_count = self.count_image(soup)
        leaf_p_count = self.count_p_leafs(soup)

        answer = f"{image_count} {leaf_p_count}"

        sc.send(answer.encode())

        print(Fore.GREEN,Style.BRIGHT,"\n[+] The process completed successfully.")

    def count_image(self,soup):
        count = len(soup.find_all("img"))
        return count

    def count_p_leafs(self, soup):
        c = 0
        p_s = soup.find_all('p')
        for p in p_s:
            if not p.find_all("p"):
                c += 1
        return c


    def start(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

        print(Fore.BLUE,Style.BRIGHT,"[+] The server is listening at:", self.sock.getsockname())

        while True:
            sc, sockname = self.sock.accept()
            print(Fore.YELLOW,Style.BRIGHT,'\n[+] Accepted a connection from', sockname)

            thread = threading.Thread(target=self.process, args=(sc,sockname))
            thread.start()


class Client:
    
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def correct_link(self,link):
        x = re.search("http[s]",link)
        if not x:
            link = "https://" + link
        
        return link

    def start(self,link):
        self.sock.connect((self.host,self.port))
        link = self.correct_link(link)
        encoded_link = link.encode()
        self.sock.send(encoded_link)

        image_count, leaf_p = (self.sock.recv(constants.MAX_BYTES)).decode().split()
        print(Fore.RED, Style.BRIGHT,f"Images: {Fore.WHITE}{image_count}{Fore.RED},{Style.BRIGHT} Leaf paragraphs: {Fore.WHITE}{leaf_p}")

        self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Web Scraper")
    choices = {"server": Server, "client": Client}
    parser.add_argument('role', choices = choices, help = "server or client")
    parser.add_argument("-p",metavar="PAGE", type=str, help="Web URL")
    args = parser.parse_args()

    Class = choices[args.role]
    
    if args.role == "client":
        cl_obj = Class(constants.HOST,constants.PORT)
        cl_obj.start(args.p)
    
    elif args.role == "server":
         s_obj = Class(constants.HOST,constants.PORT)
         s_obj.start()




