from flask import Flask, render_template, json, request, jsonify
import simplejson as json
import requests
import mysql.connector as mysql
import re
from bs4 import BeautifulSoup
from datetime import datetime
import random
import Levenshtein as lev
import os
import urllib
import hashlib

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "shopr",
    database = "shopr"
)
cursor = db.cursor()

def commonwords(str1,str2): 

    fused = []
    words1 = str1.title().split()
    words2 = str2.title().split()
    
    for word1 in words1:
        for word2 in words2:
            word1 = re.sub(r'^\W+$', '', word1)
            word2 = re.sub(r'^\W+$', '', word2)

            if word1.isalnum() and word2.isalnum():
                dist12 = lev.distance(re.sub(r'\W+', '', word1), re.sub(r'\W+', '', word2))
                print("[%s][%s] => [%s]" % (word1,word2,dist12))
                if dist12 == 0:
                    fused.append(word1 + 'x2')
                elif dist12 == 1:
                    fused.append(word1 + '|' + word2)

    return fused

# Driver program 
if __name__ == "__main__": 
    gtin = "9300652002652"
    query1 = """
        SELECT
            candidatetitle
        FROM productcandidates
        WHERE gtin = %s
        ORDER BY candidaterank asc
        limit 3
    """
    cursor.execute(query1,(gtin,))
    records = cursor.fetchall()

    str1 = records[0][0]
    str2 = records[1][0]
    str3 = records[2][0]

    fused1 = commonwords(str1,str2)
    if len(fused1) <= 1:
        fused2 = commonwords(str1,str3)
        fused1 = fused1 + fused2
    print(' '.join(fused1))
