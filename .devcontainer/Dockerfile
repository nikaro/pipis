FROM fedora:30

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash
# Update path to include virtualenv
ENV PATH "/usr/local/pyvenv/bin:${PATH}"
# Set locales
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN \
    echo "if [ -f /etc/bash_completion ]; then . /etc/bash_completion; fi" >> /root/.bashrc &&\
    echo "if [ -f /etc/profile.d/bash_completion.sh ]; then . /etc/profile.d/bash_completion.sh; fi" >> /root/.bashrc && \
    echo 'PS1="\[\e[32m\][\[\e[m\]\[\e[31m\]\u\[\e[m\]\[\e[33m\]@\[\e[m\]\[\e[32m\]\h\[\e[m\]:\[\e[36m\]\w\[\e[m\]\[\e[32m\]]\[\e[m\]\[\e[32m\]\\$\[\e[m\] "' >> /root/.bashrc

# Install git, required tools
RUN dnf install -y \
        bash-completion \
        curl \
        dnf-plugins-core \
        findutils \
        gcc \
        git \
        libffi-devel \
        make \
        openssl-devel \
        python3 \
        python3-devel \
        unzip \
        neovim \
    2>&1 && \
    # Install Docker CE CLI.
    dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo \
    dnf install -y docker-ce-cli 2>&1

# Install python requirements
RUN python3 -m venv /usr/local/pyvenv && \
    pip install -U pip wheel 2>&1
