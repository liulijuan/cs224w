#!/usr/bin/env python
# coding=utf-8

from sym_matrix import SymMatrix
import mathutil
import math

query_index = {} 
url_index = {} 
link_out = {}  
link_in = {}  
query_common_count = SymMatrix() 
url_common_count = SymMatrix()  
query_sim_matrix = SymMatrix() 
url_sim_matrix = SymMatrix()  
query_damp = 0.8 
url_damp = 0.8  
evidence_size = 20
evidence = []  
query_weight_sum_variance = {}  
url_weight_sum_variance = {}  


def initEvidence():
    global evidence_size
    global evidence

    for i in range(evidence_size):
        evidence.append(0)
    evidence[0] = 0.5
    for i in range(1, evidence_size):
        evidence[i] = evidence[i - 1] + 1.0 / math.pow(2, i + 1)


def indexUserAndPosition(viewfile):
    global query_index
    global url_index
    query_count = 0
    url_count = 0
    for line in open(viewfile, "r"):
        arr = line.strip("\n").split()
        user = arr[0]
        if user not in query_index:
            query_index[user] = query_count
            query_count += 1
        for ele in arr[1:]:
            brr = ele.split(":")
            if len(brr) == 2:
                position = brr[0]
                if position not in url_index:
                    url_index[position] = url_count
                    url_count += 1


def readLink(viewfile):
    global link_out
    global link_in
    global url_index
    global query_index

    for line in open(viewfile, "r"):
        arr = line.strip("\n").split()
        user = arr[0]
        userid = query_index[user]
        url_count_collection = {}
        for ele in arr[1:]:
            brr = ele.split(":")
            if len(brr) == 2:
                position = brr[0]
                positionid = url_index[position]
                count = int(brr[1])
                url_count_collection[positionid] = count
                query_count_collection = {}
                if positionid in link_in:
                    query_count_collection = link_in[positionid]
                query_count_collection[userid] = count
                link_in[positionid] = query_count_collection
        link_out[userid] = url_count_collection


def initWeightSumAndVariance():
    global link_out
    global link_in

    for k, v in link_out.items():
        ps = []
        for p, c in v.items():
            ps.append(c)
        tup = mathutil.getSumAndVariance(ps)
        query_weight_sum_variance[k] = tup
    for k, v in link_in.items():
        us = []
        for u, c in v.items():
            us.append(c)
        tup = mathutil.getSumAndVariance(us)
        url_weight_sum_variance[k] = tup


def initSimMatrix():
    global link_out
    global link_in
    global query_sim_matrix
    global url_sim_matrix
    global query_common_count
    global url_common_count

    querynum = len(link_out)  
    urlnum = len(link_in) 

    query_sim_matrix = SymMatrix()
    url_sim_matrix = SymMatrix()
    query_common_count = SymMatrix()
    url_common_count = SymMatrix()

    for k1, v1 in link_out.items():  
        ps1 = []
        for p, c in v1.items():
            ps1.append(p)
        for k2, v2 in link_out.items():
            if k1 < k2:
                ps2 = []
                for p, c in v2.items():
                    ps2.append(p)
                common = mathutil.findCommonEle(
                    sorted(ps1), sorted(ps2)) 
                commonLen = len(common)
                if commonLen > 0:
                    query_common_count.set(k1, k2, commonLen)
                    query_sim_matrix.set(k1, k2, query_damp)
        query_sim_matrix.set(k1, k1, 1)  
		
    for k1, v1 in link_in.items():
        qry1 = []
        for u, c in v1.items():
            qry1.append(u)
        for k2, v2 in link_in.items():
            if k1 < k2:
                qry2 = []
                for u, c in v2.items():
                    qry2.append(u)
                common = mathutil.findCommonEle(sorted(qry1), sorted(qry2))
                commonLen = len(common)
                if commonLen > 0:
                    url_common_count.set(k1, k2, commonLen)
                    url_sim_matrix.set(k1, k2, url_damp)
            # print "(%d,%d)%f" % (k1, k2, url_sim_matrix.get(k1, k2)),
        url_sim_matrix.set(k1, k1, 1)
        # print


def updateSim():
    global link_out
    global link_in
    global query_common_count
    global query_sim_matrix
    global url_common_count
    global url_sim_matrix
    global query_damp
    global url_damp
    global evidence_size
    global evidence

    querynum = len(link_out) 
    urlnum = len(link_in)  

    for k1, v1 in link_out.items():  
        ps1 = []  
        for p, c in v1.items():
            ps1.append(p)
        for k2, v2 in link_out.items():
            commCount = query_common_count.get(k1, k2)  
            if commCount == None:
                commCount = 0
            
            if k1 < k2 and commCount > 0:
                
                ps2 = []  
                for p, c in v2.items():
                    ps2.append(p)
                if commCount > evidence_size:
                    commCount = evidence_size
                edv = evidence[commCount - 1]
                sum_part = 0.0
                for p1 in ps1:
                    for p2 in ps2:
                        sim_p1_p2 = url_sim_matrix.get(p1, p2)
                        if sim_p1_p2 == None:
                            continue
                        spread_p1 = math.pow(
                            math.e, -url_weight_sum_variance[p1][1])
                        weight_u1_p1 = link_out[k1][p1]
                        weight_u1_sum = query_weight_sum_variance[k1][0]
                        normalized_weight_u1_p1 = 1.0 * \
                            weight_u1_p1 / weight_u1_sum
                        spread_p2 = math.pow(
                            math.e, -url_weight_sum_variance[p2][1])
                        weight_u2_p2 = link_out[k2][p2]
                        weight_u2_sum = query_weight_sum_variance[k2][0]
                        normalized_weight_u2_p2 = 1.0 * \
                            weight_u2_p2 / weight_u2_sum
                        sum_part += spread_p1 * normalized_weight_u1_p1 * \
                            spread_p2 * normalized_weight_u2_p2 * sim_p1_p2
                new_sim = edv * query_damp * sum_part
                query_sim_matrix.set(k1, k2, new_sim)
            # print "(%d,%d)%f" % (k1, k2, query_sim_matrix.get(k1, k2)),
       # print

    for k1, v1 in link_in.items():  
        us1 = []  
        for u, c in v1.items():
            us1.append(u)
        for k2, v2 in link_in.items():
            commCount = url_common_count.get(
                k1, k2)  
            if commCount == None:
                commCount = 0
            
            if k1 < k2 and commCount > 0:
                # if k1 < k2:
                us2 = []  
                for u, c in v2.items():
                    us2.append(u)
                if commCount > evidence_size:
                    commCount = evidence_size
                edv = evidence[commCount - 1]
                sum_part = 0.0
                for u1 in us1:
                    for u2 in us2:
                        sim_u1_u2 = query_sim_matrix.get(u1, u2)
                        if sim_u1_u2 == None:
                            continue
                        spread_u1 = math.pow(
                            math.e, -query_weight_sum_variance[u1][1])
                        weight_p1_u1 = link_in[k1][u1]
                        weight_p1_sum = url_weight_sum_variance[k1][0]
                        normalized_weight_p1_u1 = 1.0 * \
                            weight_p1_u1 / weight_p1_sum
                        spread_u2 = math.pow(
                            math.e, -query_weight_sum_variance[u2][1])
                        weight_p2_u2 = link_in[k2][u2]
                        weight_p2_sum = url_weight_sum_variance[k2][0]
                        normalized_weight_p2_u2 = 1.0 * \
                            weight_p2_u2 / weight_p2_sum
                        sum_part += spread_u1 * normalized_weight_p1_u1 * \
                            spread_u2 * normalized_weight_p2_u2 * sim_u1_u2
                new_sim = edv * url_damp * sum_part
                url_sim_matrix.set(k1, k2, new_sim)
            # print "(%d,%d)%f" % (k1, k2, url_sim_matrix.get(k1, k2)),
        # print


def simrank(linkfile, iteration):
    initEvidence()
    indexUserAndPosition(linkfile)
    readLink(linkfile)
    initWeightSumAndVariance()
    print "iteration 0:"
    initSimMatrix()
    print
    for i in range(iteration):
        print "iteration %d:" % (i + 1)
        updateSim()
        print


def printResult(sim_query_file, sim_url_file):
    global url_sim_matrix
    global query_sim_matrix
    global link_out
    global link_in
    querynum = len(link_out) 
    urlnum = len(link_in)  

    f_out_user = open(sim_query_file, "w")
    for i in range(querynum):
        f_out_user.write(str(i) + "\t")
        neighbour = []
        for j in range(querynum):
            if i != j:
                sim = query_sim_matrix.get(i, j)
                if sim == None:
                    sim = 0
                if sim > 0:
                    neighbour.append((j, sim))
        
        neighbour = sorted(
            neighbour, cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
        for (u, sim) in neighbour:
            f_out_user.write(str(u) + ":" + str(sim) + "\t")
        f_out_user.write("\n")
    f_out_user.close()

    
    f_out_position = open(sim_url_file, "w")
    for i in range(urlnum):
        f_out_position.write(str(i) + "\t")
        neighbour = []
        for j in range(urlnum):
            if i != j:
                sim = url_sim_matrix.get(i, j)
                if sim == None:
                    sim = 0
                if sim > 0:
                    neighbour.append((j, sim))
        neighbour = sorted(
            neighbour, cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
        for (p, sim) in neighbour:
            f_out_position.write(str(p) + ":" + str(sim) + "\t")
        f_out_position.write("\n")
    f_out_position.close()

def findCommonEle(list1,list2):
    rect=[]
    length1=len(list1)
    length2=len(list2)
    idx1=0
    idx2=0
    while idx1<length1 and idx2<length2:
        ele1=list1[idx1]
        ele2=list2[idx2]
        if ele1==ele2:
            rect.append(ele1)
            idx1+=1
            idx2+=1
        elif ele1<ele2:
            idx1+=1
        else:
            idx2+=1
    return rect

def getSumAndVariance(li):
    assert len(li)>0
    total=0.0
    sumSquare=0.0
    for ele in li:
        total+=ele
        sumSquare+=ele*ele
    mean=total/len(li)
    variance=sumSquare/len(li)-mean*mean
    return (total,variance)

	
if __name__ == '__main__':
    linkfile = "../data/query-url-graphdata.tsv"
    sim_query_file = "../data/querySim.tsv"
    sim_url_file = "../data/querySim.tsv"
    simrank(linkfile, 5)
    printResult(sim_query_file, sim_url_file)