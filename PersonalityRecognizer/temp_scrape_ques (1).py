from BeautifulSoup import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.porter import *
import subprocess
import shlex
import os
from scipy import spatial
from nltk.tokenize import RegexpTokenizer
import shutil
import pickle
import operator
import json
import networkx as nx
f = []


def extract_nodes_at_level(G, root, level):

    x = nx.shortest_path_length(G, root)
    sorted_x = sorted(x.items(), key=operator.itemgetter(1),reverse= True)
    nodes_at_level = []
    for (node,depth) in sorted_x:
        if depth == level:
            nodes_at_level.append(node)
    return nodes_at_level


# Function to return the nodes which are at nearest distance to node in list_node in the Graph
def nearest_node_in_list(Graph, node, list_node):
    closest_node_list = [node]
    closest_single_node = node
    closest_distance = 9999
    first_time = 1

    for each_node in list_node:
        try:
            distance = nx.shortest_path_length(Graph,source = node, target= each_node)
        except Exception as e:
            continue
        if distance < closest_distance:
            closest_node_list = [each_node]
            closest_single_node = each_node
            closest_distance = distance
        elif distance == closest_distance:
            closest_node_list.append(each_node)

    return closest_node_list


def TopicHierarchy(user_topic_list):
    if os.path.isfile("graph.pkl"):
         graph = load_obj("graph.pkl")
    if os.path.isfile("levelNodes.pkl"):
         nodes_level = load_obj("levelNodes.pkl")
    print "user_topic_list"
    print user_topic_list
    user_topic_dict = {}
    user_list = [0 for x in range(len(nodes_level))]
    for usertopic in user_topic_list:
        node_list = nearest_node_in_list(graph, usertopic, nodes_level)
        print 'node list'
        print node_list
        for node in node_list:
            user_list[nodes_level.index(node)] += 1
    print 'user_list vector'
    print user_list
    return user_list


def save_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)


def run_command(cmd):
    cmd = shlex.split(cmd)
    return subprocess.check_output(cmd).decode('ascii')

userScores = {}
userTopics = {}
stop = stopwords.words('english')
stop.append(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', ' '])
quesDirname = "/home/saurabh/IR_Project/user_ques_Xt/"
topicDirname = "/home/saurabh/IR_Project/user_topic_Xt/"


def processQuestion(temp_refinedques):
    temp_refinedques = unicode(temp_refinedques, errors='ignore')
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(temp_refinedques)
    tokens = [i for i in tokens if i not in stop]
    tokens = list(set(tokens))
    stemmer = PorterStemmer()
    stem_tokens = [stemmer.stem(token) for token in tokens]
    stem_tokens = [stem_token for stem_token in stem_tokens]
    temp_refinedques = ' '.join(stem_tokens)
    return temp_refinedques


def extractQues():
    global userTopics
    p = None
    JsonDict={}
    JsonDict=load_obj("topic_dictionary.pkl")
    #for root, directories, files in os.walk("/home/saurabh/IR_Project/quora_dataset"):
    for root, directories, files in os.walk("/home/saurabh/IR_Project/small_set"):
        usertopiclist = []

        for filename in files:

            p=root.split('/')[-1]
            filename = os.path.join(root, filename)
            f = open(filename, 'r')
            filecontent = f.read()
            soup = BeautifulSoup(filecontent)
            try:
                mainTag = soup.find('div', attrs={'class': 'header'})
                mainSoup = BeautifulSoup(str(mainTag))
                titleTag = mainSoup.find('span', attrs={'class': 'rendered_qtext'})
                detailsTag = mainSoup.find('div', attrs={'class': 'question_details'})
                topicTag = mainSoup.findAll('span', attrs={'class': 'TopicNameSpan TopicName'})
                [s.extract() for s in detailsTag('a')]
            except:
                print "No question"

            filetopiclist = []
            for topic in topicTag:
                if topic:
                    refined_topic = re.sub('<.*?>', '', str(topic))
                    print topic.text
                    try:
                        id1=JsonDict[refined_topic]
                        filetopiclist.append(id1)
                    except:
                        print ' '
            filetopiclist = list(set(filetopiclist))
            usertopiclist.extend(filetopiclist)   # Python is fun
            question = str(titleTag) + str(detailsTag)
            refined_ques = re.sub('<.*?>', '', str(question))
            refined_ques = refined_ques.replace("'", "")
            refined_ques = refined_ques.replace(".", " ")
            final_refined_ques = processQuestion(refined_ques)
            fname= quesDirname+p+'.txt'
            f = open(fname, 'a')
            f.write(final_refined_ques)
            f.close()
            userTopics[p] = usertopiclist


def calculateScores():
    output = run_command('./PersonalityRecognizer -i ' + quesDirname + ' -d -t 2 -m 4')

    scorefile = "/home/saurabh/IR_Project/scores_output"
    f = open(scorefile, 'w')
    f.write(output)
    f.close()
    data = []

    with open(scorefile) as f:
        for line in f:
            if re.match(r'\w*.txt', line):
                lineList = line.split()
                print lineList
                userid = re.sub('\.txt$', '', lineList[0])
                lineList = lineList[1:]
                lineList = [float(x) for x in lineList]
                userScores[userid] = lineList
    save_obj(userScores, "userScores.pkl")


def calcuateSimilarity(userId):
    if os.path.isfile("userScores.pkl"):
         userScores = load_obj("userScores.pkl")
    similarity = {}
    data1 = userScores[userId]
    for user in userScores.keys():
        data2 = userScores[user]
        result = 1 - spatial.distance.cosine(data1, data2)
        similarity[user] = result

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:100])
    if userId in similarUsers:
        similarUsers.pop(userId, None)
    else:
        minKey = min(similarUsers, key=similarUsers.get)
        similarUsers.pop(minKey, None)
    for user in similarUsers:
        if user != userId:
            print user


def calcuateTopicSimilarity(userId):
    if os.path.isfile("userTopics.pkl"):
         userTopics = load_obj("userTopics.pkl")
    similarity = {}
    print "userTopics"
    print userTopics
    data1 = userTopics[userId]
    print "Vector 1 for cosine sim"
    print data1
    for user in userTopics.keys():
        data2 = userTopics[user]
        result = 1 - spatial.distance.cosine(data1, data2)
        similarity[user] = result

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:6])
    if userId in similarUsers:
        similarUsers.pop(userId, None)
    else:
        minKey = min(similarUsers, key=similarUsers.get)
        similarUsers.pop(minKey, None)
    for user in similarUsers:
        if user != userId:
            print user


def createGraph():
    G = nx.Graph()
    edge_path = "./Topic_Hierarchy_Edge_List.txt"
    with open(edge_path) as fp:
        for line in fp:
            parts = line.split()
            part1 = int(parts[0])
            part2 = int(parts[1])
            G.add_edge(part1,part2)

    print "Nodes and Edges read.."
    largest_cc = max(nx.connected_components(G), key=len)
    G_new = nx.subgraph(G,largest_cc)

    nodes_level = extract_nodes_at_level(G_new, 90223, level=2)
    print "Nodes at level are: ", len(nodes_level)
    print nodes_level
    save_obj(G_new, "graph.pkl")
    save_obj(nodes_level, "levelNodes.pkl")


def readJSON():
    with open("data.json") as json_file:
        json_data = json.load(json_file)

    save_obj(json_data, "topic_dictionary.pkl")


def preProcessData():
    try:
        shutil.rmtree(quesDirname)
    except:
        print "No directory"
    os.makedirs(quesDirname)
    readJSON()
    extractQues()
    createGraph()
    #calculateScores()


if __name__ == "__main__":
    preProcessData()
    userTopicDict = {}
    print 'after graph created'
    for i in range(1000):
        try:
            # if userTopics[str(i)]:
            #     print userTopics[str(i)]
            if userTopics[str(i)]:
                print "Calling topicHierarchy"
                userTopicDict[str(i)] = TopicHierarchy(userTopics[str(i)])
        except:
            continue
    save_obj(userTopicDict,"userTopics.pkl")
    calcuateTopicSimilarity("3")
