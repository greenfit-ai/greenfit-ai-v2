FROM node:18-alpine

WORKDIR /ui/
COPY ./* /ui/

RUN npm install
RUN npm run build
RUN npm install -g serve

EXPOSE 80
ENTRYPOINT ["npm", "run", "serve"]