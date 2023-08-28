import platform
import shutil
import pandas as pd
import subprocess
import os


class WebsiteBlocking:
    # Setup File locations
    openHostsFile = r"C:\Users\willq\PycharmProjects\Autopilot\hosts_unmodified.txt"
    blockHostsFile = r"C:\Users\willq\PycharmProjects\Autopilot\hosts_modified.txt"
    openHostsFileBackup = r"C:\Users\willq\PycharmProjects\Autopilot\hosts_unmodified_backup.txt"
    blockHostsFileBackup = r"C:\Users\willq\PycharmProjects\Autopilot\hosts_modified_backup.txt"
    # Setup initial banned websites list
    banData = pd.read_csv(r"C:\Users\willq\PycharmProjects\Autopilot\cleanedWebBlockData.csv")
    blockDomains = banData.domain.values.tolist()

    def __init__(self):
        self.hosts_path = self.determinePath()
        # self.dnsFlush = self.determineDNSFlush()
        self.banFile = self.createBanFile(self.generateBlockList())
        self.createFiles()

    @staticmethod
    def determinePath():
        if platform.system() == "Windows":
            hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
            return hosts_path
        elif platform.system() == "Linux":
            hosts_path = "/etc/hosts"
            return hosts_path
        else:
            print("Unsupported operating system")
            exit()

    def flushDns(self):
        try:
            subprocess.call(["ipconfig", "/flushdns"])
            print("DNS cache successfully flushed.")
        except OSError as e:
            print("Failed to flush DNS cache:", e)

    def createFiles(self):
        if not os.path.exists(self.blockHostsFile):
            with open(self.blockHostsFile, 'w') as f:
                pass
        if not os.path.exists(self.openHostsFile):
            with open(self.openHostsFile, 'w') as f:
                pass
        if not os.path.exists(self.blockHostsFileBackup):
            with open(self.blockHostsFileBackup, 'w') as f:
                pass
        if not os.path.exists(self.openHostsFileBackup):
            with open(self.openHostsFileBackup, 'w') as f:
                pass

    def generateBlockList(self):
        for i in range(len(self.blockDomains)):
            if self.blockDomains[i].startswith("www."):
                self.blockDomains.append(self.blockDomains[i].replace("www.", ""))
            else:
                self.blockDomains.append("www." + self.blockDomains[i])
        blockDomains = set(self.blockDomains)
        blockDomains = list(self.blockDomains)
        return blockDomains

    def createBanFile(self, domains):
        with open(self.blockHostsFile, 'w') as f:
            f.truncate()  # Clear the contents of the file
            for domain in domains:
                f.write('127.0.0.1 {}\n'.format(domain))
        f.close()

    def addWebsite(self, website):
        if website not in self.blockDomains:
            if website.startswith("www."):
                websiteAlt = website.replace("www.", "")
            else:
                websiteAlt = ("www." + website)
            self.blockDomains.append(website)
            self.blockDomains.append(websiteAlt)
            self.createBanFile(self.blockDomains)
        else:
            print("Website is already blocked")

    def removeWebsite(self, website):
        if website in self.blockDomains:
            if website.startswith("www."):
                websiteAlt = website.replace("www.", "")
            else:
                websiteAlt = ("www." + website)
            self.blockDomains.remove(website)
            self.blockDomains.remove(websiteAlt)
            self.createBanFile(self.blockDomains)
        else:
            print("Website is already unblocked")

    def activeBlocking(self):
        shutil.copy(self.blockHostsFile, self.blockHostsFileBackup)
        shutil.move(self.blockHostsFile, self.hosts_path)
        shutil.move(self.blockHostsFileBackup, self.blockHostsFile)
        self.flushDns()
        print("Blocking Active")
        print(self.blockDomains)

    def inactiveBlocking(self):
        shutil.copy(self.openHostsFile, self.openHostsFileBackup)
        shutil.move(self.openHostsFile, self.hosts_path)
        shutil.move(self.openHostsFileBackup, self.openHostsFile)
        self.flushDns()
        print("Blocking Inactive")


# Create an instance of the WebsiteBlocking class
testBlocker = WebsiteBlocking()

# Add a website to the block list
# testBlocker.addWebsite("example.com")

# Remove a website from the block list
# testBlocker.removeWebsite("example.org")

# Activate blocking
# testBlocker.activeBlocking()

# Deactivate blocking
# testBlocker.inactiveBlocking()
