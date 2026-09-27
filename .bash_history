clear
sudo apt update
clear
sudo apt update
clear
sudo apt install openjdk-21-jdk -y
clear
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc     https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc]"     https://pkg.jenkins.io/debian-stable binary/ | sudo tee     /etc/apt/sources.list.d/jenkins.list > /dev/null
/var/lib/jenkins/secrets/initialAdminPassword
clear
sudo apt-get update
sudo apt-get install fontconfig openjdk-21-jre
sudo apt-get install jenkins
/var/lib/jenkins/secrets/initialAdminPassword
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
sudo apt-get update
sudo apt-get install fontconfig openjdk-21-jre
sudo apt-get install jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
sudo systemctl status jenkins
clear
sudo apt install docker.io
sudo su  - 
sudo apt install docker.io
sudo SU - 
usermod -aG docker jenkins usermod -aG docker ubuntu systemctl restart docker
sudo usermod -aG docker jenkins
sudo usermod -aG docker ubuntu
sudo systemctl restart docker
sudo systemctl restart jenkins
[200~sudo usermod -aG docker jenkins
sudo usermod -aG docker ubuntu
sudo usermod -aG docker jenkins
sudo usermod -aG docker ubuntu
sudo systemctl restart docker
sudo systemctl restart jenkins
getent group docker
sudo systemctl restart jenkins
sudo systemctl status jenkins
sudo -u jenkins docker ps
docker ubuntu systemctl restart docker
su - jenkins
sudo -u jenkins docker ps
groups jenkins
sudo -u jenkins -s
docker ps
ssh -i /home/chapa/aws/jenkins-key.pem ubuntu@18.212.226.214
java -version
jenkins --version
git --version
python3 --version
mkdir ~/jenkins-demo
cd ~/jenkins-demo
nano app.py
nano requirements.txt
git init
git add .
git commit -m "Initial Jenkins demo application"
java -version
jenkins --version
git --version
python3 --version
cd ~/jenkins-demo
ls -la
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
sudo apt install python3-pytest
cd ~/jenkins-demo
pytest --version
pytest -v
ls -la
nano test_app.py
mv requirements.txt.save requirements.txt
ls -la
source venv/bin/activate
ls -la venv
ls -la venv/bin
rm -rf venv
python3 -m venv venv
source venv/bin/activate
rm -rf venv
python3 -m venv --help
cd ~/jenkins-demo
rm -rf venv
python3 -m venv venv
ls -l venv/bin/activate
source venv/bin/activate
rm -rf venv
ls -la
python3 -m venv venv
echo $?
cd ~/jenkins-demo
rm -rf venv
python3 -m venv venv
cd ~/jenkins-demo
rm -rf venv
python3 -m venv venv
sudo apt update
sudo apt install python3.14-venv
rm -rf ~/jenkins-demo/venv
cd ~/jenkins-demo
python3 -m venv venv
cd ~/jenkins-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v
cat -n requirements.txt
nano requirements.txt
cat requirements.txt
(venv) pip install -r requirements.txt
pip install -r requirements.txt
ls -la
pytest -v
pip install Flask pytest
python -c "import flask; print(flask.__version__)"
pytest -v
which python
which pip
which pytest
python -m pytest -v
git init
nano .gitignore
git status
cd ~/jenkins-demo
rm -rf ../.git
git init
git status
cat .gitignore
printf "venv/\n__pycache__/\n.pytest_cache/\n" > .gitignore
cat .gitignore
git status
git add .
git status
git commit -m "Initial Jenkins demo application"
git log --oneline
ls -la
git status
df -h /
df -h /tmp
mount | grep ' /tmp '
free -h
sudo mount -o remount,size=2G /tmp
df -h /tmp
df -h /
df -h /tmp
free -h
sudo systemctl restart jenkins
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
free -h
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
swapon --show
free -h
df -h
free -h
swapon --show
clear
df -h
free -h
swapon --show
df -h
sudo du -xh /var | sort -h | tail -30
free -h
swapon --show
sudo apt clean
df -h
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h
swapon --show
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo swapon --show
sudo apt clean
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
df -h
free -h
ps aux --sort=-%mem | head -15
systemctl cat jenkins
systemctl show jenkins --property=Environment
ps -p 67260 -o pid,cmd
sudo systemctl edit jenkins
sudo cat /etc/systemd/system/jenkins.service.d/override.conf
sudo ls -la /etc/systemd/system/jenkins.service.d/
sudo rm /etc/systemd/system/jenkins.service.d/.#override.confc4799a8b074addf3
sudo rm /etc/systemd/system/jenkins.service.d/.#override.confc4799a8b074addf3.save
sudo ls -la /etc/systemd/system/jenkins.service.d/
sudo systemctl edit jenkins
sudo cat /etc/systemd/system/jenkins.service.d/override.conf
sudo mkdir -p /etc/systemd/system/jenkins.service.d
sudo tee /etc/systemd/system/jenkins.service.d/override.conf > /dev/null <<'EOF'
[Service]
Environment="JAVA_OPTS=-Djava.awt.headless=true -Xms256m -Xmx512m"
EOF

sudo cat /etc/systemd/system/jenkins.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl cat jenkins
sudo cat /etc/systemd/system/jenkins.service.d/override.conf
sudo systemctl show jenkins --property=Environment
sudo journalctl -u jenkins -n 100 --no-pager
ps aux | grep '[j]ava'
free -h
sudo systemctl show jenkins --property=Environment
sudo tr '\0' '\n' < /proc/67260/cmdline
sudo -u jenkins jcmd 67260 VM.flags
sudo tr '\0' '\n' < /proc/67260/environ | grep -E 'JAVA_OPTS|JENKINS_JAVA'
sudo tr '\0' ' ' < /proc/67260/cmdline
sudo sh -c "tr '\0' '\n' < /proc/67260/environ | grep -E 'JAVA_OPTS|JENKINS_JAVA'"
sudo grep -n -E 'JAVA_OPTS|JENKINS_JAVA_OPTIONS|Xmx|exec.*java' /usr/bin/jenkins
sudo head -80 /usr/bin/jenkins
sudo -u jenkins jcmd 67260 VM.flags | grep -E 'InitialHeapSize|MaxHeapSize'
sudo sh -c "tr '\0' '\n' < /proc/67260/environ | grep -E 'JAVA_OPTS|JENKINS_JAVA'"
sudo grep -n -E 'JAVA_OPTS|JENKINS_JAVA_OPTIONS|Xmx|exec.*java' /usr/bin/jenkins
sudo sed -n '90,180p' /usr/bin/jenkins
sudo systemctl cat jenkins
sudo ls -la /etc/systemd/system/jenkins.service.d/
sudo cat /etc/systemd/system/jenkins.service.d/override.conf
sudo sed -n '90,180p' /usr/bin/jenkins
sudo systemctl show jenkins --property=Environment
sudo systemctl daemon-reload
sudo systemctl restart jenkins
systemctl is-active jenkins
pgrep -f '/usr/share/java/jenkins.war'
sudo tr '\0' ' ' < /proc/70000/cmdline
sudo tr '\0' ' ' < /proc/79944/cmdline
sudo -u jenkins jcmd 79944 VM.flags | grep -E 'InitialHeapSize|MaxHeapSize'
free -h
ps -o pid,%mem,rss,vsz,cmd -p 79944
sudo journalctl -u jenkins -n 30 --no-pager
sudo systemctl status jenkins --no-pager
sudo apt update
sudo apt install -y python3-pip
python3 -m pip --version
sudo apt update
sudo apt install -y python3-venv
python3 -m venv --help
sudo apt update
sudo apt install -y python3-venv
find ~ -name requirements.txt -o -name "*.py" 2>/dev/null
sudo find /var/lib/jenkins -name requirements.txt -o -name "*.py" 2>/dev/null
scp -r /path/to/my-python-project ubuntu@YOUR_EC2_PUBLIC_IP:/home/ubuntu/
find /home/ubuntu -maxdepth 4 -type f \( -name "requirements.txt" -o -name "*.py" \) 2>/dev/null
sudo cp -r /home/ubuntu/jenkins-demo/* /var/lib/jenkins/workspace/jenkins-demo/
sudo chown -R jenkins:jenkins /var/lib/jenkins/workspace/jenkins-demo
sudo -u jenkins ls -la /var/lib/jenkins/workspace/jenkins-demo
sudo -u jenkins ls -la /home/ubuntu/jenkins-demo
sudo chmod 755 /home/ubuntu
sudo chmod -R o+rX /home/ubuntu/jenkins-demo
sudo -u jenkins ls -la /home/ubuntu/jenkins-demo
docker --version
sudo systemctl status docker --no-pager
cd /home/ubuntu/jenkins-demo
nano Dockerfile
docker build -t jenkins-demo .
docker images
docker run -d --name jenkins-demo -p 5000:5000 jenkins-demo:latest
docker ps
curl http://localhost:5000
docker ps
curl http://localhost:5000
sudo -u jenkins docker ps
df -h
sudo du -sh /var/lib/jenkins/* 2>/dev/null | sort -h
docker system df
sudo du -sh /var/lib/docker 2>/dev/null
sudo apt clean
df -h /
docker system df
sudo du -sh /var/lib/docker 2>/dev/null
docker image prune -f
sudo apt clean
df -h /
sudo du -xhd1 / 2>/dev/null | sort -h
sudo du -xhd1 /var 2>/dev/null | sort -h
sudo du -xhd1 /var/lib 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/containerd 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/snapd 2>/dev/null | sort -h
sudo rm -rf /var/lib/snapd/cache/*
df -h /
snap list --all
sudo snap remove amazon-ssm-agent --revision=13009
sudo snap remove snapd --revision=26865
df -h /
snap list --all
sudo du -xhd1 / 2>/dev/null | sort -h
sudo du -xhd1 /var 2>/dev/null | sort -h
sudo du -xhd1 /usr 2>/dev/null | sort -h
sudo du -xhd1 /var/cache /var/log /var/lib 2>/dev/null | sort -h
sudo du -xhd2 /var/lib/containerd 2>/dev/null | sort -h | tail -30
sudo docker ps -a
sudo docker images
sudo du -xhd2 /var/lib/jenkins 2>/dev/null | sort -h | tail -30
sudo du -xhd2 /var/cache/jenkins 2>/dev/null | sort -h | tail -30
snap list --all
snap list --all | awk '/disabled/{print $1, $3}'
sudo apt clean
sudo du -xhd1 /usr/lib 2>/dev/null | sort -h
sudo docker system df 2>/dev/null
sudo docker images
sudo docker ps -a
sudo docker image prune
sudo du -xhd2 /var/lib/jenkins 2>/dev/null | sort -h | tail -30
sudo du -xhd2 /var/cache/jenkins 2>/dev/null | sort -h | tail -30
df -h /
df -ih /
sudo lsof +L1
sudo docker rmi node:16-alpine python:3.14-slim
sudo docker ps -a
snap list
sudo docker rmi node:16-alpine python:3.14-slim
df -h /
sudo du -xhd1 /var/lib/containerd 2>/dev/null | sort -h
sudo docker rmi node:16-alpine python:3.14-slim
sudo docker images
sudo docker context ls
sudo docker info | grep -E 'Docker Root Dir|Name'
sudo docker system df
sudo du -xhd1 /var/lib/docker 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/containerd 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/docker 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/containerd 2>/dev/null | sort -h
sudo systemctl stop jenkins
sudo rm -rf /var/cache/jenkins/war
sudo systemctl start jenkins
df -h /
snap list
snap list --all
df -h /
docker ps
curl http://localhost:5000
docker ps
curl http://localhost:5000
docker ps
curl http://localhost:5000
df -h
free -h
sudo apt clean
df -h /
sudo journalctl --vacuum-time=3d
df -h /
sudo du -xhd1 /var/lib/jenkins 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/containerd 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/snapd 2>/dev/null | sort -h
sudo rm -rf /var/lib/snapd/cache/*
df -h /
docker system df
docker image prune -f
df -h /
docker image prune -f
df -h /
docker images
docker ps
curl http://localhost:5000
cd /home/ubuntu/jenkins-demo
nano app.py
cat app.py
sudo apt clean
df -h /
sudo du -sh /var/lib/jenkins/workspace/*
sudo rm -rf /var/lib/jenkins/workspace/jenkins-demo
df -h /
docker image prune -a -f
df -h /
sudo docker system df
df -h /
docker ps
sudo docker image prune
sudo du -xhd1 / 2>/dev/null | sort -h
sudo du -xhd1 /var 2>/dev/null | sort -h
sudo du -xhd1 /var/lib/jenkins 2>/dev/null | sort -h
sudo journalctl --disk-usage
sudo du -sh /var/log/*
sudo du -xhd1 /var/lib 2>/dev/null | sort -h
sudo apt clean
sudo journalctl --vacuum-time=7d
sudo du -xhd1 /var/lib 2>/dev/null | sort -h
sudo apt clean
snap list
snap list --all
sudo du -xhd1 /var/lib/containerd 2>/dev/null | sort -h
sudo docker system df -v
df -h /
sudo docker image rm python:3.14-slim
sudo docker container prune
df -h /
sudo docker image rm python:3.14-slim
sudo docker container prune
df -h /
cd /home/ubuntu/jenkins-demo
ls
nano /home/ubuntu/jenkins-demo/app.py
cd /home/ubuntu/jenkins-demo
ls -la
sudo docker ps
curl http://localhost:5000
nano /home/ubuntu/jenkins-demo/app.py
cd /home/ubuntu/jenkins-demo
git add app.py
git commit -m "Test automatic deployment"
git push
