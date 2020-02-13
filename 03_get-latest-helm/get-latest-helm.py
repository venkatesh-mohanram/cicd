import requests
from requests.auth import HTTPBasicAuth
import json
import sys, getopt

artifactoryhost = 'https://artifactory.xxx.com'
repo = 'productng-helm-local'

def getList(artifactoryhost, repo, helmname): 
        r = requests.get(
                         url= artifactoryhost + '/api/search/artifact?name=' + helmname + '&repos=' + repo
                        )
        artifactory_res = r.json()
        #print(json.dumps(artifactory_res, indent=4, sort_keys=True))
        return artifactory_res["results"]

def getLatest(results):
    allVersions = []
    for result in results:
        allVersions.append(result["uri"])
    allVersions.sort()
    if (len(allVersions) > 0):
        return allVersions[len(allVersions) - 1]
    else:
        return ""        

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hn:",["helmName="])
    except getopt.GetoptError:
        print ('python get-latest-helm.py -n <helm_name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('python get-latest-helm.py -n <helm_name>')
            sys.exit()
        elif opt in ("-n", "--helmName"):
            helm_name = arg
            #print ('Helm Name is :' + helm_name)
    
    latestVersion =  getLatest(getList(artifactoryhost, repo, helm_name))
    exit(latestVersion)

if __name__ == "__main__":
    main(sys.argv[1:])
