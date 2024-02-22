# Use the official Ubuntu 20.04 as a base image
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND noninteractive

# Update and install necessary packages
RUN apt-get update && \
    apt-get install -y \
        curl \
        python3 \
        python3-pip \
        vim \
        nano \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -s https://dl.openfoam.com/add-debian-repo.sh | bash

RUN apt-get install -y openfoam2312-default

# Set OpenFOAM environment variables
ENV WM_PROJECT_VERSION 7
ENV WM_PROJECT_DIR /usr/lib/openfoam/openfoam2312
ENV FOAM_APP $WM_PROJECT_DIR/applications
ENV FOAM_USER_APP $FOAM_USER_DIR/applications

# Set OpenFOAM bashrc
RUN echo "source $WM_PROJECT_DIR/etc/bashrc" >> /root/.bashrc

# Set Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8

# Set working directory
WORKDIR /skywalk_generator

# Install dependencies
RUN pip3 install tomli numpy
