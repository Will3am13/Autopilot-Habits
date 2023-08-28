import platform
import shutil
import pandas as pd
import subprocess


if platform.system() == "Windows":
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    dnsFlush = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
elif platform.system() == "Linux":
    hosts_path = "/etc/hosts"
    dnsFlush = subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], capture_output=True, text=True)
else:
    print("Unsupported operating system")
    exit()

openHostsFile = r"C:\Users\willq\Downloads\hosts_unmodified.txt"
blockHostsFile = r"C:\Users\willq\Downloads\hosts_modified.txt"
openHostsFileBackup = r"C:\Users\willq\Downloads\hosts_unmodified_backup.txt"
blockHostsFileBackup = r"C:\Users\willq\Downloads\hosts_modified_backup.txt"
domainData = pd.read_csv(r"C:\Users\willq\PycharmProjects\pythonProject\domainNoDupe.csv")
# Clean Data
domainData = domainData.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'])
domainData.Ban = domainData.Ban.astype(bool)
# Create ban list dataframe, domains that are set to be banned (True)
banData = domainData[domainData.Ban == True]
banData = banData.dropna()
# Make a list of blocked domains
blockDomains = banData.domain.values.tolist()


# Debug/print for me to visualize
# print(banData.head(10))
# print(domainData.tail(10))
# print(domainData.head(10))
# print(blockDomains)

def removeDupes(data):
    data = set(data)
    data = list(data)
    return data


# Make sure both www. and naked url are in list
def createBanList():
    for i in range(len(blockDomains)):
        if blockDomains[i].startswith("www."):
            blockDomains.append(blockDomains[i].replace("www.", ""))
        else:
            blockDomains.append("www." + blockDomains[i])
    removeDupes(blockDomains)
    return blockDomains


# print(blockDomains)


# Take the block domains list and write into the host text file
# 127.0.0.1 www.youtube.com
# 127.0.0.1 youtube.com
def createBanFile(blockHostsFile):
    with open(blockHostsFile, 'w') as f:
        for domain in blockDomains:
            f.write('127.0.0.1 {}\n'.format(domain))
    return blockHostsFile


def addBanList(website):
    if website not in blockDomains:
        if website.startswith('www.'):
            blockDomains.append(website)
            blockDomains.append(website.replace('www.', ''))
        else:
            blockDomains.append(website)
            blockDomains.append('www.' + website)
        return createBanFile(blockHostsFile)
    else:
        return False


def removeBanList(website):
    if website in blockDomains:
        if website.startswith('www.'):
            websiteAlt = website.replace('www.', '')
        else:
            websiteAlt = ('www.' + website)
        blockDomains.remove(website)
        blockDomains.remove(websiteAlt)
        createBanFile(blockHostsFile)
        return blockHostsFile
    else:
        return False


def dnsClear():
    os = platform.system()
    if os == "Windows":
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
    elif os == "Linux" or os == "Darwin":
        subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], capture_output=True, text=True)
    else:
        print("DNS cache clearing not supported on this OS.")


def toggleMode(active):
    if active:
        dnsClear()
        shutil.copy(blockHostsFile, blockHostsFileBackup)
        shutil.move(blockHostsFile, hosts_path)
        shutil.move(blockHostsFileBackup, blockHostsFile)
        print("Blocking Active")
    elif not active:
        dnsClear()
        shutil.copy(openHostsFile, openHostsFileBackup)
        shutil.move(openHostsFile, hosts_path)
        shutil.move(openHostsFileBackup, openHostsFile)
        print("Blocking Inactive")


# print(blockDomains)
# createCal()
# Add a timer that toggles the mode every X minutes
# addBanList("twitter.com")
print(blockDomains)
# addBanList("hbomax.com")
# createBanList()
# removeBanList("cava.com")
# createBanFile(removeBanList("cava.com"))
# print(blockDomains)
toggleMode(True)
# createBanList()
# print(blockDomains)
# addBanList('facebook.com')
# createBanFile(blockHostsFile)
# toggleMode(False)
# Add a timer that toggles the mode every X minutes