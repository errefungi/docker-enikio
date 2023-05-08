FROM node

WORKDIR /usuarios

COPY src ./src

RUN npm init --yes
RUN npm install express morgan mysql mysql2 axios cors

EXPOSE 3001

CMD node src/index.js
