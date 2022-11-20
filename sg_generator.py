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
import pickle
# from heapdict import heapdict

pickle_file = "socialGraph.pickle"


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
        self.active_users =  {}
    
    def preprocess(self):
        url_links = list(self.data['links'])
        for i, link in enumerate(url_links):
            path = urlparse(link).path
            path = path[1:]
            link = path.partition('/')[0]
            url_links[i] = link
        return url_links

    def saveAndLoad(self,id,file_name):
        if id==0:
            with open(file_name, 'wb') as handle:
                pickle.dump(self.social_graph, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(file_name, 'rb') as handle:
                data = pickle.load(handle)
            return data
        return

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

    def clean_graph(self,data):
        graphData = {}
        for key,val in data.items():
            
            if len(val) > 1:
                graphData[key] = val
        
        return graphData
        
    def construct_graph(self):
        self.user_list = self.preprocess()
        self.parse_user_data(self.user_list)
        self.social_graph = self.clean_graph(self.social_graph)
        # print(len(self.social_graph))
        self.saveAndLoad(0,pickle_file)
        df=pd.concat({k: pd.Series(v) for k, v in self.social_graph.items()})
        print(df)
        df.to_excel('mySocialGraph.xlsx')
        return
    
    def activeNodes(self):
        data = self.saveAndLoad(1,pickle_file)
        # print(len(data))
        
        for key,val in data.items():
            # users = val
            for user in val:
                if user not in self.active_users:
                    self.active_users[user] = 1
                else:
                    self.active_users[user] += 1
        
        # print(list(self.active_users.items()))
        keyMax = max(self.active_users, key= lambda x: self.active_users[x])
        # print(keyMax)
        return keyMax
                                     
        # g = nx.Graph(data)
        # print(g)
        # print(g.nodes)
        # nx.draw(g)
        # plt.draw()
        # plt.savefig("filename.png")

sg = Social_Graph()
active_user= sg.activeNodes()
print(active_user,sg.active_users[active_user])