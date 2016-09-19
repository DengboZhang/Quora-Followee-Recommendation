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
import web
from web import form

user=""
question=""


#=================================================


f = []


def extract_nodes_at_level(G, root, level):

    x = nx.shortest_path_length(G, root)
    sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse= True)
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
            distance = nx.shortest_path_length(Graph,source=node, target=each_node)
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
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/graph.pkl"):
        print "File graph.pkl found"
        graph = load_obj("graph.pkl")
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/levelNodes.pkl"):
        print "File levelNodes.pkl found"
        nodes_level = load_obj("levelNodes.pkl")
    print "user_topic_list"
    print user_topic_list
    user_topic_dict = {}
    userVector = [0 for x in range(len(nodes_level))]
    for usertopic in user_topic_list:
        node_list = nearest_node_in_list(graph, usertopic, nodes_level)
        print 'node list'
        print node_list
        for node in node_list:
            try:
                userVector[nodes_level.index(node)] += 1
            except:
                print "Skipping vector update for " + str(node)
    print 'userVector vector'
    print userVector
    return userVector


def save_obj(obj, name):
    name = "/home/saurabh/IR_Project/PersonalityRecognizer/" + name
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    name = "/home/saurabh/IR_Project/PersonalityRecognizer/" + name
    with open(name, 'rb') as f:
        return pickle.load(f)


def run_command(cmd):
    cmd = shlex.split(cmd)
    return subprocess.check_output(cmd).decode('ascii')


userTopics = {}
userList = []
stop = stopwords.words('english')
stop.append(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', ' '])
quesDirname = "/home/saurabh/IR_Project/user_ques_Xt/"
topicDirname = "/home/saurabh/IR_Project/user_topic_Xt/"
queryDirname = "/home/saurabh/IR_Project/query/"


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
    global userList
    p = None
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/topic_dictionary.pkl"):
        print "topic_dictionary.pkl found"
        JsonDict=load_obj("topic_dictionary.pkl")
    for root, directories, files in os.walk("/home/saurabh/IR_Project/quora_dataset"):
    #for root, directories, files in os.walk("/home/saurabh/IR_Project/small_set"):
        usertopiclist = []

        for filename in files:

            p = root.split('/')[-1]
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
                continue

            print "After extracting the tags"
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
            userList.append(p)
    userList = list(set(userList))
    save_obj(userList,"userList.pkl")


def createTopicVector():
    userTopicVector = {}
    for user in userList:
        if userTopics[user]:
            userTopicVector[user] = TopicHierarchy(userTopics[user])
    save_obj(userTopicVector, "userTopicsVector.pkl")


def calculateScores():
    userScores = {}
    output = run_command('/home/saurabh/IR_Project/PersonalityRecognizer/PersonalityRecognizer -i ' + quesDirname + ' -d -t 2 -m 4')
    scorefile = "/home/saurabh/IR_Project/scores_output"
    f = open(scorefile, 'w')
    f.write(output)
    f.close()

    with open(scorefile) as f:
        for line in f:
            if re.match(r'\w*.txt', line):
                lineList = line.split()
                print lineList
                userid = re.sub('\.txt$', '', lineList[0])
                lineList = lineList[1:]
                lineList = [float(x) for x in lineList]
                userScores[userid] = lineList
    print "Saving userScores as"
    print userScores
    save_obj(userScores, "userScores.pkl")


def calcuateSimilarity(userId):
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userScores.pkl"):
        print "File userScores.pkl found"
        userScores = load_obj("userScores.pkl")
    similarity = {}
    print "UserScores"
    print userScores
    data1 = userScores[userId]
    for user in userScores.keys():
        data2 = userScores[user]
        result = 1 - spatial.distance.cosine(data1, data2)
        similarity[user] = result

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:11])
    if userId in similarUsers:
        similarUsers.pop(userId, None)
    else:
        minKey = min(similarUsers, key=similarUsers.get)
        similarUsers.pop(minKey, None)
    print "Returning similar users as"
    print similarUsers
    for user in similarUsers:
        if user != userId:
            print user
    return similarUsers


def calcuateTopicSimilarity(userId):
    userTopicsVector = {}
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userTopicsVector.pkl"):
        print "File userTopicsVector.pkl found"
        userTopicsVector = load_obj("userTopicsVector.pkl")
    similarity = {}
    print "userTopicsVector"
    print userTopicsVector
    data1 = userTopicsVector[userId]
    print "Vector 1 for cosine sim"
    print data1
    for user in userTopicsVector.keys():
        data2 = userTopicsVector[user]
        result = 1 - spatial.distance.cosine(data1, data2)
        similarity[user] = result

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:11])
    if userId in similarUsers:
        similarUsers.pop(userId, None)
    else:
        minKey = min(similarUsers, key=similarUsers.get)
        similarUsers.pop(minKey, None)
    for user in similarUsers:
        if user != userId:
            print user
    return similarUsers


def calcuateTopicSimilarityFromSimilarUsers(userId,list):
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userTopicsVector.pkl"):
        print "File userTopicsVector.pkl found"
        userTopicsVector = load_obj("userTopicsVector.pkl")
    similarity = {}
    print "userTopicsVector"
    print userTopicsVector
    data1 = userTopicsVector[userId]
    print "Vector 1 for cosine sim"
    print data1
    print "UserList is"
    print userList
    for user in list:
        try:
            data2 = userTopicsVector[user]
            result = 1 - spatial.distance.cosine(data1, data2)
            similarity[user] = result
        except:
            continue

    similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:11])
    if userId in similarUsers:
        similarUsers.pop(userId, None)
    else:
        minKey = min(similarUsers, key=similarUsers.get)
        similarUsers.pop(minKey, None)
    for user in similarUsers:
        if user != userId:
            print user
    return similarUsers


def createGraph():
    G = nx.Graph()
    edge_path = "/home/saurabh/IR_Project/PersonalityRecognizer/Topic_Hierarchy_Edge_List.txt"
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
    with open("/home/saurabh/IR_Project/PersonalityRecognizer/data.json") as json_file:
        json_data = json.load(json_file)

    save_obj(json_data, "topic_dictionary.pkl")


def preProcessData():
    print "Preprocessing Data"
    try:
        shutil.rmtree(quesDirname)
        shutil.rmtree(queryDirname)
    except:
        print "No directory"
    os.makedirs(quesDirname)
    os.makedirs(queryDirname)
    readJSON()
    createGraph()
    extractQues()
    calculateScores()
    createTopicVector()
#===================================================



def calculateQueryScore():
    output = run_command('/home/saurabh/IR_Project/PersonalityRecognizer/PersonalityRecognizer -i ' + queryDirname + ' -d -t 2 -m 4')
    queryscorefile = "/home/saurabh/IR_Project/query_scores_output"
    f = open(queryscorefile, 'w')
    f.write(output)
    f.close()

    with open(queryscorefile) as f:
        for line in f:
            if re.match(r'\w*.txt', line):
                lineList = line.split()
                print lineList
                userid = re.sub('\.txt$', '', lineList[0])
                lineList = lineList[1:]
                lineList = [float(x) for x in lineList]
                return lineList


def getMaxTopic(user):
    max = -1
    maxtopic = -1
    for i in range(48):
        if(d1[user][i] * topic[i] > max):
            max = d1[user][i] * topic[i]
            maxtopic = i
    return maxtopic


def getMaxTrait(user):
    max = -1
    trait = -1
    for i in range(5):
        if(d1[user][i] * personality[i] > max):
            max = d1[user][i] * personality[i]
            trait = i
    return trait



render = web.template.render('templates/')

urls = ('/', 'index', '/result', 'result', '/queryresult', 'queryresult','/personalitystatistic.html', 'personalitystatistic','/topicstatistic.html', 'topicstatistic','/topicresult', 'topicresult','/bothresult', 'bothresult')
app = web.application(urls, globals())

myform = form.Form(
    form.Textbox("User"),
#        form.notnull,
#        form.regexp('\d+', 'Must be a digit')),
#        form.Validator('Must be more than 5', lambda x:int(x)>5),
    form.Textarea('Question'),
    form.Checkbox("personality", description="personality", class_="standard", value="Based on Personality"),
    form.Checkbox("topic", description="topic", class_="standard", value="Based on Content"),
    form.Checkbox("topic_personality", description="topic_personality", class_="standard", value="Based on both"))



class index:
    def GET(self):
        form = myform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        print "Calling form"
        uList = []
        if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userList.pkl"):
            print "File userList.pkl found"
            uList = load_obj("userList.pkl")

        return render.formtest(form, uList)

    def POST(self):
        form = myform()
        if not form.validates():
            return render.formtest(form)
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            global user
            global question
            user = form.d.User
            question = form.d.Question
            if form['personality'].checked:
                if user:
                    raise web.seeother('/result')
                elif question:
                    raise web.seeother('/queryresult')
                else:
                    raise web.seeother("/")
            if form['topic'].checked:
                raise web.seeother('/topicresult')
            if form['topic_personality'].checked:
                raise web.seeother('/bothresult')




class result:
    def GET(self):
        list1 = calcuateSimilarity(user)
        list3 = calcuateTopicSimilarityFromSimilarUsers(user, list1)
        print "List of similar users"
        print list1
        print list3
        if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userScores.pkl"):
            print "File userScores.pkl found"
            userScores = load_obj("userScores.pkl")
        dict1 = {}
        for usr in list1:
            dict1[usr] = userScores[usr]
        #return render.result(dict1, list2, list3)
        myScore = userScores[user]
        return render.result(dict1, myScore)
        #return render.result(similarUsers)

    def POST(self):
        raise web.seeother("/")


class queryresult:
    def GET(self):
        #query_ques = processQuestion(question)
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(question)
        tokens = [i for i in tokens if i not in stop]
        tokens = list(set(tokens))
        stemmer = PorterStemmer()
        stem_tokens = [stemmer.stem(token) for token in tokens]
        stem_tokens = [stem_token for stem_token in stem_tokens]
        query_ques = ' '.join(stem_tokens)
        fname= queryDirname + 'query.txt'
        f = open(fname, 'w')
        f.write(query_ques)
        f.close()
        score = calculateQueryScore()
        print "Score"
        print score
        if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userScores.pkl"):
            print "File userScores.pkl found"
            userScores = load_obj("userScores.pkl")
        similarity = {}
        print "UserScores"
        print userScores
        for user in userScores.keys():
            data2 = userScores[user]
            result = 1 - spatial.distance.cosine(score, data2)
            similarity[user] = result
        similarUsers = dict(sorted(similarity.iteritems(), key=operator.itemgetter(1), reverse=True)[:11])
        dict1 = {}
        for usr in similarUsers:
            dict1[usr] = userScores[usr]
        myScore = userScores[user]
        return render.queryresult(dict1, myScore)
        #return render.queryresult(similarUsers)

    def POST(self):
        raise web.seeother("/")


class personalitystatistic:
    def GET(self):
        userid = web.cookies().get('userId')
        return render.personalitystatistic(userid)

    def POST(self):
        raise web.seeother("/")


class topicresult:
    def GET(self):
        topicVector = {}
        list2 = calcuateTopicSimilarity(user)
        if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userTopicsVector.pkl"):
            print "File userScores.pkl found"
            topicVector = load_obj("userTopicsVector.pkl")
        print "userTopicVector"
        print topicVector
        dict1 = {}
        for usr in list2:
            dict1[usr] = topicVector[usr]
        #return render.result(dict1, list2, list3)
        myVector = topicVector[user]
        #userid = web.cookies().get('userId')
        return render.topicresult(dict1, myVector)

    def POST(self):
        raise web.seeother("/")


class bothresult:
    def GET(self):
        userScores = {}
        topicVector = {}
        list1 = calcuateSimilarity(user)
        list3 = calcuateTopicSimilarityFromSimilarUsers(user, list1)
        if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userScores.pkl"):
            print "File userScores.pkl found"
            userScores = load_obj("userScores.pkl")
        if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userTopicsVector.pkl"):
            print "File userTopicsVector.pkl found"
            topicVector = load_obj("userTopicsVector.pkl")
        dict1 = {}
        for usr in list3:
            dict1[usr] = userScores[usr]
        dict2 = {}
        for usr in list3:
            dict2[usr] = topicVector[usr]

        #return render.result(dict1, list2, list3)
        myScore = userScores[user]
        myVector = topicVector[user]

        return render.bothresult(dict1, dict2, myScore, myVector)

    def POST(self):
        raise web.seeother("/")


class topicstatistic:
    def GET(self):
        userid = web.cookies().get('userId')
        return render.topicstatistic(userid)

    def POST(self):
        raise web.seeother("/")


if __name__=="__main__":
    web.internalerror = web.debugerror
    #preProcessData()
    app.run()
