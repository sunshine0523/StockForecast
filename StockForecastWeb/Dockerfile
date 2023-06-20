FROM node

COPY ./ /home/app/node

WORKDIR /home/app/node

EXPOSE 8080

RUN npm config set registry https://registry.npmmirror.com/
RUN npm install
CMD ["npm", "run", "dev"]