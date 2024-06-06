FROM node:22-alpine3.19

WORKDIR /app

ENV TZ="Asia/Baghdad"

COPY package.json ./

# COPY package-lock.json ./

RUN npm install -g npm@10.6.0

RUN apk add python3 make gcc g++ 

RUN npm install

COPY . ./

CMD [ "node", "app.cjs" ]
