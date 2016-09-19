import pickle
import os


def load_obj(name):
    name = "/home/saurabh/IR_Project/PersonalityRecognizer/" + name
    with open(name, 'rb') as f:
        return pickle.load(f)


def show():
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/graph.pkl"):
        print "File graph.pkl found"
        graph = load_obj("graph.pkl")
        print graph
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/levelNodes.pkl"):
        print "File levelNodes.pkl found"
        nodes_level = load_obj("levelNodes.pkl")
        print nodes_level
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/topic_dictionary.pkl"):
        print "topic_dictionary.pkl found"
        JsonDict=load_obj("topic_dictionary.pkl")
        #print JsonDict
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userScores.pkl"):
        print "File userScores.pkl found"
        userScores = load_obj("userScores.pkl")
        print userScores
    if os.path.isfile("/home/saurabh/IR_Project/PersonalityRecognizer/userTopicsVector.pkl"):
        print "File userTopicsVector.pkl found"
        userTopicsVector = load_obj("userTopicsVector.pkl")
        print userTopicsVector

if __name__=="__main__":
    show()