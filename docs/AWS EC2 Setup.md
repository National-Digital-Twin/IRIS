**Repository:** `IRIS-data-cleanser`

**Description:** `Details steps to set up the pipeline on an EC2 instance`

**SPDX-License-Identifier:** OGL-UK-3.0

# AWS Initial Setup
# 	https://eu-west-2.console.aws.amazon.com/
# 	Sign in via root or IAM user
#   Go to https://eu-west-2.console.aws.amazon.com/ec2/v2/home?region=eu-west-2#LaunchInstances:
# 	EC2 > Instances > Launch an instance
#   - Name: `iris-data-cleansing-ec2`
# 	- Quick Start Image: `Ubuntu`
#   - AMI: `Ubuntu Server 22.04 LTS (HVM), SSD Volume Type (64-bit)`
# 	- Instance type: `t3.large` (2 vCPU, 8 GiB RAM, EBS storage, $0.0944 per hour, $2.2656/day, £12.69/week, £54.97/month)
# 	- Key pair: `iris-cleanser-key-pair`
#   - Security group: Select existing default security group (HTTP/HTTPS open anywhere, SSH open to my IP only)
#   - Storage: `50 GiB SSD (gb3) with 3000 IOPS` (storage type EBS, device name `/dev/sda1`, delete on termination, not encrypted, 125 throughput)

#	Might want to create a billing alert

# AWS CLI command `RunInstances`
```
{
  "MaxCount": 1,
  "MinCount": 1,
  "ImageId": "ami-0eb260c4d5475b901",
  "InstanceType": "t3.medium",
  "KeyName": "iris-cleanser-key-pair",
  "EbsOptimized": true,
  "BlockDeviceMappings": [
    {
      "DeviceName": "/dev/sda1",
      "Ebs": {
        "Encrypted": false,
        "DeleteOnTermination": true,
        "SnapshotId": "snap-0d487d397a4374e2a",
        "VolumeSize": 50,
        "VolumeType": "gp2"
      }
    }
  ],
  "NetworkInterfaces": [
    {
      "AssociatePublicIpAddress": true,
      "DeviceIndex": 0,
      "Groups": [
        "sg-064c76190d27756d1"
      ]
    }
  ],
  "TagSpecifications": [
    {
      "ResourceType": "instance",
      "Tags": [
        {
          "Key": "Name",
          "Value": "iris-data-cleansing-ec2"
        }
      ]
    }
  ],
  "PrivateDnsNameOptions": {
    "HostnameType": "ip-name",
    "EnableResourceNameDnsARecord": true,
    "EnableResourceNameDnsAAAARecord": false
  }
}
```

# Connect
chmod 400 ~/.ssh/iris-cleanser-key-pair.pem
ssh-add ~/.ssh/iris-cleanser-key-pair.pem
ssh {username@public-ipv4-dns.com}
screen
sudo apt-get update
sudo apt-get upgrade

# Create a swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo sh -c 'echo "/swapfile none swap sw 0 0" >> /etc/fstab'


# Install fzf
sudo apt install fzf
sudo apt show fzf
# Add to ~/.bash_profile
```
source /usr/share/doc/fzf/examples/key-bindings.bash
source /usr/share/doc/fzf/examples/completion.bash
```


# Install pyenv
curl https://pyenv.run | bash
# Add to ~/.bash_profile
export PATH="$HOME/.pyenv/bin:$PATH"
export PYENV_ROOT="$HOME/.pyenv"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv virtualenvwrapper
# Save & close
source ~/.bashrc


## Install git
sudo apt-get install git

# Create deploy key
ssh-keygen -t ed25519 -C "{deployment_email}"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
# Upload to Github repo as a deploy key

# Grab the repo
git clone git@github.com:National-Digital-Twin/IRIS-data-cleanser.git

# Install Python with pyenv
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm gettext libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev

cd ./IRIS-data-cleanser/
pyenv install $(cat .python-version)
pyenv shell $(cat .python-version)
python -m pip install --upgrade pip
python -m pip install virtualenvwrapper
git clone https://github.com/pyenv/pyenv-virtualenvwrapper.git $(pyenv root)/plugins/pyenv-virtualenvwrapper
source ~/.bashrc
source ~/.bash_profile
pyenv virtualenvwrapper

# Setup the virtualenv
mkvirtualenv -p python$(cat .python-version) $(cat .venv)
python -V
python -m pip install --upgrade pip

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
nano ~/.bash_profile
```
# Poetry
export PATH="/home/ubuntu/.local/bin:$PATH"

# Setup
workon IRIS
cd ~/IRIS-data-cleanser/
```
source ~/.bash_profile
poetry --version
poetry self update
poetry install --no-root

# Create templated .env for storing secrets
cp .env.template .env
direnv allow

# pytest
pytest


# Install aws cli
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install
# Configure AWS CLI
aws configure
# AWS Access Key ID [None]: SEE 1PASSWORD
# AWS Secret Access Key [None]: SEE 1PASSWORD
# Default region name [None]: eu-west-2
# Default output format [None]:
# List buckets
aws s3api list-buckets
# Read from a Bucket
aws s3api list-objects --bucket iris-data-cleanser-bucket
# Get object
aws s3api get-object --bucket iris-data-cleanser-bucket --key test.txt outputfile.txt
# Write to a bucket
aws s3api put-object --bucket iris-data-cleanser-bucket --key myfile.txt --body myfile.txt


# Install Docker
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce
# Test installation
sudo docker run hello-world
# Add user to the docker group to use Docker as a non-root user
sudo usermod -aG docker $USER
# Re-evaluate group membership
newgrp docker
# Now we can use Docker without sudo
# Run Docker on system startup
sudo systemctl enable docker
# Manually start Docker service
sudo systemctl start docker
# Download docker-compose binary
sudo curl -L "https://github.com/docker/compose/releases/download/2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker compose version


# Airbyte
# Source: https://docs.airbyte.com/deploying-airbyte/on-aws-ec2/
cd ~
mkdir airbyte && cd airbyte
wget https://raw.githubusercontent.com/airbytehq/airbyte/master/run-ab-platform.sh
chmod +x run-ab-platform.sh
nano .env
```
BASIC_AUTH_USERNAME=airbyte-iris-data-cleanser
BASIC_AUTH_PASSWORD=secure-password-in-1password-vault
```
./run-ab-platform.sh -b


# Add a Destination
# N.B. Ensure EC2 can see RDS ("Connected compute resources" under RDS instance on https://eu-west-2.console.aws.amazon.com/rds/home)
# - Destination name: `Postgres`
# - Host: `<credential>`
# - Port: `5432`
# - DB Name: `postgres`
# - Default Schema: `public`
# - User: `<credential>`
# - Password: `<credential>`


# Add a source
# - Go to Connector Builder
# - Import `os_places_api.yaml`, `isle-of-wight-domestic.yaml`, `certificates.yaml`

# How to delete a custom connector
# Source: https://github.com/airbytehq/airbyte/issues/27415
# Click to edit the connector -> in the URL you can find the connector id
docker exec -ti airbyte-db psql -U docker airbyte
update connector_builder_project set tombstone=true where "id"='<CONNECTOR_ID>';


# dbt
cd ~/IRIS-data-cleanser/c477_data_cleansing/
mkdir ~/.dbt/
nano ~/.dbt/profiles.yml
```
iris_data_cleansing:
  target: dev_with_fal
  outputs:
    dev_with_fal:
      type: fal
      db_profile: dev_postgres # This points to your main adapter
    dev_postgres:
      type: postgres
      host: <credential>
      user: <credential>
      password: <credential>
      dbname: postgres
      schema: public
      port: 5432
```
dbt debug
dbt deps
dbt seed --threads 8
# Run just one model using `dbt run --select <model_name>`


# Developing Airbyte Custom Python Source
## The Python module that queries the EPC Recommendations ZIP endpoint can be executed directly via CLI
cd ./airbyte/source-epc-recommendations/
python ./source_epc_recommendations/utils.py --help
python ./source_epc_recommendations/utils.py

## The Airbyte Custom Python Source code wraps and calls utils.py
## The four commands built in are as follows
## Reference: https://docs.airbyte.com/connector-development/tutorials/building-a-python-source/
cd ./airbyte/source-epc-recommendations/
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json

## Deploying this to AWS requires building this docker container
## This can be done locally to test. Deployment requires updating this code via git
## before running the following commands on the AWS EC2 instance.
## First build the container
docker build . -t airbyte/source-epc-recommendations:dev
## Then use the following commands to run it
docker run --rm airbyte/source-epc-recommendations:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-epc-recommendations:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-epc-recommendations:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-epc-recommendations:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
## This can be accessed from within the Airbyte UI by adding a new source from a Docker image
## The Airbyte UI has access to the EC2 local Docker Registry via the identifier `airbyte/source-epc-recommendations:dev`
