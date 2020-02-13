import requests
from requests.auth import HTTPBasicAuth
import json
import subprocess 


def getTags(artifactoryhost, repo, imagename, username, apikey): 
	r = requests.get(
		url='https://' + artifactoryhost + '/api/docker/' + repo + '/v2/' + imagename + '/tags/list',
		auth=HTTPBasicAuth(username,apikey))
	artifactory_res = r.json()
	print(json.dumps(artifactory_res, indent=4, sort_keys=True))
	return artifactory_res["tags"]

def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def dockerLogin(username, password, registry):
	subprocess.call(["docker", "login", "-u", username, "-p", password, registry])
    
def dockerLogout(registry):
	subprocess.call(["docker", "logout", registry])    

def syncRepo(fromHost, fromRepo, fromImagename, fromTags, 
	     toRepo, toImagename): 
	for tag in fromTags:
		fromImageName = fromRepo + "." + fromHost + "/" + fromImagename + ":" + tag
		toImageName = toRepo + "/" + toImagename + ":" + tag
		cmds = '''
			echo '> Pulling the docker image {fromImage} ...';
			docker image pull {fromImage};
			echo '> Tagging the {fromImage} into {toImage} ...';
			docker tag {fromImage} {toImage};
			echo '> Pushing the image {toImage} ...';
			docker push {toImage};
			echo '> Deleting the images {fromImage} ...';
			docker image rm {fromImage};
			echo '> Deleting the image {toImage} ...';
			docker image rm {toImage};
			'''.format(fromImage=fromImageName, toImage=toImageName);
		subprocess_cmd(cmds);

def main():
	with open("config.json") as configfile:
		config = json.load(configfile);
	# Load all the artifactory details
	artifactory_host = config["artifactory-host"];
	artifactory_username = config["artifactory-username"];
	artifactory_api = config["artifactory-apikey"];
	# Load target repo details
	target_registry_host = config["target-registry-host"]
	target_registry_username = config["target-registry-username"]
	target_registry_password = config["target-registry-password"]

	# Login to docker
	dockerLogin(target_registry_username, target_registry_password, target_registry_host);

	for item in config["sync-repo"]:
		from_repo = item["from-repo"]
		from_imagename = item["from-imagename"]
		to_repo = item["to-repo"]
		to_imagename = item["to-imagename"]
		tags = getTags(artifactory_host, from_repo, from_imagename, artifactory_username, artifactory_api)
		syncRepo(artifactory_host, from_repo, from_imagename, tags, to_repo, to_imagename)

	# Logout from the docker    
	dockerLogout(target_registry_host)

main()


