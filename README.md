# QuoraFolloweeRecommendation

* input data → web pages of questions of users
* output → users to follow, ranked
* two process
* personality based recommendation
* topic interest based recommendation
* intermediate data stored as json
* in topic hierarchy, for each node, find base topics at some level
* use networkx library to travel topic hierarchy
* find sort path(s) to root
* and find nodes at level in the ans
* other nodes which have the same nodes in this level
* and are closest means they posses similar interest in topics
* networkx is python library for complex networks
* personality recognizer module
* 5 vector personality test
* 0 to 7 score
* Linguistic Inquiry and Word Count → LIWC
* personality recognizer 
* based on words used by user, find his intent or personality
* to do combination → 1st get results based on personality scores
* rank them based on topic hierarchy
* topic hierarchy
* topic tags
