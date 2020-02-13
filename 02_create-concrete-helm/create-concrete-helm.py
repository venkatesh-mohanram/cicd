import requests
from requests.auth import HTTPBasicAuth
import sys, getopt
import glob
import json
import yaml
import subprocess
from datetime import datetime

def getTags(artifactoryhost, repo, imagename, username, apikey): 
    r = requests.get(
                  url='https://' + artifactoryhost + '/api/docker/' + repo + '/v2/' + imagename + '/tags/list',
                  auth=HTTPBasicAuth(username,apikey))
    artifactory_res = r.json()
    #print(json.dumps(artifactory_res, indent=4, sort_keys=True))
    return artifactory_res["tags"]

def getLatest(tags):
    # Sort the tags in alphabetical order
    tags.sort()
    for i in tags:
        print(i)
    size = len(tags)
    return tags[size - 1]

def updateYaml(fileLocation):
    with open(fileLocation + "/config.json") as configfile:
        config = json.load(configfile)
    with open(fileLocation + "/values.yaml") as f:
        content = yaml.load(f)
        for mapping in config["mappings"]:
            microservice = mapping["microservice"]
            artifactoryImageName = mapping["artifactoryImageName"]
            latest_tag = getLatest(getTags("artifactory.xxx.com", "productng-docker-local", artifactoryImageName, "vemohanr", "AKCp5e3yELLbcgNgDh977RcUrHKN6rj2SgFBiJibeB4dLKj4E9Ttdcza9mkdy7jNnNYV3qyuF"))
            print ("Latest tag for " + microservice + " is " + latest_tag) 
            content[microservice]["image"] = content[microservice]["image"].split(':')[0] + ':' + latest_tag
    with open(fileLocation + "/values.yaml", "w") as f:
        yaml.dump(content, f)
#        print(yaml.dump(content))
def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print (proc_stdout)

def packageHelm(helmLocation):
    now = datetime.now()
    version = now.strftime("%y%m%d.%H%M")
    dirPath = helmLocation[:helmLocation.rfind('/')]
    chartName = helmLocation[len(dirPath) - len(helmLocation) + 1:]
    cmds = '''
            cd {dirPath}
            tar -czvf {chartName}-{version}.tgz {chartName}
            cd -
            '''.format(dirPath=dirPath, chartName=chartName, version=version)
    subprocess_cmd(cmds)

def publishHelm(helmLocation):
    path = helmLocation[:helmLocation.rfind('/')]
    chartName = helmLocation[len(path) - len(helmLocation) + 1:]
    path = path + "/*.tgz"
    print (path)
    print (chartName)
    for filename in glob.glob(path):
        print ("Found " + filename)
        with open(filename, 'rb') as helmZip:
            zipName = filename[filename.rfind('/'):]
            r = requests.put(
                    url='https://artifactory.xxx.com/productng-helm-local/product/' + chartName + zipName,
                    auth=HTTPBasicAuth('vemohanr', 'AKCp5e3yELLbcgNgDh977RcUrHKN6rj2SgFBiJibeB4dLKj4E9Ttdcza9mkdy7jNnNYV3qyuF'),
                    files={"archive" : (filename, helmZip)}
                    )
            print (r.json())
            print ("Helm chart published successfully")

def publishHelm2(helmLocation):
    path = helmLocation[:helmLocation.rfind('/')]
    chartName = helmLocation[len(path) - len(helmLocation) + 1:]
    path = path + "/*.tgz"
    print ("Path is " + path)
    print ("Chart name is " + chartName)
    for filename in glob.glob(path):
        print ("Found " + filename)
        zipName = filename[filename.rfind('/'):]
        r = requests.put(
                url='https://artifactory.xxx.com/productng-helm-local/product/' + chartName + zipName,
                auth=HTTPBasicAuth('vemohanr', 'AKCp5e3yELLbcgNgDh977RcUrHKN6rj2SgFBiJibeB4dLKj4E9Ttdcza9mkdy7jNnNYV3qyuF'),
                data = open(filename, 'rb').read()
                )
        print (r.json())
                    

def main(argv):
    helm_location = ''
    helm_name = ''
    try:
        opts, args = getopt.getopt(argv, "hl:",["helmLocation="])
    except getopt.GetoptError:
        print ('create_concrete_helm.py -l <helm_location>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('create_concrete_helm.py -l <helm_location>')
            sys.exit()
        elif opt in ("-l", "--helmLocation"):
            helm_location = arg
        elif opt in ("-n", "--helmName"):
            helm_name = arg
            
    # Update the values.yaml with the latest image tag available in the artifactory.xxx       
    updateYaml(helm_location)
    # Package the helm and create a .tgz file
    packageHelm(helm_location)
    # Publish the .tgz file to artifactory helm repo
    publishHelm2(helm_location)

if __name__ == "__main__":
    main(sys.argv[1:])
