FROM docker.io/maven:3-eclipse-temurin-8

# ARG REPO=https://github.com/opengeospatial/ets-ogcapi-tiles10.git
# ARG REPO_REF="tags/1.1"
# temporary, until PRs are approved/merged
ARG REPO=https://github.com/kad-korpem/ets-ogcapi-tiles10.git
ARG REPO_REF="allow-204-within-limits"

WORKDIR /src
RUN git clone ${REPO} . && git checkout ${REPO_REF}

# temporary, until PRs are approved/merged
RUN mvn spring-javaformat:apply

RUN mvn clean install
RUN mv /src/target/ets-ogcapi-tiles10-*-aio.jar /src/target/ets-ogcapi-tiles10-aio.jar

FROM docker.io/eclipse-temurin:21-jre
RUN apt update && apt install -y python3 \
    python3-pip

WORKDIR /src
COPY scripts /src

RUN python3 -m pip config set global.break-system-packages true
RUN python3 -m pip install -r requirements.txt
LABEL AUTHOR="pdok@kadaster.nl"
# set correct timezone
ENV TZ=Europe/Amsterdam

COPY --from=0 /src/target/ets-ogcapi-tiles10-aio.jar /opt/ets-ogcapi-tiles10-aio.jar
ENTRYPOINT ["bash", "/src/startup.sh"]
