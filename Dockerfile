FROM redhat/ubi8

RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    dnf install -y python3.8 && \
    dnf clean all


COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /opt/lue_bot/
COPY least_used_emoji_bot.py .

ENTRYPOINT ["python3", "least_used_emoji_bot.py"]
