ARG CUDA_VERSION=12.1.1
ARG PYTHON_VERSION=3.10.12

FROM nvidia/cuda:${CUDA_VERSION}-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive TZ=America/Toronto

RUN apt-get -o Acquire::Max-FutureTime=86400 update && apt-get install -y \
    git vim curl \
    wget libgl1 libglib2.0-0 \
    openssh-server \
    python3-opencv \
    make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git git-lfs  \
    ffmpeg libsm6 libxext6 cmake libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# INSTALL OPENCV
RUN apt-get update
RUN apt-get install libopencv-dev python3-opencv -y

# PREPARE WORKING DIR AND SETUP PYTHON ENV
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

ARG PYTHON_VERSION=3.10.12

RUN curl https://pyenv.run | bash
ENV PATH=$HOME/.pyenv/shims:$HOME/.pyenv/bin:$PATH

RUN pyenv install $PYTHON_VERSION && \
    pyenv global $PYTHON_VERSION && \
    pyenv rehash && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    datasets

VOLUME ["/src"]
WORKDIR /src

RUN pip install --upgrade pip
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
RUN pip install pandas matplotlib tqdm scikit-learn scikit-image numpy scipy h5py tensorflow
RUN pip install opencv-contrib-python-headless
RUN pip install marimo

CMD [ "marimo", "edit", "--headless", "--token-password", "password", "--host", "0.0.0.0", "-p", "8080" ]
