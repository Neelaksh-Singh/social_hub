# Importing all the required libraries and modules 
import os
from dotenv import load_dotenv
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from github import Github
from urllib.parse import urlparse
import threading, concurrent.futures
import asyncio



load_dotenv()
access_token = os.getenv('access_token')
g = Github(access_token)


class Social_Graph:
    def __init__(self):
        self.data = pd.read_excel('raw_data.xlsx')
        self.data.columns = ['links']
        self.user_list = []
        self.social_graph = {}
        self.MAX_THREAD = 100
        self.lock = threading.RLock()
    
    def preprocess(self):
        url_links = list(self.data['links'])
        for i, link in enumerate(url_links):
            path = urlparse(link).path
            path = path[1:]
            link = path.partition('/')[0]
            url_links[i] = link
        return url_links

    def save(self,user,repo):
        pass

    def user_sg(self,user):
        repos = set()
        for repo in g.get_user(user).get_repos():
            repos.add(repo.name)
        # print(repos)
        with self.lock:
            for repo in repos:
                if repo not in self.social_graph:
                    self.social_graph[repo] = [user]
                else:
                    self.social_graph[repo].append(user)
        
        return 

       
    # Runs task for each single individual seperately
    def parse_user_data(self, users ):
        threads = min(self.MAX_THREAD, len(users))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.user_sg, users)

    def construct_graph(self):
        self.user_list = self.preprocess()
        self.parse_user_data(self.user_list)
        # print(len(self.social_graph))
        df=pd.concat({k: pd.Series(v) for k, v in self.social_graph.items()})
        print(df)
        df.to_excel('mySocialGraph.xlsx')
        return

sg = Social_Graph()
sg.construct_graph()