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
    #print sorted_x
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
    #print closest_node_list

    for each_node in list_node:
        try:
            distance = nx.shortest_path_length(Graph,source = node, target= each_node)
            #print "distance" + str(distance)
        except Exception as e:
            #print "no distance",node,each_node
            #print e
            continue
        if distance < closest_distance:
            #print "Found a node with shorter distance"
            closest_node_list = [each_node]
            closest_single_node = each_node
            closest_distance = distance
        elif distance == closest_distance:
            closest_node_list.append(each_node)

    return closest_node_list

nodes_level = []


def TopicHierarchy(user_topic_list):
    print "user_topic_list"
    print user_topic_list
    user_topic_dict = {}
    user_list = [0 for x in range(len(nodes_level))]
    #print 'user_topic_list' + user_topic_list
    print user_topic_list
    for usertopic in user_topic_list:
        node_list = nearest_node_in_list(G_new, usertopic, nodes_level)
        #print "Nodes nearest to " + usertopic + " are:"
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

# walk_dir = "/home/saurabh/IR_Project/quora_dataset"
#
# root, subdirs, files = os.walk(walk_dir)
# print root

userScores = {}
userTopics = {}

stop = stopwords.words('english')
stop.append(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', ' '])

'''
class user:

    def __init__(self, userid, extravert, emotional, agreeable, conscientious, experience):
        self.userid = userid
        self.extravert = extravert
        self.emotional = emotional
        self.agreeable = agreeable
        self.conscientious = conscientious
        self.experience = experience

    def __str__(self):
        return self.userid  + self.extravert + self.emotional + self.agreeable + self.conscientious + self.experience

    def __repr__(self):
        return self.userid  + self.extravert + self.emotional + self.agreeable + self.conscientious + self.experience
'''

quesDirname = "/home/saurabh/IR_Project/user_ques_Xt/"
topicDirname = "/home/saurabh/IR_Project/user_topic_Xt/"


def processQuestion(temp_refinedques):
    temp_refinedques = unicode(temp_refinedques, errors='ignore')
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(temp_refinedques)
    tokens = [i for i in tokens if i not in stop]
    tokens = list(set(tokens))
    stemmer = PorterStemmer()
    #stem_tokens = [stemmer.stem(token.decode('utf-8')) for token in tokens]
    #stem_tokens = [stem_token.encode('utf-8') for stem_token in stem_tokens]
    stem_tokens = [stemmer.stem(token) for token in tokens]
    stem_tokens = [stem_token for stem_token in stem_tokens]
    temp_refinedques = ' '.join(stem_tokens)
    return temp_refinedques


def extractQues():
    global userTopics
    p = None
    JsonDict={}
    JsonDict=load_obj("topic_dictionary.pkl")
    for root, directories, files in os.walk("/home/saurabh/IR_Project/quora_dataset"):
    #for root, directories, files in os.walk("/home/saurabh/IR_Project/small_set"):
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
                    #usertopiclist.append(topic.text)

                    #filetopiclist.append(topic.text)

                    #filetopiclist.append(refined_topic)
            filetopiclist = list(set(filetopiclist))
            usertopiclist.extend(filetopiclist)   # Python is fun
            #print "User topic list"
            #print usertopiclist

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
    #output = run_command('./PersonalityRecognizer -i test.txt -t 2 -m 4')

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

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:6])
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

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:3])
    if userId in similarUsers:
        similarUsers.pop(userId, None)
    else:
        minKey = min(similarUsers, key=similarUsers.get)
        similarUsers.pop(minKey, None)
    for user in similarUsers:
        if user != userId:
            print user


def createGraph():
    global G_new
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
    #print "here",nearest_node_in_list(G_new, 214224,[1,3,110611,2,240414])
    global nodes_level
    nodes_level = extract_nodes_at_level(G_new, 90223, level = 2)
    #nodes_level = extract_nodes_at_level(G_new, 2, 2)
    print "Nodes at level are: ",len(nodes_level)
    #print "Node ids"
    print nodes_level
    save_obj(G_new,"graph.pkl")


def readJSON():
    with open("data.json") as json_file:
        json_data = json.load(json_file)

    save_obj(json_data, "topic_dictionary.pkl")
    # for key, value in json_data.iteritems():
    #         print key, value


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
            #print "Calling for user " + str(i) + "======================================="
            if userTopics[str(i)]:
                #print "Calling topicHierarchy"
                userTopicDict[str(i)] = TopicHierarchy(userTopics[str(i)])
            #print "Completed for user " + str(i) + "======================================="
        except:
            print "Completed with error for user " + str(i) + "======================================="
            continue
    print 'After all call completed'
    save_obj(userTopicDict,"userTopics.pkl")
    calcuateTopicSimilarity("3")