# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install vagrant-disksize to allow resizing the vagrant box disk.
unless Vagrant.has_plugin?("vagrant-disksize")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-disksize plugin is missing. Please install it using 'vagrant plugin install vagrant-disksize' and rerun 'vagrant up'"
end

# Install vagrant-vbguest to update guest additions on box launch
unless Vagrant.has_plugin?("vagrant-vbguest")
    raise  Vagrant::Errors::VagrantError.new, "vagrant-vbguest plugin is missing. Please install it using 'vagrant plugin install vagrant-vbguest' and rerun 'vagrant up'"
end


# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  #config.vm.box = "ubuntu/bionic64"
  config.vm.box = "ubuntu/focal64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Jupyter notebook (development)
  config.vm.network "forwarded_port", guest: 8888, host: 8888, host_ip: "127.0.0.1"

  # Flask (development)
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"

  # Nginx/UWSGI (production)
  config.vm.network "forwarded_port", guest: 80, host: 8000, host_ip: "127.0.0.1"

  # Redis (development)
  config.vm.network "forwarded_port", guest: 6379, host: 6379, host_ip: "127.0.0.1"

  # MySQL (development)
  config.vm.network "forwarded_port", guest: 3306, host: 3306, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.synced_folder ".", "/vagrant_data", type: "virtualbox"
  config.vm.synced_folder '.', '/vagrant', disabled: true

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
      # View the documentation for the provider you are using for more
      # information on available options.

      # Display the VirtualBox GUI when booting the machine
      #vb.gui = true

      # Configure virtual memory allocation
      vb.memory = 2048
      vb.cpus = 2

      # ubuntu/focal64 image currently suffering from a bug which makes it slow to boot.
      # Work-around described at https://askubuntu.com/questions/1243582 
      vb.customize [ "modifyvm", :id, "--uartmode1", "file", File::NULL ]
  end

  # Configure disk size using the plugin vagrant-disksize.
  # This is installed using vagrant plugin install vagrant-disksize
  #
#   config.disksize.size = '10GB'


  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.
  # config.vm.provision "shell", inline: <<-SHELL
  #   apt-get update
  #   apt-get install -y apache2
  # SHELL
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update

    BORDER="\n\n===================================================="

    echo -e $BORDER
    echo "Installing binutils..."

    apt-get -y install build-essential g++ python-dev autotools-dev libicu-dev libbz2-dev mlocate
    apt-get -y install libboost-serialization1.71.0 libgfortran5


    echo -e $BORDER
    echo "Installing miniconda..."

    # Provisioner runs as root. Sudo as `vagrant` user for conda install:
    /usr/bin/sudo -i -u vagrant bash <<"EOF"
        if [[ ! -d "$HOME/miniconda" ]];
        then
            # Install miniconda
            wget -nv https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
            bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda
            rm Miniconda3-latest-Linux-x86_64.sh

#            echo "Modifying PATH..."
#            sed -i 's;^PATH=\(.*\);PATH=\1\:\$HOME\/miniconda\/bin;' $HOME/.bash_profile
#            grep "PATH" -n .bash_profile
             echo "PATH=/home/vagrant/miniconda/bin/:$PATH" >> .profile
        else
            echo "Miniconda already installed! ^_^"
        fi
EOF


    echo -e $BORDER
    echo "Installing cppyy and development tools using conda..."

    /usr/bin/sudo -i -u vagrant bash <<"EOF"
        PATH="$PATH:$HOME/miniconda/bin"

        if conda list | grep -E 'cppyy|flask|markdown|jupyter|xeus' 2>&1>/dev/null; 
        then
            echo "cppyy and devtools already installed :)"
        else
            if [[ -d "$HOME/miniconda" ]];
            then
                conda init bash
                eval "$(conda shell.bash hook)"
                conda update -y -n base -c defaults conda

                # We originally configured a conda environment here, but leaving it as (base) solves problems!
                conda install -yc conda-forge cppyy
                conda install -y flask markdown

                # Development tools
                conda install -yc conda-forge jupyter
                jupyter notebook --generate-config
                sed -i 's/c.NotebookApp.ip.*/c.NotebookApp.ip = "0.0.0.0"/g' /home/vagrant/.jupyter/jupyter_notebook_config.py
                sed -i '/^#c.NotebookApp.ip /s/^#//' /home/vagrant/.jupyter/jupyter_notebook_config.py

                conda install xeus xeus-cling -c conda-forge
                conda install jupyterthemes -c conda-forge
                jt -t monokai
            else
                echo "Miniconda not installed!"
                exit 1
            fi
        fi
EOF


#     echo $BORDER
#     echo "Installing Docker"
#
#     if hash docker 2>/dev/null; then
#         echo "Docker already installed :)"
#     else
#         apt-get -y install apt-transport-https ca-certificates curl software-properties-common
#         curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
#         add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
#         apt-get update
#         apt-cache policy docker-ce
#
#         apt-get -y install docker-ce
#         systemctl status docker
#         usermod -aG docker vagrant
#
#         apt-get install -y docker-compose
#     fi

  SHELL
end
